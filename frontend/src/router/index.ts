import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Auth/LoginPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/workbench',
    children: [
      {
        path: 'workbench',
        name: 'Workbench',
        component: () => import('@/views/Workbench/WorkbenchPage.vue'),
        meta: { title: '工作台' },
      },
      {
        path: 'dashboard',
        name: 'DashboardList',
        component: () => import('@/views/Dashboard/DashboardListPage.vue'),
        meta: { title: '仪表板' },
      },
      {
        path: 'dashboard/:id/edit',
        name: 'DashboardEdit',
        component: () => import('@/views/Dashboard/DashboardEditor.vue'),
        meta: { title: '编辑仪表板' },
      },
      {
        path: 'dashboard/:id/view',
        name: 'DashboardView',
        component: () => import('@/views/Dashboard/DashboardViewer.vue'),
        meta: { title: '查看仪表板' },
      },
      {
        path: 'data',
        name: 'DataManagement',
        component: () => import('@/views/Data/DataManagementPage.vue'),
        meta: { title: '数据准备' },
      },
      {
        path: 'market',
        name: 'TemplateMarket',
        component: () => import('@/views/Market/TemplateMarket.vue'),
        meta: { title: '模板市场' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('ddyl_token')
  if (to.name !== 'Login' && !token) {
    next('/login')
  } else if (to.name === 'Login' && token) {
    next('/workbench')
  } else {
    next()
  }
})

export default router
