import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/docs/api',
      name: 'ApiDocs',
      component: () => import('../views/ApiDocs.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('../views/Layout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue'),
          meta: { title: '数据看板' },
        },
        {
          path: 'products',
          name: 'Products',
          component: () => import('../views/Products.vue'),
          meta: { title: '产品管理' },
        },
        {
          path: 'codes',
          name: 'Codes',
          component: () => import('../views/Codes.vue'),
          meta: { title: '兑换码管理' },
        },
        {
          path: 'usage-logs',
          name: 'UsageLogs',
          component: () => import('../views/UsageLogs.vue'),
          meta: { title: '使用日志' },
        },
        {
          path: 'audit-logs',
          name: 'AuditLogs',
          component: () => import('../views/AuditLogs.vue'),
          meta: { title: '审计日志' },
        },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if ((to.path !== '/login' && !to.meta.public) && !authStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
