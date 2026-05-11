<template>
  <div class="kg-page">
    <div class="kg-page-header">
      <h1 class="kg-page-title">使用日志</h1>
    </div>

    <!-- Search Bar -->
    <div class="kg-search-bar">
      <el-form :inline="true">
        <el-form-item label="兑换码">
          <el-input v-model="searchForm.code" placeholder="搜索兑换码" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="产品">
          <el-select v-model="searchForm.product_id" clearable placeholder="全部产品" style="width: 160px">
            <el-option v-for="c in products" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.action" clearable placeholder="全部类型" style="width: 130px">
            <el-option label="兑换" value="activate" />
            <el-option label="消耗" value="deduct" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLogs">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table -->
    <div class="kg-table-wrapper">
      <el-table :data="logs" stripe>
        <el-table-column prop="code" label="兑换码" width="200">
          <template #default="{ row }">
            <code class="key-code">{{ row.code }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="产品" width="120" />
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.action === 'activate' ? 'success' : 'warning'"
              size="small"
              effect="plain"
            >
              {{ row.action === 'activate' ? '兑换' : '消耗' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="额度数量" width="100" align="center">
          <template #default="{ row }">
            <span class="amount-num">{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remaining_after" label="操作后剩余" width="100" align="center">
          <template #default="{ row }">
            <span class="remaining-num">{{ row.remaining_after }}</span>
          </template>
        </el-table-column>
        <el-table-column label="上报数据" min-width="200">
          <template #default="{ row }">
            <el-popover v-if="row.metadata && Object.keys(row.metadata).length" trigger="hover" width="300">
              <template #reference>
                <el-button link type="primary" size="small">
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
              </template>
              <div class="metadata-list">
                <div v-for="(v, k) in row.metadata" :key="k" class="metadata-item">
                  <span class="metadata-key">{{ k }}</span>
                  <span class="metadata-value">{{ v }}</span>
                </div>
              </div>
            </el-popover>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="client_ip" label="IP" width="140">
          <template #default="{ row }">
            <code class="ip-text">{{ row.client_ip }}</code>
          </template>
        </el-table-column>
        <el-table-column label="请求ID" width="160">
          <template #default="{ row }">
            <el-tooltip v-if="row.request_id" :content="row.request_id" placement="top">
              <code class="request-id-text">{{ row.request_id.length > 16 ? row.request_id.slice(0, 16) + '...' : row.request_id }}</code>
            </el-tooltip>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="170">
          <template #default="{ row }">
            <span class="time-text">{{ formatDateTime(row.created_at) }}</span>
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
          @current-change="loadLogs"
          @size-change="loadLogs"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { searchUsageLogs } from '../api/usageLogs'
import { getProducts } from '../api/products'
import { formatDateTime } from '../utils/format'

const logs = ref<any[]>([])
const products = ref<any[]>([])
const total = ref(0)

const searchForm = reactive({
  code: '',
  product_id: null as number | null,
  action: null as string | null,
  page: 1,
  page_size: 20,
})

async function loadProducts() {
  const res: any = await getProducts()
  products.value = res.data.items
}

async function loadLogs() {
  const res: any = await searchUsageLogs(searchForm)
  logs.value = res.data.items
  total.value = res.data.total
}

onMounted(() => {
  loadProducts()
  loadLogs()
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

.amount-num {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--kg-warning);
}

.remaining-num {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--kg-primary);
}

.ip-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: var(--kg-text-secondary);
}

.request-id-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: var(--kg-text-secondary);
  cursor: default;
}

.time-text {
  font-size: 13px;
  color: var(--kg-text-secondary);
}

.text-muted {
  color: var(--kg-text-muted);
}

.metadata-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metadata-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 6px 0;
  border-bottom: 1px solid var(--kg-border);
}

.metadata-item:last-child {
  border-bottom: none;
}

.metadata-key {
  font-weight: 600;
  font-size: 13px;
  color: var(--kg-text);
}

.metadata-value {
  font-size: 13px;
  color: var(--kg-text-secondary);
  text-align: right;
  word-break: break-all;
}
</style>
