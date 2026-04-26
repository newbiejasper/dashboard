<template>
  <div class="dashboard-list-page page-container">
    <div class="page-header">
      <div>
        <h2>仪表板</h2>
        <p class="page-desc">管理您的数据仪表板和可视化大屏</p>
      </div>
      <el-button type="primary" size="large" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建仪表板
      </el-button>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="dash-tabs">
      <el-tab-pane label="全部仪表板" name="all" />
      <el-tab-pane label="大屏" name="screens" />
    </el-tabs>

    <!-- Dashboard grid -->
    <div class="dash-grid" v-if="dashboards.length > 0">
      <div
        class="dash-card card"
        v-for="dash in dashboards"
        :key="dash.id"
      >
        <div class="dash-preview" :style="{ background: dash.background_config?.color || 'linear-gradient(135deg, #667eea, #764ba2)' }">
          <span class="dash-type">{{ dash.dashboard_type === 'screen' ? '大屏' : '仪表板' }}</span>
          <div class="dash-actions-top">
            <el-tooltip content="预览" placement="top">
              <el-button circle size="small" @click.stop="$router.push(`/dashboard/${dash.id}/view`)">
                <el-icon><View /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="编辑" placement="top">
              <el-button circle size="small" type="primary" @click.stop="$router.push(`/dashboard/${dash.id}/edit`)">
                <el-icon><Edit /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
        <div class="dash-info">
          <h4>{{ dash.name }}</h4>
          <p>{{ dash.description || '暂无描述' }}</p>
          <div class="dash-meta">
            <span>
              <el-icon size="14"><View /></el-icon>
              {{ dash.visit_count || 0 }}
            </span>
            <span>{{ formatDate(dash.updated_at) }}</span>
          </div>
        </div>
        <div class="dash-footer">
          <el-tooltip content="分享" placement="top">
            <el-button text @click.stop="shareDashboard(dash)">
              <el-icon><Share /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="设置" placement="top">
            <el-button text @click.stop="editDashboard(dash)">
              <el-icon><Setting /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button text type="danger" @click.stop="confirmDelete(dash)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无仪表板，点击右上角创建" :image-size="120" />

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="新建仪表板" width="480px">
      <el-form :model="form" label-position="top">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="输入仪表板名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.dashboard_type">
            <el-radio value="dashboard">仪表板</el-radio>
            <el-radio value="screen">大屏</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
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
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardAPI } from '@/api/endpoints'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Dashboard } from '@/types'

const router = useRouter()
const activeTab = ref('all')
const dashboards = ref<Dashboard[]>([])
const showCreateDialog = ref(false)
const creating = ref(false)
const form = ref({ name: '', description: '', dashboard_type: 'dashboard' as const })

async function loadDashboards() {
  const type = activeTab.value === 'screens' ? 'screen' : 'dashboard'
  const res = await dashboardAPI.list(type)
  dashboards.value = res.data
}

watch(activeTab, () => loadDashboards())
onMounted(loadDashboards)

function formatDate(d?: string) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

async function handleCreate() {
  if (!form.value.name.trim()) { ElMessage.warning('请输入名称'); return }
  creating.value = true
  try {
    const res = await dashboardAPI.create(form.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    router.push(`/dashboard/${res.data.id}/edit`)
  } catch { ElMessage.error('创建失败')
  } finally { creating.value = false }
}

function shareDashboard(dash: Dashboard) {
  dashboardAPI.share(dash.id).then((res) => {
    ElMessageBox.alert(
      `分享链接：${window.location.origin}/share/${res.data.share_token}\n嵌入链接：${window.location.origin}/embed/${res.data.embed_token}`,
      '分享仪表板'
    )
  })
}

function editDashboard(dash: Dashboard) {
  // Navigation to editor
  router.push(`/dashboard/${dash.id}/edit`)
}

function confirmDelete(dash: Dashboard) {
  ElMessageBox.confirm(`确定删除"${dash.name}"？删除后不可恢复。`, '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await dashboardAPI.delete(dash.id)
    ElMessage.success('已删除')
    loadDashboards()
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

.dash-tabs {
  margin-bottom: 20px;
}

.dash-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.dash-card {
  overflow: hidden;
  transition: all 0.2s;
}
.dash-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.dash-preview {
  height: 160px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 12px;
  position: relative;
}

.dash-type {
  background: rgba(0, 0, 0, 0.4);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
}

.dash-actions-top {
  display: none;
  gap: 4px;
}
.dash-card:hover .dash-actions-top {
  display: flex;
}

.dash-info {
  padding: 16px;
}

.dash-info h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.dash-info p {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.dash-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-light);
}

.dash-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dash-footer {
  border-top: 1px solid var(--border-light);
  padding: 8px 16px;
  display: flex;
  justify-content: flex-end;
  gap: 4px;
}
</style>
