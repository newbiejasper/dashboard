<template>
  <el-dialog
    v-model="visible"
    title="创建数据集"
    width="820px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-steps :active="step" align-center finish-status="success" style="margin-bottom: 24px">
      <el-step title="选择数据表" />
      <el-step title="配置维度 & 指标" />
      <el-step title="下钻 & 筛选" />
    </el-steps>

    <!-- Step 1: Select Data Source & Table -->
    <div v-show="step === 0" class="step-content">
      <h3 class="step-title">选择数据源和表</h3>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">数据源</label>
          <el-select v-model="form.datasource_id" placeholder="选择数据源" @change="onDatasourceChange" class="full-width">
            <el-option
              v-for="ds in datasources"
              :key="ds.id"
              :label="ds.name"
              :value="ds.id"
            >
              <span>{{ ds.name }}</span>
              <span class="ds-type-tag">{{ getSourceLabel(ds.source_type) }}</span>
            </el-option>
          </el-select>
        </div>
        <div class="form-group">
          <label class="form-label">数据集名称</label>
          <el-input v-model="form.name" placeholder="输入数据集名称" />
        </div>
      </div>

      <div v-if="step0Loading" class="loading-area">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>正在加载表列表...</span>
      </div>

      <div v-else-if="tables.length > 0" class="table-list">
        <div
          v-for="t in tables"
          :key="t.name"
          class="table-item"
          :class="{ selected: form.source_table === t.name }"
          @click="selectTable(t)"
        >
          <div class="table-icon">
            <el-icon :size="20"><DataBoard /></el-icon>
          </div>
          <div class="table-info">
            <span class="table-name">{{ t.name }}</span>
            <span class="table-comment">{{ t.comment || '暂无注释' }}</span>
          </div>
          <div class="table-meta">
            <el-tag size="small" type="info">{{ formatRows(t.rows) }} 行</el-tag>
          </div>
          <el-icon v-if="form.source_table === t.name" class="check-icon" color="#4F46E5"><CircleCheck /></el-icon>
        </div>
      </div>

      <el-empty v-else-if="form.datasource_id && !step0Loading" description="该数据源下没有表" :image-size="60" />
    </div>

    <!-- Step 2: Configure Dimensions & Measures -->
    <div v-show="step === 1" class="step-content">
      <h3 class="step-title">配置维度与指标</h3>
      <p class="step-desc">将字段拖拽或勾选到对应的角色中</p>

      <!-- Available Fields -->
      <div class="field-section">
        <h4>可用字段</h4>
        <div class="field-chips">
          <el-tag
            v-for="col in availableColumns"
            :key="col.name"
            closable
            :type="col.assigned === 'dimension' ? 'success' : col.assigned === 'measure' ? 'primary' : ''"
            :disable-transitions="false"
            @close="unassignField(col)"
            @click="autoAssignField(col)"
          >
            <el-icon style="margin-right: 4px; vertical-align: middle;">
              <component :is="col.type === 'number' ? 'TrendCharts' : col.type === 'date' ? 'Clock' : 'List'" />
            </el-icon>
            {{ col.name }}
            <span class="field-type-badge">{{ col.type }}</span>
          </el-tag>
        </div>
      </div>

      <div class="config-columns">
        <!-- Dimensions -->
        <div class="config-panel">
          <div class="panel-header dimension-header">
            <el-icon><Grid /></el-icon>
            <span>维度 (Dimensions)</span>
            <el-tag size="small" type="success">{{ form.dimensions_config.length }}</el-tag>
          </div>
          <div class="panel-body">
            <div
              v-for="(dim, idx) in form.dimensions_config"
              :key="idx"
              class="config-item"
            >
              <div class="item-row">
                <el-icon class="drag-handle"><Rank /></el-icon>
                <span class="item-name">{{ dim.name }}</span>
                <el-tag size="small" :type="dim.type === 'date' ? 'warning' : 'success'" class="item-type-tag">{{ dim.type }}</el-tag>
                <el-input
                  v-model="dim.alias"
                  placeholder="别名"
                  size="small"
                  class="alias-input"
                />
                <el-button text size="small" type="danger" @click="removeDimension(idx)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <!-- Sub-dimensions -->
              <div v-if="dim.sub_dimensions && dim.sub_dimensions.length > 0" class="sub-dims">
                <span class="sub-label">子维度:</span>
                <el-tag
                  v-for="(sub, si) in dim.sub_dimensions"
                  :key="si"
                  size="small"
                  closable
                  @close="removeSubDimension(idx, si)"
                >
                  {{ sub.name }}
                </el-tag>
              </div>
              <div class="add-sub">
                <el-select
                  v-model="newSubDim[idx]"
                  placeholder="+ 添加子维度"
                  size="small"
                  filterable
                  @change="(val: string) => addSubDimension(idx, val)"
                >
                  <el-option
                    v-for="col in unassignedColumns"
                    :key="col.name"
                    :label="col.name"
                    :value="col.name"
                  />
                </el-select>
              </div>
            </div>
            <el-empty v-if="form.dimensions_config.length === 0" description="点击上方字段自动分配" :image-size="40" />
          </div>
        </div>

        <!-- Measures -->
        <div class="config-panel">
          <div class="panel-header measure-header">
            <el-icon><TrendCharts /></el-icon>
            <span>指标 (Measures)</span>
            <el-tag size="small" type="primary">{{ form.measures_config.length }}</el-tag>
          </div>
          <div class="panel-body">
            <div
              v-for="(m, idx) in form.measures_config"
              :key="idx"
              class="config-item"
            >
              <div class="item-row">
                <el-icon class="drag-handle"><Rank /></el-icon>
                <span class="item-name">{{ m.name }}</span>
                <el-tag size="small" type="primary" class="item-type-tag">{{ m.type }}</el-tag>
                <el-select v-model="m.aggregation" size="small" class="agg-select">
                  <el-option label="SUM" value="SUM" />
                  <el-option label="AVG" value="AVG" />
                  <el-option label="COUNT" value="COUNT" />
                  <el-option label="MAX" value="MAX" />
                  <el-option label="MIN" value="MIN" />
                  <el-option label="COUNT DISTINCT" value="COUNT_DISTINCT" />
                </el-select>
                <el-input
                  v-model="m.alias"
                  placeholder="别名"
                  size="small"
                  class="alias-input"
                />
                <el-button text size="small" type="danger" @click="removeMeasure(idx)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <el-empty v-if="form.measures_config.length === 0" description="点击上方字段自动分配" :image-size="40" />
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Drill-down & Filter Fields -->
    <div v-show="step === 2" class="step-content">
      <h3 class="step-title">配置下钻维度与筛选项</h3>

      <div class="config-section">
        <h4>
          <el-icon><Down /></el-icon>
          下钻维度 (Drill-down)
        </h4>
        <p class="section-desc">配置图表点击下钻的层级路径，如：国家 → 省份 → 城市</p>
        <div
          v-for="(drill, idx) in form.drill_down_config"
          :key="idx"
          class="drill-item card"
        >
          <div class="drill-header">
            <el-input v-model="drill.name" placeholder="下钻名称（如：地理下钻）" size="small" class="drill-name-input" />
            <el-button text size="small" type="danger" @click="removeDrill(idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <div class="drill-levels">
            <div v-for="(lv, li) in drill.levels" :key="li" class="drill-level-row">
              <el-icon><ArrowRight /></el-icon>
              <el-tag closable @close="removeDrillLevel(idx, li)" class="level-tag">
                {{ lv }}
              </el-tag>
            </div>
            <el-select
              v-model="newDrillLevel[idx]"
              placeholder="+ 添加层级"
              size="small"
              filterable
              @change="(val: string) => addDrillLevel(idx, val)"
            >
              <el-option
                v-for="col in allConfigurableColumns"
                :key="col.name"
                :label="col.name"
                :value="col.name"
              />
            </el-select>
          </div>
        </div>
        <el-button size="small" @click="addDrillGroup" class="add-btn">
          <el-icon><Plus /></el-icon> 添加下钻组
        </el-button>
      </div>

      <div class="config-section">
        <h4>
          <el-icon><Filter /></el-icon>
          筛选项 (Filter Fields)
        </h4>
        <p class="section-desc">预定义的筛选字段，将自动显示在仪表板的筛选器区域</p>
        <div
          v-for="(flt, idx) in form.filter_fields"
          :key="idx"
          class="filter-item card"
        >
          <div class="filter-row">
            <span class="filter-field-label">{{ flt.field }}</span>
            <el-select v-model="flt.type" size="small" class="filter-type-select">
              <el-option label="下拉选择" value="dropdown" />
              <el-option label="日期选择" value="date_picker" />
              <el-option label="日期范围" value="date_range" />
              <el-option label="文本输入" value="text_input" />
              <el-option label="滑块" value="slider" />
            </el-select>
            <el-input v-model="flt.alias" placeholder="显示名称" size="small" class="alias-input" />
            <el-button text size="small" type="danger" @click="removeFilter(idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        <el-select
          v-model="newFilterField"
          placeholder="+ 添加筛选项"
          size="small"
          filterable
          class="add-filter-select"
          @change="addFilterField"
        >
          <el-option
            v-for="col in allConfigurableColumns"
            :key="col.name"
            :label="col.name"
            :value="col.name"
          />
        </el-select>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button v-if="step > 0" @click="step--">上一步</el-button>
      <el-button v-if="step < 2" type="primary" :disabled="!canNext" @click="step++">下一步</el-button>
      <el-button v-if="step === 2" type="primary" :loading="creating" @click="handleCreate">创建数据集</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { datasourceAPI, datasetAPI } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import type { DataSource } from '@/types'

