<template>
  <div class="data-mgmt-page page-container">
    <div class="page-header">
      <div>
        <h2>数据准备</h2>
        <p class="page-desc">管理数据源连接和数据集</p>
      </div>
      <div class="header-actions">
        <el-dropdown trigger="click" @command="handleCreateDS">
          <el-button type="primary">
            <el-icon><Plus /></el-icon> 新建数据源
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="mysql">MySQL</el-dropdown-item>
              <el-dropdown-item command="clickhouse">ClickHouse</el-dropdown-item>
              <el-dropdown-item command="postgresql">PostgreSQL</el-dropdown-item>
              <el-dropdown-item command="api">API接口</el-dropdown-item>
              <el-dropdown-item command="kafka">Kafka</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon> 上传文件
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="数据源" name="datasources">
        <div class="source-grid">
          <div class="source-card card" v-for="ds in dataStore.datasources" :key="ds.id">
            <div class="source-icon" :class="ds.source_type">
              <el-icon :size="28"><component :is="getSourceIcon(ds.source_type)" /></el-icon>
            </div>
            <div class="source-info">
              <h4>{{ ds.name }}</h4>
              <p>{{ ds.description || getSourceLabel(ds.source_type) }}</p>
              <div class="source-meta">
                <el-tag size="small" :type="ds.is_active ? 'success' : 'info'">
                  {{ ds.is_active ? '已连接' : '已断开' }}
                </el-tag>
                <span class="source-mode">{{ ds.connection_mode === 'direct' ? '直连' : '缓存' }}</span>
              </div>
            </div>
            <div class="source-actions">
              <el-tooltip content="测试连接" placement="top">
                <el-button text @click="testConnection(ds)">
                  <el-icon><Connection /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-button text @click="editDatasource(ds)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button text type="danger" @click="deleteDatasource(ds)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </div>
        <el-empty v-if="dataStore.datasources.length === 0" description="暂无数据源" :image-size="80" />
      </el-tab-pane>

      <el-tab-pane label="数据集" name="datasets">
        <div class="dataset-grid">
          <div class="dataset-card card" v-for="ds in dataStore.datasets" :key="ds.id">
            <div class="ds-header">
              <span class="ds-type">{{ getDatasetTypeLabel(ds.dataset_type) }}</span>
              <span class="ds-count">{{ ds.row_count }} 行</span>
            </div>
            <h4>{{ ds.name }}</h4>
            <p>{{ ds.description || ds.source_table || '自定义数据集' }}</p>
            <div class="ds-fields">
              <el-tag
                v-for="f in (ds.fields_config || []).slice(0, 5)"
                :key="f.name"
                size="small"
                :type="f.type === 'number' ? 'primary' : f.type === 'date' ? 'warning' : 'info'"
              >
                {{ f.name }}
              </el-tag>
              <el-tag v-if="(ds.fields_config?.length || 0) > 5" size="small">
                +{{ (ds.fields_config?.length || 0) - 5 }}
              </el-tag>
            </div>
            <div class="ds-footer">
              <span class="ds-date">{{ formatDate(ds.updated_at) }}</span>
              <div class="ds-actions">
                <el-button text size="small" @click="previewDataset(ds)">
                  <el-icon><View /></el-icon> 预览
                </el-button>
                <el-button text size="small" type="danger" @click="deleteDataset(ds)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-if="dataStore.datasets.length === 0" description="暂无数据集" :image-size="80" />
      </el-tab-pane>
    </el-tabs>

    <!-- Upload Dialog -->
    <el-dialog v-model="showUploadDialog" title="上传文件" width="480px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".csv,.xlsx,.xls,.txt,.json"
        :limit="1"
      >
        <el-icon :size="48" color="#CBD5E1"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">
            支持 CSV、Excel (xlsx/xls)、TXT、JSON 格式，最大 100MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="uploadFile">上传</el-button>
      </template>
    </el-dialog>

    <!-- Dataset Preview Dialog -->
    <el-dialog v-model="showPreviewDialog" title="数据预览" width="80%" :fullscreen="false">
      <el-table :data="previewData" border stripe max-height="500" size="small" v-if="previewFields.length > 0">
        <el-table-column
          v-for="f in previewFields"
          :key="f.name"
          :prop="f.name"
          :label="f.name"
          :width="f.type === 'number' ? 120 : 150"
          :align="f.type === 'number' ? 'right' : 'left'"
        />
      </el-table>
      <el-empty v-else description="暂无数据" :image-size="60" />
    </el-dialog>

    <!-- New Datasource Dialog -->
    <el-dialog v-model="showNewDSDialog" :title="'新建 ' + newDSTypeLabel + ' 数据源'" width="520px">
      <el-form :model="newDSForm" label-position="top">
        <el-form-item label="数据源名称" required>
          <el-input v-model="newDSForm.name" placeholder="输入数据源名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newDSForm.description" />
        </el-form-item>
        <el-form-item label="连接模式">
          <el-radio-group v-model="newDSForm.connection_mode">
            <el-radio value="direct">直连模式（实时查询）</el-radio>
            <el-radio value="local_cache">本地缓存（Doris引擎）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="!isFileType" label="主机地址">
          <el-input v-model="newDSForm.config.host" placeholder="localhost" />
        </el-form-item>
        <el-form-item v-if="!isFileType" label="端口">
          <el-input-number v-model="newDSForm.config.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item v-if="!isFileType" label="数据库名">
          <el-input v-model="newDSForm.config.database" placeholder="database" />
        </el-form-item>
        <el-form-item v-if="!isFileType" label="用户名">
          <el-input v-model="newDSForm.config.username" />
        </el-form-item>
        <el-form-item v-if="!isFileType" label="密码">
          <el-input v-model="newDSForm.config.password" type="password" show-password />
        </el-form-item>
        <el-form-item v-if="newDSForm.source_type === 'api'" label="API URL">
          <el-input v-model="newDSForm.config.url" placeholder="https://api.example.com/data" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNewDSDialog = false">取消</el-button>
        <el-button type="primary" :loading="creatingDS" @click="createDatasource">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import { datasourceAPI, datasetAPI } from '@/api/endpoints'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { DataSource, Dataset } from '@/types'

