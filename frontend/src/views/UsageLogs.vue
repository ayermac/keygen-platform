<template>
  <div>
    <el-form :inline="true" style="margin-bottom: 16px">
      <el-form-item label="Key Code">
        <el-input v-model="searchForm.key_code" placeholder="搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="searchForm.category_id" clearable placeholder="全部" style="width: 160px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="操作类型">
        <el-select v-model="searchForm.action" clearable placeholder="全部" style="width: 120px">
          <el-option label="激活" value="activate" />
          <el-option label="扣减" value="deduct" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadLogs">搜索</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="logs" border stripe>
      <el-table-column prop="key_code" label="Key Code" width="200" />
      <el-table-column prop="category_name" label="分类" width="120" />
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-tag :type="row.action === 'activate' ? 'success' : 'warning'">
            {{ row.action === 'activate' ? '激活' : '扣减' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="Score 数量" width="100" />
      <el-table-column prop="remaining_after" label="操作后剩余" width="100" />
      <el-table-column label="上报数据" min-width="200">
        <template #default="{ row }">
          <el-popover v-if="row.metadata && Object.keys(row.metadata).length" trigger="hover" width="300">
            <template #reference>
              <el-button link type="primary">查看</el-button>
            </template>
            <div v-for="(v, k) in row.metadata" :key="k" style="margin-bottom: 4px">
              <strong>{{ k }}:</strong> {{ v }}
            </div>
          </el-popover>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="client_ip" label="IP" width="140" />
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 16px; justify-content: flex-end"
      v-model:current-page="searchForm.page"
      v-model:page-size="searchForm.page_size"
      :total="total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @current-change="loadLogs"
      @size-change="loadLogs"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { searchUsageLogs } from '../api/usageLogs'
import { getCategories } from '../api/categories'
import { formatDateTime } from '../utils/format'

const logs = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)

const searchForm = reactive({
  key_code: '',
  category_id: null as number | null,
  action: null as string | null,
  page: 1,
  page_size: 20,
})

async function loadCategories() {
  const res: any = await getCategories()
  categories.value = res.data.items
}

async function loadLogs() {
  const res: any = await searchUsageLogs(searchForm)
  logs.value = res.data.items
  total.value = res.data.total
}

onMounted(() => {
  loadCategories()
  loadLogs()
})
</script>
