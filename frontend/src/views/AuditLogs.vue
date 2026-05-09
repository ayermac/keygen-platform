<template>
  <div class="kg-page">
    <div class="kg-page-header">
      <h1 class="kg-page-title">审计日志</h1>
    </div>

    <div class="kg-table-wrapper">
      <el-table :data="logs" stripe>
        <el-table-column prop="admin_username" label="操作人" width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-dot">{{ (row.admin_username || 'A')[0].toUpperCase() }}</div>
              <span>{{ row.admin_username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" width="160">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" type="info">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="目标类型" width="120">
          <template #default="{ row }">
            <code class="target-tag">{{ row.target_type }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="target_id" label="目标 ID" width="100">
          <template #default="{ row }">
            <span class="id-text">#{{ row.target_id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="详情" min-width="200">
          <template #default="{ row }">
            <el-text v-if="row.detail" truncated class="detail-text">
              {{ JSON.stringify(row.detail) }}
            </el-text>
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
          v-model:current-page="page"
          v-model:page-size="pageSize"
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
import { ref, onMounted } from 'vue'
import { getAuditLogs } from '../api/auditLogs'
import { formatDateTime } from '../utils/format'

const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

async function loadLogs() {
  const res: any = await getAuditLogs({ page: page.value, page_size: pageSize.value })
  logs.value = res.data.items
  total.value = res.data.total
}

onMounted(loadLogs)
</script>

<style scoped>
.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-dot {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}

.target-tag {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  background: var(--kg-bg);
  color: var(--kg-text-secondary);
  padding: 2px 6px;
  border-radius: 4px;
}

.id-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: var(--kg-text-muted);
}

.detail-text {
  font-size: 13px;
  color: var(--kg-text-secondary);
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.time-text {
  font-size: 13px;
  color: var(--kg-text-secondary);
}

.text-muted {
  color: var(--kg-text-muted);
}
</style>
