<template>
  <div class="dashboard-editor">
    <!-- Top Toolbar -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <el-divider direction="vertical" />
        <el-input
          v-model="dashboardName"
          class="title-input"
          @blur="saveTitle"
          placeholder="仪表板名称"
        />
      </div>
      <div class="toolbar-center">
        <el-button-group>
          <el-tooltip content="添加图表" placement="bottom">
            <el-button @click="showAddChart = true">
              <el-icon><Plus /></el-icon>
              添加视图
            </el-button>
          </el-tooltip>
          <el-tooltip content="添加过滤组件" placement="bottom">
            <el-button @click="showAddFilter = true">
              <el-icon><Filter /></el-icon>
              过滤组件
            </el-button>
          </el-tooltip>
        </el-button-group>
      </div>
      <div class="toolbar-right">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button type="primary" :loading="saving" @click="saveDashboard">
          <el-icon><Check /></el-icon> 保存
        </el-button>
        <el-button @click="previewDashboard">
          <el-icon><View /></el-icon> 预览
        </el-button>
        <el-button @click="showShareDialog = true">
          <el-icon><Share /></el-icon> 分享
        </el-button>
      </div>
    </div>

    <div class="editor-body">
      <!-- Left: Chart Type Panel -->
      <div class="editor-left" v-show="showLeftPanel">
        <div class="panel-header">
          <span>组件</span>
          <el-button text @click="showLeftPanel = false"><el-icon><Close /></el-icon></el-button>
        </div>
        <ChartTypePanel @select="onChartSelect" />
      </div>

      <!-- Center: Canvas -->
      <div class="editor-canvas" @drop.prevent="onDrop" @dragover.prevent>
        <div class="canvas-header">
          <span class="canvas-size">{{ dashboardStore.currentDashboard?.width }} × {{ dashboardStore.currentDashboard?.height }}</span>
        </div>
        <div
          class="canvas-area"
          :style="canvasStyle"
          ref="canvasRef"
        >
          <grid-layout
            :layout="gridLayout"
            :col-num="12"
            :row-height="150"
            :margin="[10, 10]"
            :is-draggable="true"
            :is-resizable="true"
            :vertical-compact="true"
            :use-css-transforms="true"
            @layout-updated="onLayoutUpdated"
          >
            <!-- Chart Views -->
            <grid-item
              v-for="view in dashboardStore.views"
              :key="'v-' + view.id"
              :x="getGridItem(view).x"
              :y="getGridItem(view).y"
              :w="getGridItem(view).w"
              :h="getGridItem(view).h"
              :i="'v-' + view.id"
              class="canvas-view"
              :class="{ selected: selectedView?.id === view.id }"
              @click="selectView(view)"
            >
              <div class="view-header">
                <span class="view-title">{{ view.title || view.chart?.name || '图表' }}</span>
                <div class="view-actions">
                  <el-button text size="small" @click.stop="editView(view)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button text size="small" type="danger" @click.stop="removeView(view)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="view-content">
                <ChartEngine
                  v-if="view.chart"
                  :chart="view.chart"
                  :data="chartData[view.chart_id || 0] || []"
                />
                <div v-else class="empty-chart">
                  <el-icon :size="32" color="#CBD5E1"><DataBoard /></el-icon>
                  <p>请选择图表类型</p>
                </div>
              </div>
            </grid-item>

            <!-- Filter Components -->
            <grid-item
              v-for="(f, idx) in dashboardStore.filters"
              :key="'f-' + idx"
              :x="getFilterGrid(f, idx).x"
              :y="getFilterGrid(f, idx).y"
              :w="getFilterGrid(f, idx).w"
              :h="1"
              :i="'f-' + idx"
              :is-resizable="false"
              class="canvas-filter"
            >
              <div class="filter-content">
                <span class="filter-label">{{ f.title }}</span>
                <component :is="getFilterComponent(f.filter_type)" v-bind="getFilterProps(f)" />
              </div>
            </grid-item>
          </grid-layout>

          <!-- Empty state -->
          <el-empty
            v-if="dashboardStore.views.length === 0 && dashboardStore.filters.length === 0"
            description="拖拽左侧图表到画布，或点击上方「添加视图」"
            :image-size="100"
            style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%)"
          />
        </div>
      </div>

      <!-- Right: Config Panel -->
      <div class="editor-right" v-show="showRightPanel">
        <div class="panel-header">
          <span>配置</span>
          <el-button text @click="showRightPanel = false"><el-icon><Close /></el-icon></el-button>
        </div>

        <el-tabs v-model="configTab" class="config-tabs">
          <el-tab-pane label="数据" name="data">
            <div class="config-section" v-if="selectedView?.chart">
              <h4>数据集</h4>
              <el-select v-model="selectedView.chart.dataset_id" class="config-select" @change="onDatasetChange">
                <el-option
                  v-for="ds in datasets"
                  :key="ds.id"
                  :label="ds.name"
                  :value="ds.id"
                />
              </el-select>

              <h4>维度</h4>
              <el-select v-model="selectedView.chart.dimensions" multiple class="config-select" @change="onConfigChange">
                <el-option
                  v-for="f in datasetDimensions.length > 0 ? datasetDimensions : currentFields"
                  :key="f.name"
                  :label="f.alias || f.name"
                  :value="f.name"
                >
                  <span>{{ f.alias || f.name }}</span>
                  <span v-if="f.sub_dimensions?.length" class="field-hint">
                    <el-icon><ArrowRight /></el-icon> {{ f.sub_dimensions.map((s: any) => s.name).join(', ') }}
                  </span>
                </el-option>
              </el-select>

              <h4>指标</h4>
              <el-select v-model="selectedView.chart.measures" multiple class="config-select" @change="onConfigChange">
                <el-option
                  v-for="f in datasetMeasures.length > 0 ? datasetMeasures : currentFields"
                  :key="f.name"
                  :label="f.alias || f.name"
                  :value="f.name"
                >
                  <span>{{ f.alias || f.name }}</span>
                  <span class="field-hint">{{ f.aggregation }}</span>
                </el-option>
              </el-select>
            </div>
            <el-empty v-else description="请选择一个视图" :image-size="60" />
          </el-tab-pane>

          <el-tab-pane label="样式" name="style">
            <div class="config-section" v-if="selectedView">
              <h4>标题</h4>
              <el-input v-model="selectedView.title" placeholder="视图标题" @change="onConfigChange" />

              <h4>背景颜色</h4>
              <el-color-picker v-model="selectedView.style.backgroundColor" @change="onConfigChange" />

              <h4>边框</h4>
              <el-select v-model="selectedView.style.borderStyle" class="config-select" @change="onConfigChange">
                <el-option label="无边框" value="none" />
                <el-option label="实线" value="solid" />
                <el-option label="虚线" value="dashed" />
              </el-select>
            </div>
          </el-tab-pane>

          <el-tab-pane label="交互" name="interaction">
            <div class="config-section" v-if="selectedView">
              <el-checkbox v-model="interactions.linkage" label="图表联动" @change="saveInteractions" />
              <p class="config-hint">联动筛选会影响其他关联图表</p>

              <h4 style="margin-top: 16px;">下钻层级</h4>
              <el-select
                v-model="interactions.drill_down_hierarchy"
                multiple
                class="config-select"
                placeholder="点击触发下钻"
                @change="saveInteractions"
              >
                <el-option label="国家→省份→城市" value="country,province,city" />
                <el-option label="年份→季度→月份" value="year,quarter,month" />
                <el-option label="类别→子类→产品" value="category,subcategory,product" />
              </el-select>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- Add Chart Dialog -->
    <el-dialog v-model="showAddChart" title="添加图表" width="400px">
      <ChartTypePanel @select="addNewChart" />
      <template #footer>
        <el-button @click="showAddChart = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- Share Dialog -->
    <el-dialog v-model="showShareDialog" title="分享仪表板" width="480px">
      <div class="share-content">
        <h4>公共链接</h4>
        <el-input :model-value="shareUrl" readonly>
          <template #append>
            <el-button @click="copyText(shareUrl)">复制</el-button>
          </template>
        </el-input>

        <h4 style="margin-top: 16px;">嵌入代码 (Iframe)</h4>
        <el-input :model-value="embedCode" type="textarea" :rows="3" readonly>
          <template #append>
            <el-button @click="copyText(embedCode)">复制</el-button>
          </template>
        </el-input>

        <el-checkbox v-model="shareWithPassword" style="margin-top: 12px;">密码保护</el-checkbox>
        <el-input v-if="shareWithPassword" v-model="sharePassword" placeholder="设置访问密码" style="margin-top: 8px;" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { dashboardAPI, datasetAPI } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import ChartEngine from '@/components/charts/ChartEngine.vue'
