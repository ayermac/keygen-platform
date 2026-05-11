<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="layout-aside">
      <!-- Logo -->
      <div class="aside-logo">
        <div class="logo-icon">K</div>
        <transition name="fade">
          <span v-if="!isCollapsed" class="logo-text">Keygen</span>
        </transition>
      </div>

      <!-- Navigation -->
      <el-menu
        :default-active="route.path"
        :collapse="isCollapsed"
        class="aside-menu"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon class="menu-icon"><DataAnalysis /></el-icon>
          <template #title>数据看板</template>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon class="menu-icon"><Box /></el-icon>
          <template #title>产品管理</template>
        </el-menu-item>
        <el-menu-item index="/codes">
          <el-icon class="menu-icon"><Key /></el-icon>
          <template #title>兑换码管理</template>
        </el-menu-item>
        <el-menu-item index="/batches">
          <el-icon class="menu-icon"><Files /></el-icon>
          <template #title>批次管理</template>
        </el-menu-item>
        <el-menu-item index="/usage-logs">
          <el-icon class="menu-icon"><Document /></el-icon>
          <template #title>使用日志</template>
        </el-menu-item>
        <el-menu-item index="/audit-logs">
          <el-icon class="menu-icon"><Notebook /></el-icon>
          <template #title>审计日志</template>
        </el-menu-item>
      </el-menu>

      <!-- Collapse Toggle -->
      <div class="aside-footer" @click="isCollapsed = !isCollapsed">
        <el-icon :size="18">
          <Fold v-if="!isCollapsed" />
          <Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <el-container class="layout-main">
      <!-- Header -->
      <el-header class="layout-header">
        <div class="header-left">
          <h2 class="header-title">{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleLogout" trigger="click">
            <div class="user-avatar-wrap">
              <div class="user-avatar">A</div>
              <span class="user-name">管理员</span>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Content -->
      <el-main class="layout-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapsed = ref(false)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': '数据看板',
    '/products': '产品管理',
    '/codes': '兑换码管理',
    '/batches': '批次管理',
    '/usage-logs': '使用日志',
    '/audit-logs': '审计日志',
  }
  return titles[route.path] || 'Keygen Platform'
})

function handleLogout(command: string) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

/* ---- Sidebar ---- */
.layout-aside {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  position: relative;
  z-index: 10;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
}

.aside-logo {
  display: flex;
  align-items: center;
  padding: 24px 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 800;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.025em;
  white-space: nowrap;
}

/* ---- Menu ---- */
.layout-aside :deep(.el-menu) {
  background: transparent !important;
  border: none !important;
  padding: 12px 8px;
  flex: 1;
}

.layout-aside :deep(.el-menu-item) {
  color: #94a3b8 !important;
  border-radius: 8px !important;
  margin-bottom: 4px !important;
  height: 44px !important;
  line-height: 44px !important;
  transition: all 0.2s ease !important;
}

.layout-aside :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.06) !important;
  color: #e2e8f0 !important;
}

.layout-aside :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
  color: #a5b4fc !important;
  font-weight: 600 !important;
}

.layout-aside :deep(.el-menu-item .el-icon) {
  font-size: 18px !important;
  margin-right: 12px !important;
}

.layout-aside :deep(.el-menu--collapse .el-menu-item .el-icon) {
  margin-right: 0 !important;
}

.menu-icon {
  font-size: 18px;
}


/* ---- Aside Footer ---- */
.aside-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.aside-footer:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.04);
}

/* ---- Header ---- */
.layout-header {
  background: var(--kg-surface);
  border-bottom: 1px solid var(--kg-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  box-shadow: var(--kg-shadow-sm);
  position: sticky;
  top: 0;
  z-index: 5;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--kg-text);
  letter-spacing: -0.025em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--kg-radius);
  transition: all 0.2s ease;
}

.user-avatar-wrap:hover {
  background: var(--kg-bg);
}

.user-avatar {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--kg-text);
}

.user-arrow {
  color: var(--kg-text-muted);
  font-size: 12px;
}

/* ---- Content ---- */
.layout-content {
  background: var(--kg-bg);
  padding: 24px 32px;
  min-height: calc(100vh - 64px);
  overflow-y: auto;
}

/* ---- Transitions ---- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
