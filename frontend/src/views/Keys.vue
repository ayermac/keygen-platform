<template>
  <div>
    <el-form :inline="true" style="margin-bottom: 16px">
      <el-form-item label="分类">
        <el-select v-model="searchForm.category_id" clearable placeholder="全部" style="width: 160px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" clearable placeholder="全部" style="width: 120px">
          <el-option label="未使用" value="unused" />
          <el-option label="已激活" value="activated" />
          <el-option label="已过期" value="expired" />
          <el-option label="已禁用" value="disabled" />
        </el-select>
      </el-form-item>
      <el-form-item label="Key Code">
        <el-input v-model="searchForm.key_code" placeholder="搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadKeys">搜索</el-button>
        <el-button type="success" @click="showGenerate">批量生成</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="keys" border stripe>
      <el-table-column prop="key_code" label="Key Code" width="200" />
      <el-table-column prop="category_name" label="分类" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_score" label="初始 Score" width="100" />
      <el-table-column prop="remaining_score" label="剩余 Score" width="100" />
      <el-table-column prop="batch_id" label="批次" width="150" />
      <el-table-column label="激活时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.activated_at) }}</template>
      </el-table-column>
      <el-table-column label="过期时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.expires_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-popconfirm title="确定禁用？" @confirm="handleDisable(row.id)">
            <template #reference>
              <el-button link type="danger" :disabled="row.status !== 'unused'">禁用</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 16px; justify-content: flex-end"
      v-model:current-page="searchForm.page"
      v-model:page-size="searchForm.page_size"
      :total="total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @current-change="loadKeys"
      @size-change="loadKeys"
    />

    <el-dialog v-model="generateDialogVisible" title="批量生成激活码" width="400px">
      <el-form :model="generateForm" label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="generateForm.category_id" style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="generateForm.count" :min="1" :max="10000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="generateForm.batch_id" placeholder="留空自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerate">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { searchKeys, generateKeys, disableKey } from '../api/keys'
import { getCategories } from '../api/categories'
import { formatDateTime, statusLabel, statusType } from '../utils/format'

const keys = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)
const generateDialogVisible = ref(false)

const searchForm = reactive({
  category_id: null as number | null,
  status: null as string | null,
  key_code: '',
  page: 1,
  page_size: 20,
})

const generateForm = reactive({
  category_id: null as number | null,
  count: 100,
  batch_id: '',
})

async function loadCategories() {
  const res: any = await getCategories()
  categories.value = res.data.items
}

async function loadKeys() {
  const res: any = await searchKeys(searchForm)
  keys.value = res.data.items
  total.value = res.data.total
}

function showGenerate() {
  generateForm.category_id = null
  generateForm.count = 100
  generateForm.batch_id = ''
  generateDialogVisible.value = true
}

async function handleGenerate() {
  if (!generateForm.category_id) {
    ElMessage.warning('请选择分类')
    return
  }
  const res: any = await generateKeys(generateForm)
  ElMessage.success(`成功生成 ${res.data.count} 个激活码`)
  generateDialogVisible.value = false
  loadKeys()
}

async function handleDisable(id: number) {
  await disableKey(id)
  ElMessage.success('已禁用')
  loadKeys()
}

onMounted(() => {
  loadCategories()
  loadKeys()
})
</script>
