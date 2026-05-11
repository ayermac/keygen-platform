<template>
  <div class="login-page">
    <!-- Animated Background -->
    <div class="login-bg">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1"></div>
      <div class="bg-glow bg-glow-2"></div>
    </div>

    <!-- Login Card -->
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <div class="logo-icon">K</div>
        </div>
        <h1 class="login-title">Keygen</h1>
        <p class="login-subtitle">兑换码管理系统</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>Universal Activation Code Platform</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import request from '../api/request'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res: any = await request.post('/admin/login', form)
    authStore.setToken(res.data.token)
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* ---- Background ---- */
.login-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #312e81 100%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(99, 102, 241, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.06) 1px, transparent 1px);
  background-size: 60px 60px;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
}

.bg-glow-1 {
  width: 500px;
  height: 500px;
  background: #6366f1;
  top: -10%;
  right: -5%;
  animation: float1 8s ease-in-out infinite;
}

.bg-glow-2 {
  width: 400px;
  height: 400px;
  background: #8b5cf6;
  bottom: -10%;
  left: -5%;
  animation: float2 10s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-30px, 30px); }
}

@keyframes float2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

/* ---- Card ---- */
.login-card {
  position: relative;
  z-index: 1;
  width: 420px;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 20px;
  padding: 48px 40px 36px;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  animation: scaleIn 0.5s ease;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* ---- Header ---- */
.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.login-logo .logo-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 800;
  font-size: 26px;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.login-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 6px;
}

.login-subtitle {
  font-size: 14px;
  color: #64748b;
}

/* ---- Form ---- */
.login-form :deep(.el-input__wrapper) {
  border-radius: 10px !important;
  padding: 4px 12px !important;
  box-shadow: 0 0 0 1px #e2e8f0 !important;
  background: #f8fafc !important;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #a5b4fc !important;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3) !important;
  background: #fff !important;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 22px;
}

.login-btn {
  width: 100%;
  height: 46px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4) !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0.05em;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
}

.login-btn:active {
  transform: translateY(0);
}

/* ---- Footer ---- */
.login-footer {
  text-align: center;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;
}

.login-footer span {
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
</style>
