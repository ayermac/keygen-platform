<template>
  <div class="kg-page">
    <div class="kg-page-header">
      <h1 class="kg-page-title">批次管理</h1>
    </div>

    <!-- Search Bar -->
    <div class="kg-search-bar">
      <el-form :inline="true">
        <el-form-item label="产品">
          <el-select v-model="searchForm.product_id" clearable placeholder="全部产品" style="width: 160px">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="searchForm.batch_id" placeholder="搜索批次号" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadBatches">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table -->
    <div class="kg-table-wrapper">
      <el-table :data="batches" stripe>
        <el-table-column prop="batch_id" label="批次号" width="180">
          <template #default="{ row }">
            <code class="batch-id">{{ row.batch_id }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="产品" min-width="120" />
        <el-table-column prop="card_type_name" label="卡种" width="100">
          <template #default="{ row }">
            <span>{{ row.card_type_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="count" label="数量" width="80" align="center">
          <template #default="{ row }">
            <span class="score-num">{{ row.count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="单码额度" width="100" align="center">
          <template #default="{ row }">
            <span class="score-num">{{ row.total_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="创建人" width="100" />
        <el-table-column prop="remark" label="备注" min-width="140">
          <template #default="{ row }">
            <span class="text-muted">{{ row.remark || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            <span class="time-text">{{ formatDateTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="action-cell">
              <el-button type="primary" size="small" plain @click="openDetail(row.batch_id)">
                详情
              </el-button>
              <el-dropdown @command="(cmd: string) => handleExport(row.batch_id, cmd)" trigger="click">
                <el-button type="success" size="small" plain>
                  导出 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="">全部</el-dropdown-item>
                    <el-dropdown-item command="unused">未兑换</el-dropdown-item>
                    <el-dropdown-item command="activated">已兑换</el-dropdown-item>
                    <el-dropdown-item command="disabled">已禁用</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-popconfirm title="确定禁用该批次所有兑换码？此操作不可撤销。" @confirm="handleDisable(row.batch_id)">
                <template #reference>
                  <el-button type="danger" size="small" plain>禁用</el-button>
                </template>
              </el-popconfirm>
            </div>
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
          @current-change="loadBatches"
          @size-change="loadBatches"
        />
      </div>
    </div>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" :title="`批次详情 — ${detailBatch?.batch_id || ''}`" size="60%">
      <template v-if="detailBatch">
        <div class="detail-meta">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="产品">{{ detailBatch.product_name }}</el-descriptions-item>
            <el-descriptions-item label="卡种">{{ detailBatch.card_type_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="数量">{{ detailBatch.count }}</el-descriptions-item>
            <el-descriptions-item label="单码额度">{{ detailBatch.total_score }}</el-descriptions-item>
            <el-descriptions-item label="创建人">{{ detailBatch.creator || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(detailBatch.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ detailBatch.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <h3 class="detail-section-title">兑换码列表 ({{ detailBatch.codes.length }})</h3>
        <el-table :data="detailBatch.codes" stripe size="small" max-height="460">
          <el-table-column prop="code" label="兑换码" width="200">
            <template #default="{ row }">
              <code class="key-code">{{ row.code }}</code>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small" effect="plain">
                {{ statusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_score" label="初始额度" width="90" align="center" />
          <el-table-column prop="remaining_score" label="剩余额度" width="90" align="center">
            <template #default="{ row }">
              <span class="score-num remaining">{{ row.remaining_score }}</span>
            </template>
          </el-table-column>
          <el-table-column label="兑换时间" width="160">
            <template #default="{ row }">
              <span class="time-text">{{ formatDateTime(row.activated_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="过期时间" width="160">
            <template #default="{ row }">
              <span class="time-text">{{ formatDateTime(row.expires_at) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { searchBatches, getBatchDetail, disableBatch } from '../api/batches'
import { getProducts } from '../api/products'
import { formatDateTime, statusLabel, statusType } from '../utils/format'

const batches = ref<any[]>([])
const products = ref<any[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detailBatch = ref<any>(null)

const searchForm = reactive({
  product_id: null as number | null,
  batch_id: '',
  page: 1,
  page_size: 20,
})

async function loadProducts() {
  const res: any = await getProducts()
  products.value = res.data.items
}

async function loadBatches() {
  const res: any = await searchBatches(searchForm)
  batches.value = res.data.items
  total.value = res.data.total
}

async function openDetail(batchId: string) {
  const res: any = await getBatchDetail(batchId)
  detailBatch.value = res.data
  detailVisible.value = true
}

function handleExport(batchId: string, statusFilter: string) {
  const token = localStorage.getItem('token')
  let url = `/api/v1/admin/batches/${batchId}/export`
  if (statusFilter) {
    url += `?status=${statusFilter}`
  }
  fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((r) => r.blob())
    .then((blob) => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = statusFilter ? `batch_${batchId}_${statusFilter}.csv` : `batch_${batchId}.csv`
      a.click()
      URL.revokeObjectURL(a.href)
      ElMessage.success('导出成功')
    })
    .catch(() => ElMessage.error('导出失败'))
}

async function handleDisable(batchId: string) {
  await disableBatch(batchId)
  ElMessage.success('批次已禁用')
  loadBatches()
}

onMounted(() => {
  loadProducts()
  loadBatches()
})
</script>

<style scoped>
.batch-id {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: var(--kg-text);
  background: var(--kg-bg);
  padding: 3px 8px;
  border-radius: 4px;
}

.key-code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: var(--kg-text);
  background: var(--kg-bg);
  padding: 3px 8px;
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

.action-cell {
  display: flex;
  gap: 6px;
  align-items: center;
}

.detail-meta {
  margin-bottom: 20px;
}

.detail-section-title {
  font-size: 15px;
  font-weight: 600;
  margin: 16px 0 10px;
  color: var(--kg-text);
}
</style>
