<template>
  <div class="workbench-page page-container">
    <!-- Stats Overview -->
    <div class="stats-row">
      <div class="stat-card" v-for="stat in stats" :key="stat.key">
        <el-icon :size="24" :color="stat.color">
          <component :is="stat.icon" />
        </el-icon>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h3 class="section-title">快速创建</h3>
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="createDashboard">
          <el-icon><Plus /></el-icon>
          新建仪表板
        </el-button>
        <el-button size="large" @click="createDatasource">
          <el-icon><Connection /></el-icon>
          添加数据源
        </el-button>
        <el-button size="large" @click="uploadDataset">
          <el-icon><Upload /></el-icon>
          上传数据集
        </el-button>
      </div>
    </div>

    <!-- Template Market Preview -->
    <div class="section">
      <div class="section-header">
        <h3 class="section-title">热门模板</h3>
        <el-button text @click="$router.push('/market')">
          查看更多 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="template-grid">
        <div
          class="template-card card"
          v-for="tpl in templates"
          :key="tpl.id"
          @click="useTemplate(tpl.id)"
        >
          <div class="tpl-preview" :style="{ background: tpl.thumbnail || 'linear-gradient(135deg, #667eea, #764ba2)' }">
            <span class="tpl-badge">{{ tpl.template_category }}</span>
          </div>
          <div class="tpl-info">
            <h4>{{ tpl.name }}</h4>
            <p>{{ tpl.description?.slice(0, 30) || '行业模板' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Dashboards -->
    <div class="section">
      <div class="section-header">
        <h3 class="section-title">最近访问</h3>
        <el-button text @click="$router.push('/dashboard')">
          查看全部 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="recent-list card">
        <div
          class="recent-item"
          v-for="dash in recentDashboards"
          :key="dash.id"
          @click="$router.push(`/dashboard/${dash.id}/edit`)"
        >
          <el-icon size="20" color="var(--primary)"><Monitor /></el-icon>
          <div class="recent-info">
            <span class="recent-name">{{ dash.name }}</span>
            <span class="recent-time">{{ formatDate(dash.updated_at) }}</span>
          </div>
          <el-icon><ArrowRight /></el-icon>
        </div>
        <el-empty v-if="recentDashboards.length === 0" description="暂无仪表板" :image-size="60" />
      </div>
    </div>

    <!-- New Dashboard Dialog -->
    <el-dialog v-model="showCreateDialog" title="新建仪表板" width="480px">
      <el-form :model="newDashboard" label-position="top">
        <el-form-item label="名称" required>
          <el-input v-model="newDashboard.name" placeholder="输入仪表板名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="newDashboard.dashboard_type">
            <el-radio value="dashboard">仪表板</el-radio>
            <el-radio value="screen">大屏</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="newDashboard.description"
            type="textarea"
            :rows="3"
            placeholder="描述此仪表板的用途"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardAPI } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import type { Dashboard, StatsResponse } from '@/types'

const router = useRouter()

const stats = ref([
  { key: 'dashboards', label: '仪表板', value: 0, icon: 'Monitor', color: '#4F46E5' },
  { key: 'screens', label: '大屏', value: 0, icon: 'DataBoard', color: '#10B981' },
  { key: 'datasources', label: '数据源', value: 0, icon: 'Connection', color: '#F59E0B' },
  { key: 'datasets', label: '数据集', value: 0, icon: 'DataAnalysis', color: '#EF4444' },
])

const recentDashboards = ref<Dashboard[]>([])
const templates = ref<Dashboard[]>([])

// Create dialog
const showCreateDialog = ref(false)
const creating = ref(false)
const newDashboard = ref({
  name: '',
  description: '',
  dashboard_type: 'dashboard' as const,
})

onMounted(async () => {
  try {
    const [statsRes, recentRes, tplRes] = await Promise.all([
      dashboardAPI.stats(),
      dashboardAPI.recent(),
      dashboardAPI.templates(),
    ])
    const s = statsRes.data
    stats.value = [
      { ...stats.value[0], value: s.dashboard_count },
      { ...stats.value[1], value: s.screen_count },
      { ...stats.value[2], value: s.datasource_count },
      { ...stats.value[3], value: s.dataset_count },
    ]
    recentDashboards.value = recentRes.data
    templates.value = tplRes.data.slice(0, 4)
  } catch (err) {
    console.error('Failed to load dashboard stats', err)
  }
})

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN')
}

function createDashboard() {
  showCreateDialog.value = true
}

async function handleCreate() {
  if (!newDashboard.value.name.trim()) {
    ElMessage.warning('请输入名称')
    return
  }
  creating.value = true
  try {
    const res = await dashboardAPI.create(newDashboard.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    router.push(`/dashboard/${res.data.id}/edit`)
  } catch {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

function createDatasource() {
  router.push('/data')
}

function uploadDataset() {
  router.push('/data')
}

function useTemplate(templateId: number) {
  dashboardAPI.useTemplate(templateId).then((res) => {
    ElMessage.success('模板应用成功')
    router.push(`/dashboard/${res.data.id}/edit`)
  }).catch(() => {
    ElMessage.error('模板应用失败')
  })
}
</script>

<style scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.2s;
}
.stat-card:hover {
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.quick-actions {
  margin-bottom: 28px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.template-card {
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s;
}
.template-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.tpl-preview {
  height: 120px;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 8px;
  position: relative;
}

.tpl-badge {
  background: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
}

.tpl-info {
  padding: 12px 16px;
}

.tpl-info h4 {
  font-size: 14px;
  font-weight: 600;
}

.tpl-info p {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.recent-list {
  padding: 0;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--border-light);
}
.recent-item:last-child {
  border-bottom: none;
}
.recent-item:hover {
  background: #F8FAFC;
}

.recent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.recent-name {
  font-weight: 500;
  color: var(--text-primary);
}

.recent-time {
  font-size: 12px;
  color: var(--text-light);
}
</style>
