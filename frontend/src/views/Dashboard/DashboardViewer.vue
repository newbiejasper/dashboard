<template>
  <div class="dashboard-viewer" :style="viewerStyle">
    <div class="viewer-toolbar">
      <el-button text @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <span class="viewer-title">{{ dashboardStore.currentDashboard?.name }}</span>
      <div class="viewer-actions">
        <el-button @click="exportImage">
          <el-icon><Picture /></el-icon> 导出图片
        </el-button>
        <el-button @click="exportPDF">
          <el-icon><Document /></el-icon> 导出PDF
        </el-button>
      </div>
    </div>
    <div class="viewer-content" ref="viewerRef">
      <!-- Filter Bar -->
      <div class="filter-bar" v-if="dashboardStore.filters.length > 0">
        <component
          v-for="(f, i) in dashboardStore.filters"
          :key="i"
          :is="getFilterComp(f.filter_type)"
          v-bind="getFilterProps(f)"
        />
      </div>

      <!-- Views Grid -->
      <div class="views-grid" :style="{ width: dashWidth + 'px' }">
        <div
          v-for="view in dashboardStore.views"
          :key="view.id"
          class="view-card"
          :style="getViewCardStyle(view)"
        >
          <div class="view-card-header">
            <span>{{ view.title || view.chart?.name || '图表' }}</span>
          </div>
          <div class="view-card-body">
            <ChartEngine
              v-if="view.chart"
              :chart="view.chart"
              :data="chartData[view.chart_id || 0] || []"
              width="100%"
              height="100%"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { datasetAPI } from '@/api/endpoints'
import ChartEngine from '@/components/charts/ChartEngine.vue'
import type { DashboardView, DashboardFilter } from '@/types'
import html2canvas from 'html2canvas'

const route = useRoute()
const router = useRouter()
const dashboardStore = useDashboardStore()
const viewerRef = ref<HTMLElement>()
const chartData = reactive<Record<number, any[]>>({})

const dashWidth = computed(() => dashboardStore.currentDashboard?.width || 1200)

const viewerStyle = computed(() => {
  const bg = dashboardStore.currentDashboard?.background_config
  return {
    background: bg?.color || '#F8FAFC',
    minHeight: '100vh',
  }
})

onMounted(async () => {
  const id = Number(route.params.id)
  await dashboardStore.loadDashboard(id)
  for (const view of dashboardStore.views) {
    if (view.chart_id) {
      await loadChartData(view)
    }
  }
})

async function loadChartData(view: DashboardView) {
  const chart = view.chart
  if (!chart) return
  try {
    const res = await datasetAPI.query(chart.dataset_id, {
      dimensions: chart.dimensions,
      measures: chart.measures,
      limit: 200,
    })
    chartData[view.chart_id || 0] = res.data.data || []
  } catch { /* ignore */ }
}

function getViewCardStyle(view: DashboardView) {
  const pos = view.position || { x: 0, y: 0, w: 400, h: 300 }
  return {
    position: 'absolute' as const,
    left: pos.x + 'px',
    top: pos.y + 'px',
    width: pos.w + 'px',
    height: pos.h + 'px',
  }
}

function getFilterComp(type: string) {
  const map: Record<string, string> = {
    dropdown: 'el-select',
    date_picker: 'el-date-picker',
    text_input: 'el-input',
    slider: 'el-slider',
  }
  return map[type] || 'el-input'
}

function getFilterProps(f: DashboardFilter) {
  return { placeholder: f.title, clearable: true, style: { width: '200px' } }
}

async function exportImage() {
  if (!viewerRef.value) return
  const canvas = await html2canvas(viewerRef.value, { backgroundColor: '#FFFFFF', useCORS: true, scale: 2 })
  const link = document.createElement('a')
  link.download = `${dashboardStore.currentDashboard?.name || 'dashboard'}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}

function exportPDF() {
  html2canvas(viewerRef.value!, { backgroundColor: '#FFFFFF', useCORS: true, scale: 2 }).then((canvas) => {
    const imgData = canvas.toDataURL('image/png')
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(`
        <html><head><title>${dashboardStore.currentDashboard?.name || 'Dashboard'}</title>
        <style>body{margin:0;display:flex;justify-content:center;}
        img{max-width:100%;height:auto;}</style></head>
        <body><img src="${imgData}" onload="window.print()"></body></html>
      `)
      printWindow.document.close()
    }
  })
}
</script>

<style scoped>
.dashboard-viewer {
  padding: 0;
}

.viewer-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: white;
  border-bottom: 1px solid var(--border);
}

.viewer-title {
  font-size: 18px;
  font-weight: 600;
  flex: 1;
}

.viewer-actions {
  display: flex;
  gap: 8px;
}

.viewer-content {
  padding: 24px;
  position: relative;
  min-height: 80vh;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.views-grid {
  position: relative;
  margin: 0 auto;
}

.view-card {
  background: white;
  border-radius: 8px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.view-card-header {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  background: #FAFAFA;
}

.view-card-body {
  height: calc(100% - 36px);
  padding: 8px;
}
</style>