import ChartTypePanel from '@/components/charts/ChartTypePanel.vue'
import VueGridLayout from 'vue3-grid-layout'
import type { DashboardView, DashboardFilter, Dataset, ChartType, Chart } from '@/types'

const { GridLayout, GridItem } = VueGridLayout

// Pixel → Grid conversion (12 cols, 150px rowHeight, 10px margin)
const COL_W = 160  // 1920/12 approx
const ROW_H = 160  // rowHeight + margin[1]

function pixelsToGrid(p: { x?: number; y?: number; w?: number; h?: number }) {
  return {
    x: Math.round((p.x || 0) / COL_W),
    y: Math.round((p.y || 0) / ROW_H),
    w: Math.max(2, Math.round((p.w || 400) / COL_W)),
    h: Math.max(2, Math.round((p.h || 300) / ROW_H)),
  }
}

function gridToPixels(g: { x: number; y: number; w: number; h: number }) {
  return {
    x: g.x * COL_W,
    y: g.y * ROW_H,
    w: g.w * COL_W,
    h: g.h * ROW_H,
  }
}

const route = useRoute()
const router = useRouter()
const dashboardStore = useDashboardStore()
const canvasRef = ref<HTMLElement>()

// UI state
const showLeftPanel = ref(true)
const showRightPanel = ref(true)
const showAddChart = ref(false)
const showAddFilter = ref(false)
const showShareDialog = ref(false)
const configTab = ref('data')
const saving = ref(false)
const selectedView = ref<DashboardView | null>(null)
const dashboardName = ref('')
const datasets = ref<Dataset[]>([])
const chartData = reactive<Record<number, any[]>>({})

