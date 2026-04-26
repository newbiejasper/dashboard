<template>
  <div class="chart-engine" ref="chartRef" :style="{ width: width, height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ChartType, Chart } from '@/types'

const props = withDefaults(defineProps<{
  chart: Partial<Chart>
  data?: any[]
  width?: string
  height?: string
  theme?: 'light' | 'dark'
}>(), {
  width: '100%',
  height: '100%',
  theme: 'light',
})

const chartRef = ref<HTMLElement>()
let instance: echarts.ECharts | null = null

function buildOption(): echarts.EChartsOption {
  const ct = props.chart.chart_type || 'bar'
  const dims = props.chart.dimensions || []
  const measures = props.chart.measures || []
  const data = props.data || []
  const config = props.chart.config || {}
  const colors = props.chart.color_schema || ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6']

  const xField = dims[0] || 'category'
  const yField = measures[0] || 'value'
  const yField2 = measures[1] || ''
  const values = data.map((d: any) => Number(d[yField]) || 0)
  const labels = data.map((d: any) => d[xField] || '')
  const values2 = yField2 ? data.map((d: any) => Number(d[yField2]) || 0) : []

  const baseOption: any = {
    color: colors,
    tooltip: {
      trigger: ct === 'pie' || ct === 'funnel' || ct === 'sunburst' ? 'item' : 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#E2E8F0',
      borderWidth: 1,
      textStyle: { color: '#1E293B', fontSize: 12 },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  }

  switch (ct) {
    // ===== Basic Charts =====
    case 'bar':
      return {
        ...baseOption,
        legend: yField2 ? { data: [yField, yField2], bottom: 0 } : undefined,
        xAxis: { type: 'category', data: labels, axisLabel: { rotate: labels.length > 8 ? 45 : 0 } },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar', name: yField,
          data: values, barMaxWidth: 40,
          itemStyle: { borderRadius: [4, 4, 0, 0] },
          emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' } },
        }, ...(yField2 ? [{
          type: 'bar', name: yField2,
          data: values2, barMaxWidth: 40,
          itemStyle: { borderRadius: [4, 4, 0, 0] },
        }] : [])],
      }

    case 'line':
      return {
        ...baseOption,
        xAxis: { type: 'category', data: labels },
        yAxis: { type: 'value' },
        series: [{
          type: 'line', data: values, smooth: true,
          areaStyle: { opacity: 0.1 },
          lineStyle: { width: 3 },
          symbol: 'circle', symbolSize: 6,
        }],
      }

    case 'pie':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0, type: 'scroll' },
        series: [{
          type: 'pie', radius: ['30%', '55%'],
          center: ['50%', '45%'],
          data: data.map((d: any) => ({ name: d[xField], value: Number(d[yField]) })),
          label: { formatter: '{b}\n{d}%', fontSize: 11 },
          emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.2)' } },
        }],
      }

    case 'doughnut':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0, type: 'scroll' },
        series: [{
          type: 'pie', radius: ['40%', '65%'],
          center: ['50%', '45%'],
          data: data.map((d: any) => ({ name: d[xField], value: Number(d[yField]) })),
          label: { show: false },
          emphasis: { scale: false },
        }],
      }

    case 'horizontal_bar':
      return {
        ...baseOption,
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        yAxis: { type: 'category', data: labels, axisLabel: { fontSize: 11 } },
        xAxis: { type: 'value' },
        series: [{ type: 'bar', data: values, barMaxWidth: 30, itemStyle: { borderRadius: [0, 4, 4, 0] } }],
      }

    case 'area':
      return {
        ...baseOption,
        xAxis: { type: 'category', data: labels, boundaryGap: false },
        yAxis: { type: 'value' },
        series: [{
          type: 'line', data: values,
          smooth: true, areaStyle: { opacity: 0.4 },
          lineStyle: { width: 2 },
          symbol: 'none',
        }],
      }

    case 'scatter':
      return {
        ...baseOption,
        xAxis: { type: 'value' },
        yAxis: { type: 'value' },
        series: [{
          type: 'scatter', data: data.map((d: any) => [Number(d[dims[0]] || 0), Number(d[yField] || 0)]),
          symbolSize: (val: number) => Math.max(6, val[0] % 20 + 6),
        }],
      }

    case 'radar':
      return {
        ...baseOption,
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, data: [yField] },
        radar: {
          indicator: labels.map((l) => ({ name: l, max: Math.max(...values) * 1.2 || 100 })),
          shape: 'polygon', splitNumber: 5,
        },
        series: [{ type: 'radar', data: [{ name: yField, value: values }], areaStyle: { opacity: 0.2 } }],
      }

    case 'gauge':
      return {
        ...baseOption,
        series: [{
          type: 'gauge',
          center: ['50%', '55%'],
          radius: '80%',
          startAngle: 220, endAngle: -40,
          min: 0, max: Math.max(...values) * 1.5 || 100,
          splitNumber: 5,
          progress: { show: true, width: 12 },
          axisLine: { lineStyle: { width: 12 } },
          axisTick: { show: false },
          splitLine: { length: 8, lineStyle: { width: 2 } },
          axisLabel: { distance: 20, fontSize: 10 },
          detail: { fontSize: 18, fontWeight: 'bold', formatter: '{value}' },
          data: [{ value: values[0] || 0, name: xField }],
        }],
      }

    case 'progress':
      return {
        ...baseOption,
        grid: { left: '3%', right: '10%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', max: 100, splitLine: { show: false }, axisLabel: { show: false } },
        yAxis: { type: 'category', data: labels, axisLine: { show: false }, axisTick: { show: false } },
        series: [{
          type: 'bar', data: values,
          barMaxWidth: 20,
          label: { show: true, position: 'right', formatter: '{c}%', fontWeight: 'bold' },
          itemStyle: { borderRadius: [0, 10, 10, 0] },
        }],
      }

    // ===== Advanced Charts =====
    case 'funnel':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{a}<br/>{b}: {c} ({d}%)' },
        series: [{
          type: 'funnel', left: '10%', right: '10%', bottom: '10%',
          data: data.map((d: any) => ({ name: d[xField], value: Number(d[yField]) })),
          label: { show: true, position: 'inside', formatter: '{b}: {c}', fontSize: 11 },
          emphasis: { label: { fontSize: 14 } },
        }],
      }

    case 'sankey':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c}' },
        series: [{
          type: 'sankey',
          layout: 'none',
          emphasis: { focus: 'adjacency' },
          nodeAlign: 'left',
          data: labels.map((l) => ({ name: l })),
          links: data.slice(0, -1).map((d: any, i: number) => ({
            source: d[xField],
            target: data[i + 1]?.[xField] || '',
            value: Math.abs(Number(d[yField])),
          })),
          lineStyle: { curveness: 0.5 },
        }],
      }

    case 'heatmap':
      return {
        ...baseOption,
        tooltip: { position: 'top' },
        grid: { left: '10%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', data: labels.slice(0, 10), splitArea: { show: true } },
        yAxis: { type: 'category', data: labels.slice(0, 10), splitArea: { show: true } },
        visualMap: { min: 0, max: Math.max(...values), calculable: true, orient: 'horizontal', left: 'center', bottom: '0%' },
        series: [{
          type: 'heatmap',
          data: data.slice(0, 100).map((d: any, i: number) => [i % 10, Math.floor(i / 10), Number(d[yField])]),
          label: { show: true },
          emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } },
        }],
      }

    case 'tree':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c}' },
        series: [{
          type: 'tree',
          data: [{ name: xField, children: data.slice(0, 20).map((d: any) => ({ name: d[xField], value: Number(d[yField]) })) }],
          top: '5%', left: '5%', bottom: '5%', right: '15%',
          symbolSize: 8,
          label: { position: 'left', verticalAlign: 'middle', fontSize: 11 },
          leaves: { label: { position: 'right' } },
          expandAndCollapse: true,
          animationDuration: 550,
        }],
      }

    case 'sunburst':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c}' },
        series: [{
          type: 'sunburst',
          data: data.slice(0, 30).map((d: any) => ({ name: d[xField], value: Number(d[yField]) })),
          radius: [0, '90%'],
          label: { rotate: 'radial' },
          emphasis: { focus: 'ancestor' },
        }],
      }

    case 'liquid':
      return {
        ...baseOption,
        series: [{
          type: 'liquidFill',
          data: [values[0] / 100 || 0.5],
          center: ['50%', '50%'],
          radius: '60%',
          waveAnimation: true,
          outline: { show: true, borderDistance: 8, itemStyle: { borderWidth: 2 } },
          label: { fontSize: 24, fontWeight: 'bold', formatter: (p: any) => `${(p.value * 100).toFixed(1)}%` },
        }],
      }

    case 'wordcloud':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c}' },
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          left: 'center', top: 'center',
          width: '90%', height: '90%',
          sizeRange: [12, 40],
          rotationRange: [-90, 90],
          rotationStep: 45,
          gridSize: 8,
          drawOutOfBound: false,
          data: data.slice(0, 50).map((d: any) => ({
            name: d[xField],
            value: Number(d[yField]),
            textStyle: { color: colors[Math.floor(Math.random() * colors.length)] },
          })),
        }],
      }

    case 'map_china':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c}' },
        visualMap: { min: Math.min(...values), max: Math.max(...values), inRange: { color: ['#E0E7FF', '#4F46E5', '#312E81'] } },
        series: [{
          type: 'map', map: 'china',
          roam: true,
          label: { show: true, fontSize: 10 },
          data: data.map((d: any) => ({ name: d[xField], value: Number(d[yField]) })),
        }],
      }

    case 'map_world':
      return {
        ...baseOption,
        tooltip: { trigger: 'item', formatter: '{b}: {c}' },
        visualMap: { min: Math.min(...values), max: Math.max(...values) },
        series: [{
          type: 'map', map: 'world',
          roam: true,
          label: { show: false },
          data: data.map((d: any) => ({ name: d[xField], value: Number(d[yField]) })),
        }],
      }

    default:
      return {
        ...baseOption,
        xAxis: { type: 'category', data: labels },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: values }],
      }
  }
}

function renderChart() {
  if (!chartRef.value) return
  if (!instance) {
    instance = echarts.init(chartRef.value, props.theme === 'dark' ? 'dark' : undefined)
  }
  const option = buildOption()
  instance.setOption(option, true)
  instance.resize()
}

watch(() => [props.data, props.chart], () => nextTick(renderChart), { deep: true })

onMounted(() => {
  nextTick(renderChart)
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  instance?.dispose()
  instance = null
})

function handleResize() {
  instance?.resize()
}

defineExpose({ resize: handleResize, getInstance: () => instance })
</script>

<style scoped>
.chart-engine {
  min-height: 200px;
}
</style>
