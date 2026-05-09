<template>
  <div class="kg-page">
    <div class="kg-page-header">
      <h1 class="kg-page-title">兑换码管理</h1>
      <el-button type="primary" @click="showGenerate">
        <el-icon><Plus /></el-icon>
        批量生成
      </el-button>
    </div>

    <!-- Search Bar -->
    <div class="kg-search-bar">
      <el-form :inline="true">
        <el-form-item label="产品">
          <el-select v-model="searchForm.product_id" clearable placeholder="全部产品" style="width: 160px">
            <el-option v-for="c in products" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable placeholder="全部状态" style="width: 130px">
            <el-option label="未兑换" value="unused" />
            <el-option label="已兑换" value="activated" />
            <el-option label="已过期" value="expired" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="兑换码">
          <el-input v-model="searchForm.code" placeholder="搜索兑换码" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadCodes">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table -->
    <div class="kg-table-wrapper">
      <el-table :data="codes" stripe>
        <el-table-column prop="code" label="兑换码" width="200">
          <template #default="{ row }">
            <code class="key-code">{{ row.code }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="产品" width="120" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_credits" label="初始额度" width="100" align="center">
          <template #default="{ row }">
            <span class="score-num">{{ row.total_credits }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remaining_credits" label="剩余额度" width="100" align="center">
          <template #default="{ row }">
            <span class="score-num remaining">{{ row.remaining_credits }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="batch_id" label="批次" width="140">
          <template #default="{ row }">
            <code class="batch-tag" v-if="row.batch_id">{{ row.batch_id }}</code>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="兑换时间" width="170">
          <template #default="{ row }">
            <span class="time-text">{{ formatDateTime(row.activated_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="过期时间" width="170">
          <template #default="{ row }">
            <span class="time-text">{{ formatDateTime(row.expires_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定禁用该兑换码？" @confirm="handleDisable(row.id)">
              <template #reference>
                <el-button type="danger" :icon="CloseBold" circle size="small" :disabled="row.status !== 'unused'" />
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="kg-pagination">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="searchForm.page_size"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadCodes"
          @size-change="loadCodes"
        />
      </div>
    </div>

    <!-- Generate Dialog -->
    <el-dialog v-model="generateDialogVisible" title="批量生成兑换码" width="460px">
      <el-form :model="generateForm" label-width="80px">
        <el-form-item label="产品">
          <el-select v-model="generateForm.product_id" placeholder="选择产品" style="width: 100%">
            <el-option v-for="c in products" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="generateForm.count" :min="1" :max="10000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="卡种" v-if="selectedProductCardTypes.length">
          <el-select v-model="generateForm.card_type" clearable placeholder="默认（使用产品配置）" style="width: 100%">
            <el-option v-for="ct in selectedProductCardTypes" :key="ct.name" :label="`${ct.name} — ${ct.total_score} 额度${ct.expiry_days ? ', ' + ct.expiry_days + '天' : ', 永久'}`" :value="ct.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="generateForm.batch_id" placeholder="留空自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerate">
          <el-icon><Plus /></el-icon>
          生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CloseBold } from '@element-plus/icons-vue'
import { searchCodes, generateCodes, disableCode } from '../api/codes'
import { getProducts } from '../api/products'
import { formatDateTime, statusLabel, statusType } from '../utils/format'

const codes = ref<any[]>([])
const products = ref<any[]>([])
const total = ref(0)
const generateDialogVisible = ref(false)

const searchForm = reactive({
  product_id: null as number | null,
  status: null as string | null,
  code: '',
  page: 1,
  page_size: 20,
})

const generateForm = reactive({
  product_id: null as number | null,
  count: 100,
  batch_id: '',
  card_type: '',
})

const selectedProductCardTypes = computed(() => {
  if (!generateForm.product_id) return []
  const prod = products.value.find((c: any) => c.id === generateForm.product_id)
  return prod?.card_types || []
})

async function loadProducts() {
  const res: any = await getProducts()
  products.value = res.data.items
}

async function loadCodes() {
  const res: any = await searchCodes(searchForm)
  codes.value = res.data.items
  total.value = res.data.total
}

function showGenerate() {
  generateForm.product_id = null
  generateForm.count = 100
  generateForm.batch_id = ''
  generateForm.card_type = ''
  generateDialogVisible.value = true
}

async function handleGenerate() {
  if (!generateForm.product_id) {
    ElMessage.warning('请选择产品')
    return
  }
  const res: any = await generateCodes(generateForm)
  ElMessage.success(`成功生成 ${res.data.count} 个兑换码`)
  generateDialogVisible.value = false
  loadCodes()
}

async function handleDisable(id: number) {
  await disableCode(id)
  ElMessage.success('已禁用')
  loadCodes()
}

onMounted(() => {
  loadProducts()
  loadCodes()
})
</script>

<style scoped>
.key-code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: var(--kg-text);
  background: var(--kg-bg);
  padding: 3px 8px;
  border-radius: 4px;
}

.batch-tag {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: var(--kg-text-secondary);
  background: var(--kg-bg);
  padding: 2px 6px;
  border-radius: 4px;
}

.score-num {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--kg-text);
}

.score-num.remaining {
  color: var(--kg-primary);
}

.time-text {
  font-size: 13px;
  color: var(--kg-text-secondary);
}

.text-muted {
  color: var(--kg-text-muted);
}
</style>
