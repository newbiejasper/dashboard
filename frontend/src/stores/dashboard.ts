import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardAPI } from '@/api/endpoints'
import type { Dashboard, DashboardView, DashboardFilter, Chart } from '@/types'

export const useDashboardStore = defineStore('dashboard', () => {
  const currentDashboard = ref<Dashboard | null>(null)
  const views = ref<DashboardView[]>([])
  const filters = ref<DashboardFilter[]>([])
  const isLoading = ref(false)

  async function loadDashboard(id: number) {
    isLoading.value = true
    try {
      const [dashRes, viewsRes] = await Promise.all([
        dashboardAPI.get(id),
        dashboardAPI.views(id),
      ])
      currentDashboard.value = dashRes.data
      views.value = viewsRes.data
    } finally {
      isLoading.value = false
    }
  }

  function addView(view: DashboardView) {
    views.value.push(view)
  }

  function updateView(viewId: number, data: Partial<DashboardView>) {
    const idx = views.value.findIndex((v) => v.id === viewId)
    if (idx !== -1) {
      views.value[idx] = { ...views.value[idx], ...data }
    }
  }

  function removeView(viewId: number) {
    views.value = views.value.filter((v) => v.id !== viewId)
  }

  async function saveDashboard(data: Partial<Dashboard>) {
    if (!currentDashboard.value) return
    const res = await dashboardAPI.update(currentDashboard.value.id, data)
    currentDashboard.value = res.data
  }

  return {
    currentDashboard, views, filters, isLoading,
    loadDashboard, addView, updateView, removeView, saveDashboard,
  }
})