const props = defineProps<{
  modelValue: boolean
  datasources: DataSource[]
}>()
const emit = defineEmits(['update:modelValue', 'created'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

// === State ===
const step = ref(0)
const creating = ref(false)
const step0Loading = ref(false)
const tables = ref<{ name: string; comment: string; engine: string; rows: number }[]>([])
const columns = ref<{ name: string; type: string; original_type: string; comment: string }[]>([])

// Dynamic sub-dimension/level select models
const newSubDim = ref<Record<number, string>>({})
const newDrillLevel = ref<Record<number, string>>({})
const newFilterField = ref('')

const form = ref({
  name: '',
  datasource_id: null as number | null,
  source_table: '',
  fields_config: [] as any[],
  dimensions_config: [] as any[],
  measures_config: [] as any[],
  drill_down_config: [] as any[],
  filter_fields: [] as any[],
})

// === Computed ===
const assignedFields = computed(() => {
  const dimNames = form.value.dimensions_config.map((d) => d.name)
  const measureNames = form.value.measures_config.map((m) => m.name)
  const subDimNames = form.value.dimensions_config.flatMap((d) => (d.sub_dimensions || []).map((s: any) => s.name))
  const drillNames = form.value.drill_down_config.flatMap((d) => d.levels)
  const filterNames = form.value.filter_fields.map((f) => f.field)
  return new Set([...dimNames, ...measureNames, ...subDimNames, ...drillNames, ...filterNames])
})

const availableColumns = computed(() => {
  return columns.value.map((col) => ({
    ...col,
    assigned: form.value.dimensions_config.find((d) => d.name === col.name) ? 'dimension'
      : form.value.measures_config.find((m) => m.name === col.name) ? 'measure'
      : null,
  }))
})

const unassignedColumns = computed(() => {
  return columns.value.filter((col) => !assignedFields.value.has(col.name))
})

const allConfigurableColumns = computed(() => columns.value)

const canNext = computed(() => {
  if (step.value === 0) return !!form.value.datasource_id && !!form.value.source_table && !!form.value.name
  if (step.value === 1) return form.value.dimensions_config.length > 0 || form.value.measures_config.length > 0
  return true
})

// === Methods ===
function getSourceLabel(type: string): string {
  const labels: Record<string, string> = {
    mysql: 'MySQL', clickhouse: 'ClickHouse', starrocks: 'StarRocks',
    postgresql: 'PostgreSQL', excel: 'Excel', csv: 'CSV',
    api: 'API接口', kafka: 'Kafka', redis: 'Redis',
  }
  return labels[type] || type
}

function formatRows(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}

async function onDatasourceChange() {
  form.value.source_table = ''
  form.value.name = ''
  tables.value = []
  columns.value = []
  if (!form.value.datasource_id) return
  step0Loading.value = true
  try {
    const res = await datasourceAPI.tables(form.value.datasource_id)
    tables.value = res.data.tables
  } catch {
    ElMessage.error('无法加载表列表')
  } finally {
    step0Loading.value = false
  }
}

async function selectTable(t: { name: string; comment: string }) {
  form.value.source_table = t.name
  if (!form.value.name) {
    form.value.name = t.comment || t.name
  }
  // Load columns
  try {
    const res = await datasourceAPI.columns(form.value.datasource_id!, t.name)
    columns.value = res.data.columns
    form.value.fields_config = res.data.columns.map((c) => ({
      name: c.name,
      type: c.type,
      original_type: c.original_type,
      comment: c.comment,
    }))
  } catch {
    ElMessage.error('无法加载字段信息')
  }
}

function autoAssignField(col: { name: string; type: string }) {
  if (col.type === 'number') {
    // Assign as measure with SUM aggregation
    if (!form.value.measures_config.find((m) => m.name === col.name)) {
      form.value.measures_config.push({
        name: col.name,
        type: col.type,
        alias: col.name,
        aggregation: 'SUM',
      })
    }
  } else {
    // Assign as dimension
    if (!form.value.dimensions_config.find((d) => d.name === col.name)) {
      form.value.dimensions_config.push({
        name: col.name,
        type: col.type,
        alias: col.name,
        sub_dimensions: [],
      })
    }
  }
}

function unassignField(col: { name: string; type: string; assigned: string | null }) {
  if (col.assigned === 'dimension') {
    const idx = form.value.dimensions_config.findIndex((d) => d.name === col.name)
    if (idx >= 0) form.value.dimensions_config.splice(idx, 1)
  } else if (col.assigned === 'measure') {
    const idx = form.value.measures_config.findIndex((m) => m.name === col.name)
    if (idx >= 0) form.value.measures_config.splice(idx, 1)
  }
}

function removeDimension(idx: number) {
  form.value.dimensions_config.splice(idx, 1)
}

function removeMeasure(idx: number) {
  form.value.measures_config.splice(idx, 1)
}

function addSubDimension(dimIdx: number, fieldName: string) {
  if (!fieldName) return
  const dim = form.value.dimensions_config[dimIdx]
  if (!dim.sub_dimensions) dim.sub_dimensions = []
  if (!dim.sub_dimensions.find((s: any) => s.name === fieldName)) {
    dim.sub_dimensions.push({ name: fieldName, alias: fieldName })
  }
  newSubDim.value[dimIdx] = ''
}

function removeSubDimension(dimIdx: number, subIdx: number) {
  form.value.dimensions_config[dimIdx].sub_dimensions.splice(subIdx, 1)
}

function addDrillGroup() {
  form.value.drill_down_config.push({
    name: '',
    levels: [],
  })
}

function addDrillLevel(drillIdx: number, fieldName: string) {
  if (!fieldName) return
  const drill = form.value.drill_down_config[drillIdx]
  if (!drill.levels.includes(fieldName)) {
    drill.levels.push(fieldName)
  }
  newDrillLevel.value[drillIdx] = ''
}

function removeDrillLevel(drillIdx: number, levelIdx: number) {
  form.value.drill_down_config[drillIdx].levels.splice(levelIdx, 1)
}

function removeDrill(idx: number) {
  form.value.drill_down_config.splice(idx, 1)
}

function addFilterField(fieldName: string) {
  if (!fieldName) return
  if (!form.value.filter_fields.find((f) => f.field === fieldName)) {
    const col = columns.value.find((c) => c.name === fieldName)
    form.value.filter_fields.push({
      name: fieldName,
      field: fieldName,
      type: col?.type === 'date' ? 'date_range' : 'dropdown',
      alias: fieldName,
    })
  }
  newFilterField.value = ''
}

function removeFilter(idx: number) {
  form.value.filter_fields.splice(idx, 1)
}

async function handleCreate() {
  creating.value = true
  try {
    await datasetAPI.create({
      name: form.value.name,
      description: `从 ${form.value.source_table} 表创建`,
      dataset_type: 'table',
      datasource_id: form.value.datasource_id,
      source_table: form.value.source_table,
      fields_config: form.value.fields_config,
      dimensions_config: form.value.dimensions_config,
      measures_config: form.value.measures_config,
      drill_down_config: form.value.drill_down_config,
      filter_fields: form.value.filter_fields,
    })
    ElMessage.success('数据集创建成功！')
    emit('created')
    visible.value = false
  } catch {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

function handleCancel() {
  visible.value = false
}

// Reset form on dialog close
watch(visible, (v) => {
  if (!v) {
    step.value = 0
    form.value = {
      name: '',
      datasource_id: null,
      source_table: '',
      fields_config: [],
      dimensions_config: [],
      measures_config: [],
      drill_down_config: [],
      filter_fields: [],
    }
    tables.value = []
    columns.value = []
    newSubDim.value = {}
    newDrillLevel.value = {}
    newFilterField.value = ''
  }
})
</script>

<style scoped>
.step-content {
  min-height: 300px;
}

.step-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.step-desc {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.form-group {
  flex: 1;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.full-width {
  width: 100%;
}

.ds-type-tag {
  font-size: 11px;
  color: var(--text-light);
  margin-left: 8px;
}

.loading-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--text-secondary);
}

.table-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
}

.table-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.15s;
  border-bottom: 1px solid var(--border-light);
  position: relative;
}
.table-item:last-child { border-bottom: none; }
.table-item:hover { background: #F8FAFC; }
.table-item.selected {
  background: #EEF2FF;
  border-left: 3px solid #4F46E5;
}

.table-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #F1F5F9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748B;
}

.table-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.table-name {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}
.table-comment {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 2px;
}

.check-icon {
  position: absolute;
  right: 16px;
}

/* Field chips */
.field-section {
  margin-bottom: 20px;
}

.field-section h4 {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--text-secondary);
}

.field-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.field-type-badge {
  font-size: 10px;
  opacity: 0.7;
  margin-left: 4px;
}

/* Config columns */
.config-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.config-panel {
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
}

.dimension-header { background: #F0FDF4; color: #16A34A; }
.measure-header { background: #EFF6FF; color: #2563EB; }

.panel-body {
  padding: 10px;
  max-height: 280px;
  overflow-y: auto;
}

.config-item {
  margin-bottom: 8px;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
  background: #FAFAFA;
  border-radius: 6px;
}

.drag-handle {
  color: #CBD5E1;
  cursor: grab;
}

.item-name {
  font-size: 13px;
  font-weight: 500;
  min-width: 80px;
}

.item-type-tag {
  font-size: 10px;
}

.alias-input {
  width: 80px;
}

.agg-select {
  width: 110px;
}

.sub-dims {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px 4px 28px;
  flex-wrap: wrap;
}

.sub-label {
  font-size: 11px;
  color: var(--text-light);
}

.add-sub {
  padding: 4px 8px 4px 28px;
}

.add-sub .el-select,
.add-filter-select {
  width: 160px;
}

/* Drill down */
.config-section {
  margin-bottom: 28px;
}

.config-section h4 {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.section-desc {
  font-size: 12px;
  color: var(--text-light);
  margin-bottom: 12px;
}

.drill-item {
  padding: 12px;
  margin-bottom: 10px;
}

.drill-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.drill-name-input {
  width: 200px;
}

.drill-levels {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  padding-left: 4px;
}

.drill-level-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.level-tag {
  font-size: 12px;
}

.filter-item {
  padding: 10px 12px;
  margin-bottom: 8px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-field-label {
  font-weight: 500;
  font-size: 13px;
  min-width: 80px;
}

.filter-type-select {
  width: 130px;
}

.add-btn {
  margin-top: 8px;
}

.card {
  background: #FAFAFA;
  border: 1px solid var(--border);
  border-radius: 8px;
}
</style>