// Grid layout state
const gridLayout = ref<{ i: string; x: number; y: number; w: number; h: number }[]>([])

// Interactions
const interactions = reactive({
  linkage: false,
  drill_down_hierarchy: [] as string[],
})

// Share
const shareUrl = ref('')
const embedCode = ref('')
const shareWithPassword = ref(false)
const sharePassword = ref('')

const canvasStyle = computed(() => {
  const dash = dashboardStore.currentDashboard
  if (!dash) return {}
  return {
    width: `${dash.width}px`,
    minHeight: `${dash.height}px`,
    background: dash.background_config?.color || '#FFFFFF',
    backgroundImage: dash.background_config?.image ? `url(${dash.background_config.image})` : undefined,
    backgroundSize: 'cover',
  }
})

const currentFields = computed(() => {
  const chart = selectedView.value?.chart
  if (!chart) return []
  const ds = datasets.value.find((d) => d.id === chart.dataset_id)
  return ds?.fields_config || []
})

// Use dataset's structured config for dimension/measure suggestions
const datasetDimensions = computed(() => {
  const chart = selectedView.value?.chart
  if (!chart) return []
  const ds = datasets.value.find((d) => d.id === chart.dataset_id)
  return ds?.dimensions_config || []
})

const datasetMeasures = computed(() => {
  const chart = selectedView.value?.chart
  if (!chart) return []
  const ds = datasets.value.find((d) => d.id === chart.dataset_id)
  return ds?.measures_config || []
})

// Convert view pixel position to grid layout item
function getGridItem(view: DashboardView) {
  const pos = view.position || { x: 20, y: 20, w: 400, h: 300 }
  return pixelsToGrid(pos)
}

// Put filters in the grid too (2-col width, place them below views)
function getFilterGrid(_filter: DashboardFilter, idx: number) {
  return { x: 0, y: 999 + idx, w: 4, h: 1 }
}

function getViewStyle(_view: DashboardView) {
  return {} // No longer used for positioning
}

function buildGridLayout() {
  const items: { i: string; x: number; y: number; w: number; h: number }[] = []
  for (const view of dashboardStore.views) {
    const g = getGridItem(view)
    items.push({ i: 'v-' + view.id, ...g })
  }
  for (let idx = 0; idx < dashboardStore.filters.length; idx++) {
    const g = getFilterGrid(dashboardStore.filters[idx], idx)
    items.push({ i: 'f-' + idx, ...g, h: 1 })
  }
  // Preserve existing grid item positions whenever possible
  if (gridLayout.value.length > 0) {
    for (const item of items) {
      const existing = gridLayout.value.find((e) => e.i === item.i)
      if (existing) {
        item.x = existing.x
        item.y = existing.y
        item.w = existing.w
        item.h = existing.h
      }
    }
  }
  gridLayout.value = items
}

