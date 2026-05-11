<template>
  <div class="kg-page">
    <div class="kg-page-header">
      <h1 class="kg-page-title">产品管理</h1>
      <el-button type="primary" @click="showCreate">
        <el-icon><Plus /></el-icon>
        新增产品
      </el-button>
    </div>

    <div class="kg-table-wrapper">
      <el-table :data="products" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="code" label="标识码" min-width="100">
          <template #default="{ row }">
            <code class="code-tag">{{ row.code }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="default_credits" label="默认额度" width="100" align="center">
          <template #default="{ row }">
            <span class="score-badge">{{ row.default_credits }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="credit_unit" label="额度单位" width="100" />
        <el-table-column label="接入密钥" min-width="260">
          <template #default="{ row }">
            <div class="api-key-cell">
              <code class="api-key-text">{{ row.api_key }}</code>
              <el-button type="primary" size="small" plain @click="copyApiKey(row.api_key)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            <span class="time-text">{{ row.created_at }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <div class="action-cell">
              <el-button type="primary" :icon="Edit" circle size="small" @click="showEdit(row)" />
              <el-popconfirm title="轮换后旧密钥立即失效，确定继续？" @confirm="handleRotate(row.id)">
                <template #reference>
                  <el-button type="warning" :icon="RefreshRight" circle size="small" />
                </template>
              </el-popconfirm>
              <el-popconfirm title="确定删除该产品？" @confirm="handleDelete(row.id)">
                <template #reference>
                  <el-button type="danger" :icon="Delete" circle size="small" />
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑产品' : '新增产品'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="标识码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" placeholder="唯一标识符" />
        </el-form-item>
        <el-form-item label="默认额度" prop="default_credits">
          <el-input-number v-model="form.default_credits" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="额度单位" prop="credit_unit">
          <el-input v-model="form.credit_unit" placeholder="如：积分、次数" />
        </el-form-item>
        <el-form-item label="有效期天数">
          <el-input-number v-model="form.expiry_days" :min="0" placeholder="留空为永久" style="width: 100%" />
        </el-form-item>

        <!-- Card Types -->
        <el-divider content-position="left">卡种模板（可选）</el-divider>
        <div class="card-types-section">
          <div v-for="(ct, idx) in form.card_types" :key="idx" class="card-type-row">
            <el-input v-model="ct.name" placeholder="卡种名称" style="width: 120px" />
            <el-input-number v-model="ct.total_score" :min="1" placeholder="额度" style="width: 120px" />
            <el-input-number v-model="ct.expiry_days" :min="0" placeholder="天数" style="width: 120px" />
            <el-button link type="danger" @click="form.card_types.splice(idx, 1)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="form.card_types.push({ name: '', total_score: 100, expiry_days: null })">
            <el-icon><Plus /></el-icon>
            添加卡种
          </el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ isEdit ? '更新' : '创建' }}</el-button>
      </template>
    </el-dialog>

    <!-- Rotate Key Result Dialog -->
    <el-dialog v-model="rotateDialogVisible" title="密钥已轮换" width="480px">
      <div class="rotate-result">
        <p>新密钥如下，请立即复制保存，关闭后无法再次查看：</p>
        <div class="new-key-display">
          <code>{{ newApiKey }}</code>
          <el-button type="primary" size="small" plain @click="copyApiKey(newApiKey)">
            <el-icon><CopyDocument /></el-icon>
            复制
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Delete, RefreshRight } from '@element-plus/icons-vue'
import { getProducts, createProduct, updateProduct, deleteProduct, rotateProductKey } from '../api/products'

const products = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const formRef = ref()
const rotateDialogVisible = ref(false)
const newApiKey = ref('')

const form = reactive({
  name: '',
  code: '',
  default_credits: 100,
  credit_unit: '积分',
  expiry_days: null as number | null,
  card_types: [] as Array<{ name: string; total_score: number; expiry_days: number | null }>,
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入标识码', trigger: 'blur' }],
  default_credits: [{ required: true, message: '请输入默认额度', trigger: 'blur' }],
}

async function loadProducts() {
  const res: any = await getProducts()
  products.value = res.data.items
}

function showCreate() {
  isEdit.value = false
  Object.assign(form, { name: '', code: '', default_credits: 100, credit_unit: '积分', expiry_days: null, card_types: [] })
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, {
    name: row.name,
    code: row.code,
    default_credits: row.default_credits,
    credit_unit: row.credit_unit,
    expiry_days: row.expiry_days,
    card_types: row.card_types ? row.card_types.map((ct: any) => ({ ...ct })) : [],
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  if (isEdit.value) {
    await updateProduct(editId.value, form)
  } else {
    await createProduct(form)
  }
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  dialogVisible.value = false
  loadProducts()
}

async function handleDelete(id: number) {
  await deleteProduct(id)
  ElMessage.success('删除成功')
  loadProducts()
}

async function handleRotate(id: number) {
  const res: any = await rotateProductKey(id)
  newApiKey.value = res.data.api_key
  rotateDialogVisible.value = true
  loadProducts()
}

function copyApiKey(key: string) {
  navigator.clipboard.writeText(key)
  ElMessage.success('已复制到剪贴板')
}

onMounted(loadProducts)
</script>

<style scoped>
.code-tag {
  font-family: 'SF Mono', 'Fira Code', monospace;
  background: var(--kg-primary-bg);
  color: var(--kg-primary);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.score-badge {
  display: inline-block;
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
  color: var(--kg-primary);
  padding: 2px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
}

.api-key-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.api-key-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: var(--kg-text-secondary);
  background: var(--kg-bg);
  padding: 4px 8px;
  border-radius: 4px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-text {
  font-size: 13px;
  color: var(--kg-text-secondary);
}

.action-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-types-section {
  padding: 0 0 8px;
}

.card-type-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rotate-result p {
  margin-bottom: 12px;
  color: var(--kg-text-secondary);
  font-size: 14px;
}

.new-key-display {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--kg-bg);
  padding: 12px;
  border-radius: 6px;
  border: 1px solid var(--kg-border);
}

.new-key-display code {
  flex: 1;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  word-break: break-all;
}
</style>
