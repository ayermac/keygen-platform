<template>
  <div>
    <el-button type="primary" @click="showCreate" style="margin-bottom: 16px">
      新增分类
    </el-button>

    <el-table :data="categories" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="code" label="标识码" />
      <el-table-column prop="score_per_key" label="Score 值" width="100" />
      <el-table-column prop="score_label" label="Score 标签" width="100" />
      <el-table-column label="API Key" min-width="200">
        <template #default="{ row }">
          <el-text truncated>{{ row.api_key }}</el-text>
          <el-button link type="primary" @click="copyApiKey(row.api_key)">复制</el-button>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="showEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button link type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="标识码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="Score 值" prop="score_per_key">
          <el-input-number v-model="form.score_per_key" :min="1" />
        </el-form-item>
        <el-form-item label="Score 标签" prop="score_label">
          <el-input v-model="form.score_label" />
        </el-form-item>
        <el-form-item label="有效期天数">
          <el-input-number v-model="form.expiry_days" :min="0" placeholder="留空为永久" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api/categories'

const categories = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const formRef = ref()

const form = reactive({
  name: '',
  code: '',
  score_per_key: 100,
  score_label: '积分',
  expiry_days: null as number | null,
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入标识码', trigger: 'blur' }],
  score_per_key: [{ required: true, message: '请输入 Score 值', trigger: 'blur' }],
}

async function loadCategories() {
  const res: any = await getCategories()
  categories.value = res.data.items
}

function showCreate() {
  isEdit.value = false
  Object.assign(form, { name: '', code: '', score_per_key: 100, score_label: '积分', expiry_days: null })
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, {
    name: row.name,
    code: row.code,
    score_per_key: row.score_per_key,
    score_label: row.score_label,
    expiry_days: row.expiry_days,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  if (isEdit.value) {
    await updateCategory(editId.value, form)
  } else {
    await createCategory(form)
  }
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  dialogVisible.value = false
  loadCategories()
}

async function handleDelete(id: number) {
  await deleteCategory(id)
  ElMessage.success('删除成功')
  loadCategories()
}

function copyApiKey(key: string) {
  navigator.clipboard.writeText(key)
  ElMessage.success('已复制')
}

onMounted(loadCategories)
</script>