// Called when grid-layout changes (drag/resize)
function onLayoutUpdated(newLayout: { i: string; x: number; y: number; w: number; h: number }[]) {
  for (const item of newLayout) {
    if (item.i.startsWith('v-')) {
      const viewId = Number(item.i.slice(2))
      const view = dashboardStore.views.find((v) => v.id === viewId)
      if (view) {
        const pixel = gridToPixels(item)
        view.position = { x: pixel.x, y: pixel.y, w: pixel.w, h: pixel.h }
      }
    }
  }
  gridLayout.value = newLayout
}

onMounted(async () => {
  const id = Number(route.params.id)
  await dashboardStore.loadDashboard(id)
  dashboardName.value = dashboardStore.currentDashboard?.name || ''

  // Load datasets
  const dsRes = await datasetAPI.list()
  datasets.value = dsRes.data

  // Load chart data for each view
  for (const view of dashboardStore.views) {
    if (view.chart_id) {
      await loadChartData(view)
    }
  }

  // Build grid layout from views
  buildGridLayout()

  // Load share info
  const dash = dashboardStore.currentDashboard
  if (dash) {
    const baseUrl = window.location.origin
    shareUrl.value = `${baseUrl}/share/${dash.share_token}`
    embedCode.value = `<iframe src="${baseUrl}/embed/${dash.embed_token}" width="100%" height="100%" frameborder="0"></iframe>`
  }

  // Load interactions
  if (selectedView.value?.interactions) {
    interactions.linkage = selectedView.value.interactions.linkage || false
    interactions.drill_down_hierarchy = selectedView.value.interactions.drill_down_hierarchy || []
  }
})

// Rebuild grid when views or filters change
watch(
  () => [dashboardStore.views.length, dashboardStore.filters.length],
  () => {
    buildGridLayout()
  }
)

async function loadChartData(view: DashboardView) {
  if (!view.chart_id) return
  const chart = view.chart
  if (!chart) return

  try {
    const res = await datasetAPI.query(chart.dataset_id, {
      dimensions: chart.dimensions,
      measures: chart.measures,
      limit: 200,
    })
    chartData[view.chart_id] = res.data.data || []
  } catch (err) {
    console.error('Failed to load chart data', err)
  }
}

function selectView(view: DashboardView) {
  selectedView.value = view
  showRightPanel.value = true
  interactions.linkage = view.interactions?.linkage || false
  interactions.drill_down_hierarchy = view.interactions?.drill_down_hierarchy || []
}

function onChartSelect(type: ChartType) {
  showAddChart.value = false
  // Will be handled by addNewChart
}

async function addNewChart(type: ChartType) {
  showAddChart.value = false
  const dashId = Number(route.params.id)
  const ds = datasets.value[0]
  if (!ds) {
    ElMessage.warning('请先创建数据集')
    return
  }

  const chartRes = await dashboardAPI.createChart({
    chart_type: type,
    dataset_id: ds.id,
    dimensions: [],
    measures: [],
  })
  const chart = chartRes.data

  // Find an empty grid slot for the new chart
  const usedCells = new Set<string>()
  for (const v of dashboardStore.views) {
    const g = getGridItem(v)
    for (let dx = 0; dx < g.w; dx++) {
      for (let dy = 0; dy < g.h; dy++) {
        usedCells.add(`${g.x + dx},${g.y + dy}`)
      }
    }
  }
  let gridX = 0, gridY = 0
  for (let y = 0; y < 100; y++) {
    for (let x = 0; x <= 12 - 6; x++) {
      let occupied = false
      for (let dx = 0; dx < 6; dx++) {
        if (usedCells.has(`${x + dx},${y}`)) { occupied = true; break }
      }
      if (!occupied) { gridX = x; gridY = y; y = 100; break }
    }
  }
  const pixel = gridToPixels({ x: gridX, y: gridY, w: 6, h: 2 })

  const viewRes = await dashboardAPI.addView(dashId, {
    title: '',
    chart_id: chart.id,
    position: { x: pixel.x, y: pixel.y, w: pixel.w, h: pixel.h },
    style: { backgroundColor: '#FFFFFF', borderStyle: 'solid' },
    interactions: {},
  })
  dashboardStore.addView(viewRes.data)
  selectedView.value = viewRes.data
  await loadChartData(viewRes.data)
}

async function editView(view: DashboardView) {
  selectView(view)
}

