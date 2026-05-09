<template>
  <div>
    <el-table :data="logs" border stripe>
      <el-table-column prop="admin_username" label="操作人" width="120" />
      <el-table-column prop="action" label="操作" width="160" />
      <el-table-column prop="target_type" label="目标类型" width="120" />
      <el-table-column prop="target_id" label="目标 ID" width="100" />
      <el-table-column label="详情" min-width="200">
        <template #default="{ row }">
          <el-text truncated>{{ row.detail ? JSON.stringify(row.detail) : '-' }}</el-text>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 16px; justify-content: flex-end"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @current-change="loadLogs"
      @size-change="loadLogs"
    />
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