const dataStore = useDataStore()
const activeTab = ref('datasources')
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const showNewDSDialog = ref(false)
const uploading = ref(false)
const creatingDS = ref(false)
const previewData = ref<any[]>([])
const previewFields = ref<any[]>([])

let selectedFile: File | null = null

// New datasource
const newDSType = ref('mysql')
const newDSTypeLabel = computed(() => getSourceLabel(newDSType.value))
const isFileType = computed(() => ['excel', 'csv', 'txt'].includes(newDSType.value))

const newDSForm = ref({
  name: '',
  description: '',
  source_type: 'mysql',
  connection_mode: 'direct',
  config: {
    host: 'localhost',
    port: 3306,
    database: '',
    username: 'root',
    password: '',
    url: '',
  },
})

onMounted(() => {
  dataStore.loadDatasources()
  dataStore.loadDatasets()
})

function getSourceLabel(type: string): string {
  const labels: Record<string, string> = {
    mysql: 'MySQL', clickhouse: 'ClickHouse', starrocks: 'StarRocks',
    postgresql: 'PostgreSQL', excel: 'Excel', csv: 'CSV', txt: 'TXT',
    api: 'API接口', kafka: 'Kafka', redis: 'Redis',
  }
  return labels[type] || type
}

function getSourceIcon(type: string): string {
  const icons: Record<string, string> = {
    mysql: 'Coin', clickhouse: 'DataBoard', starrocks: 'DataAnalysis',
    postgresql: 'Connection', excel: 'Document', csv: 'DocumentCopy',
    api: 'Link', kafka: 'Message', redis: 'Clock',
  }
  return icons[type] || 'Connection'
}

function getDatasetTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    table: '数据库表', sql: 'SQL查询', file: '文件上传',
    cross_source: '跨源关联', api: 'API数据集',
  }
  return labels[type] || type
}

function formatDate(d?: string): string {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', year: 'numeric' })
}

function handleCreateDS(type: string) {
  newDSType.value = type
  newDSForm.value = {
    name: getSourceLabel(type),
    description: '',
    source_type: type,
    connection_mode: 'direct',
    config: {
      host: 'localhost',
      port: type === 'clickhouse' ? 8123 : type === 'postgresql' ? 5432 : 3306,
      database: '',
      username: 'root',
      password: '',
      url: '',
    },
  }
  showNewDSDialog.value = true
}

async function createDatasource() {
  if (!newDSForm.value.name.trim()) {
    ElMessage.warning('请输入数据源名称')
    return
  }
  creatingDS.value = true
  try {
    await datasourceAPI.create({
      ...newDSForm.value,
      source_type: newDSType.value,
    })
    ElMessage.success('创建成功')
    showNewDSDialog.value = false
    dataStore.loadDatasources()
  } catch {
    ElMessage.error('创建失败')
  } finally {
    creatingDS.value = false
  }
}

function handleFileChange(file: any) {
  selectedFile = file.raw
}

async function uploadFile() {
  if (!selectedFile) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    await datasetAPI.upload(selectedFile)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    selectedFile = null
    activeTab.value = 'datasets'
    dataStore.loadDatasets()
  } catch {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

async function testConnection(ds: DataSource) {
  try {
    await datasourceAPI.test(ds.id)
    ElMessage.success('连接成功！')
  } catch {
    ElMessage.error('连接失败')
  }
}

function editDatasource(ds: DataSource) {
  ElMessage.info('编辑功能开发中')
}

function deleteDatasource(ds: DataSource) {
  ElMessageBox.confirm(`确定删除数据源 "${ds.name}"？`, '警告', {
    confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    await datasourceAPI.delete(ds.id)
    ElMessage.success('已删除')
    dataStore.loadDatasources()
  }).catch(() => {})
}

async function previewDataset(ds: Dataset) {
  try {
    const res = await datasetAPI.query(ds.id, {
      dimensions: [],
      measures: [],
      limit: 100,
    })
    previewData.value = res.data.data || []
    previewFields.value = ds.fields_config || []
    showPreviewDialog.value = true
  } catch {
    ElMessage.warning('无法预览此数据集')
  }
}

function deleteDataset(ds: Dataset) {
  ElMessageBox.confirm(`确定删除数据集 "${ds.name}"？`, '警告', {
    confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    await datasetAPI.delete(ds.id)
    ElMessage.success('已删除')
    dataStore.loadDatasets()
  }).catch(() => {})
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 4px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.source-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.source-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
}

.source-icon.mysql { color: #4479A1; }
.source-icon.clickhouse { color: #FCC624; }
.source-icon.starrocks { color: #2080F0; }
.source-icon.api { color: #10B981; }

.source-info {
  flex: 1;
}

.source-info h4 {
  font-size: 15px;
  font-weight: 600;
}

.source-info p {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 4px 0 8px;
}

.source-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.source-mode {
  font-size: 11px;
  color: var(--text-light);
}

.source-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}
.source-card:hover .source-actions {
  opacity: 1;
}

.dataset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.dataset-card {
  padding: 20px;
}

.ds-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.ds-type {
  background: #EEF2FF;
  color: var(--primary);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.ds-count {
  font-size: 12px;
  color: var(--text-light);
}

.dataset-card h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.dataset-card > p {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.ds-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 12px;
}

.ds-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-light);
  padding-top: 12px;
}

.ds-date {
  font-size: 12px;
  color: var(--text-light);
}

.ds-actions {
  display: flex;
  gap: 4px;
}
</style>