async function removeView(view: DashboardView) {
  const dashId = Number(route.params.id)
  await dashboardAPI.removeView(dashId, view.id)
  dashboardStore.removeView(view.id)
  if (selectedView.value?.id === view.id) {
    selectedView.value = null
  }
}

function onDrop(event: DragEvent) {
  const chartType = event.dataTransfer?.getData('chartType') as ChartType
  if (chartType) {
    addNewChart(chartType)
  }
}

function onDatasetChange() {
  selectedView.value && loadChartData(selectedView.value)
}

function onConfigChange() {
  // Auto-save on config changes
  if (selectedView.value) {
    saveDashboard()
  }
}

function saveInteractions() {
  if (!selectedView.value) return
  selectedView.value.interactions = { ...interactions }
  saveDashboard()
}

async function saveDashboard() {
  saving.value = true
  try {
    const dashId = Number(route.params.id)
    if (selectedView.value) {
      await dashboardAPI.updateView(dashId, selectedView.value.id, {
        title: selectedView.value.title,
        position: selectedView.value.position,
        style: selectedView.value.style,
        interactions: selectedView.value.interactions,
        chart_id: selectedView.value.chart_id,
      })
    }
    if (dashboardName.value) {
      await dashboardAPI.update(dashId, { name: dashboardName.value })
    }
    ElMessage.success('保存成功')
  } catch {
    // Silent fail for auto-save
  } finally {
    saving.value = false
  }
}

async function saveTitle() {
  if (dashboardName.value && dashboardStore.currentDashboard) {
    await dashboardStore.saveDashboard({ name: dashboardName.value })
  }
}

function refreshData() {
  dashboardStore.views.forEach((v) => loadChartData(v))
}

function previewDashboard() {
  const id = Number(route.params.id)
  window.open(`/dashboard/${id}/view`, '_blank')
}

function goBack() {
  router.push('/dashboard')
}

function getFilterComponent(type: string) {
  const map: Record<string, string> = {
    dropdown: 'el-select',
    date_picker: 'el-date-picker',
    text_input: 'el-input',
    slider: 'el-slider',
  }
  return map[type] || 'el-input'
}

function getFilterProps(filter: DashboardFilter) {
  return { placeholder: filter.title, style: { width: '100%' } }
}

function copyText(text: string) {
  navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制'))
}
</script>

<style scoped>
.dashboard-editor {
  height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
  background: #F1F5F9;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: white;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  z-index: 10;
}

.toolbar-left, .toolbar-center, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-input {
  width: 240px;
}

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-left, .editor-right {
  width: 260px;
  background: white;
  border-right: 1px solid var(--border);
  overflow-y: auto;
  flex-shrink: 0;
}

.editor-right {
  border-right: none;
  border-left: 1px solid var(--border);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  font-weight: 600;
  font-size: 14px;
}

.editor-canvas {
  flex: 1;
  overflow: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.canvas-header {
  width: 100%;
  max-width: 1200px;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.canvas-size {
  font-size: 11px;
  color: var(--text-light);
  background: white;
  padding: 2px 10px;
  border-radius: 4px;
  border: 1px solid var(--border);
}

.canvas-area {
  position: relative;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 10px;
}

.canvas-area :deep(.vue-grid-item) {
  transition: all 200ms ease;
}

.canvas-area :deep(.vue-resizable-handle) {
  z-index: 10;
}

.canvas-view {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

.canvas-view:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.canvas-view.selected {
  outline: 2px solid var(--primary);
  outline-offset: -2px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  border-bottom: 1px solid var(--border-light);
  background: #FAFAFA;
}

.view-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.view-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
}
.canvas-view:hover .view-actions {
  opacity: 1;
}

.view-content {
  flex: 1;
  min-height: 0;
}

.empty-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #CBD5E1;
  font-size: 12px;
}

.canvas-filter {
  height: 100%;
  background: white;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
}

.filter-content {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.filter-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
}

.config-tabs {
  padding: 0 12px;
}

.config-section {
  padding: 12px 0;
}

.config-section h4 {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 12px 0 6px;
}
.config-section h4:first-child {
  margin-top: 0;
}

.config-select {
  width: 100%;
  margin-bottom: 4px;
}

.config-hint {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 4px;
}

.share-content {
  padding: 8px 0;
}

.share-content h4 {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}
</style>

<style>
/* Global style for dashboard editor field hints */
.field-hint {
  font-size: 11px;
  color: var(--text-light);
  margin-left: 8px;
}
.field-hint .el-icon {
  vertical-align: middle;
  font-size: 12px;
}
</style>
