<template>
  <div class="chart-type-panel">
    <div class="panel-section" v-for="group in chartGroups" :key="group.label">
      <h4 class="group-label">{{ group.label }}</h4>
      <div class="chart-grid">
        <div
          v-for="ct in group.charts"
          :key="ct.key"
          class="chart-item"
          :class="{ active: ct.key === selected }"
          @click="$emit('select', ct.key)"
          draggable="true"
          @dragstart="onDragStart($event, ct.key)"
        >
          <div class="chart-icon">
            <component :is="getIcon(ct.key)" />
          </div>
          <span class="chart-name">{{ ct.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChartType } from '@/types'
import { h } from 'vue'

const props = defineProps<{
  selected?: ChartType
}>()

defineEmits<{
  select: [type: ChartType]
}>()

const chartGroups = [
  {
    label: '基础图表',
    charts: [
      { key: 'bar' as ChartType, name: '柱状图' },
      { key: 'line' as ChartType, name: '折线图' },
      { key: 'pie' as ChartType, name: '饼图' },
      { key: 'doughnut' as ChartType, name: '环形图' },
      { key: 'horizontal_bar' as ChartType, name: '条形图' },
      { key: 'radar' as ChartType, name: '雷达图' },
      { key: 'scatter' as ChartType, name: '散点图' },
      { key: 'area' as ChartType, name: '面积图' },
      { key: 'gauge' as ChartType, name: '仪表盘' },
      { key: 'progress' as ChartType, name: '进度条' },
    ],
  },
  {
    label: '高级图表',
    charts: [
      { key: 'funnel' as ChartType, name: '漏斗图' },
      { key: 'sankey' as ChartType, name: '桑基图' },
      { key: 'heatmap' as ChartType, name: '热力图' },
      { key: 'tree' as ChartType, name: '树图' },
      { key: 'sunburst' as ChartType, name: '旭日图' },
      { key: 'liquid' as ChartType, name: '水波图' },
      { key: 'wordcloud' as ChartType, name: '词云' },
      { key: 'map_china' as ChartType, name: '中国地图' },
      { key: 'map_world' as ChartType, name: '世界地图' },
    ],
  },
]

function getIcon(type: ChartType) {
  const icons: Record<string, any> = {
    bar: 'Histogram', line: 'DataLine', pie: 'PieChart',
    doughnut: 'Coin', horizontal_bar: 'Histogram',
    radar: 'TrendCharts', scatter: 'Grid', area: 'DataLine',
    gauge: 'Odometer', progress: 'CircleCheck',
    funnel: 'Sort', sankey: 'Share', heatmap: 'Grid',
    tree: 'List', sunburst: 'Sunny', liquid: 'Water',
    wordcloud: 'Cloudy', map_china: 'MapLocation', map_world: 'Global',
  }
  return icons[type] || 'DataBoard'
}

function onDragStart(event: DragEvent, type: ChartType) {
  event.dataTransfer?.setData('chartType', type)
}
</script>

<style scoped>
.chart-type-panel {
  padding: 12px;
}

.panel-section {
  margin-bottom: 20px;
}

.group-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
  padding: 0 4px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.chart-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.chart-item:hover {
  background: #F1F5F9;
  border-color: var(--border);
}
.chart-item.active {
  background: #EEF2FF;
  border-color: var(--primary);
}

.chart-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: var(--text-secondary);
}
.chart-item.active .chart-icon {
  color: var(--primary);
}

.chart-name {
  font-size: 10px;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.2;
}
</style>
