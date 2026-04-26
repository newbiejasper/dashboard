<template>
  <div class="template-market page-container">
    <div class="market-header">
      <div>
        <h2>模板市场</h2>
        <p class="market-desc">{{ templates.length }}+ 行业模板，一键创建仪表板</p>
      </div>
      <el-input
        v-model="searchQuery"
        placeholder="搜索模板..."
        :prefix-icon="Search"
        class="search-input"
        clearable
      />
    </div>

    <!-- Category Tabs -->
    <el-tabs v-model="activeCategory" @tab-change="loadTemplates">
      <el-tab-pane label="全部" name="" />
      <el-tab-pane v-for="cat in categories" :key="cat.key" :label="cat.label" :name="cat.key" />
    </el-tabs>

    <!-- Template Grid -->
    <div class="template-grid" v-if="filteredTemplates.length > 0">
      <div
        class="template-card card"
        v-for="tpl in filteredTemplates"
        :key="tpl.id"
        @click="useTemplate(tpl)"
      >
        <div class="tpl-preview" :style="{ background: tpl.background_config?.color || getGradient(tpl.template_category) }">
          <div class="tpl-badges">
            <span class="tpl-cat">{{ tpl.template_category }}</span>
            <span class="tpl-type">{{ tpl.dashboard_type === 'screen' ? '大屏' : '仪表板' }}</span>
          </div>
          <div class="tpl-views-count">
            <el-icon><View /></el-icon> {{ tpl.visit_count || 0 }}
          </div>
        </div>
        <div class="tpl-info">
          <h4>{{ tpl.name }}</h4>
          <p>{{ tpl.description || '行业通用仪表板模板' }}</p>
          <div class="tpl-footer">
            <span class="tpl-creator">DDYL官方</span>
            <el-button
              size="small"
              type="primary"
              @click.stop="useTemplate(tpl)"
            >
              <el-icon><CopyDocument /></el-icon>
              使用模板
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-else description="没有匹配的模板" :image-size="100" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardAPI } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import type { Dashboard } from '@/types'

const router = useRouter()
const templates = ref<Dashboard[]>([])
const searchQuery = ref('')
const activeCategory = ref('')

const categories = [
  { key: 'manufacturing', label: '制造业' },
  { key: 'retail', label: '零售电商' },
  { key: 'finance', label: '金融风控' },
  { key: 'medical', label: '医药健康' },
  { key: 'logistics', label: '物流运输' },
  { key: 'government', label: '政务数据' },
  { key: 'education', label: '教育' },
  { key: 'energy', label: '能源' },
]

const filteredTemplates = computed(() => {
  let list = templates.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter((t) => t.name.toLowerCase().includes(q) || t.description?.toLowerCase().includes(q))
  }
  return list
})

const gradients = ['linear-gradient(135deg, #667eea, #764ba2)', 'linear-gradient(135deg, #f093fb, #f5576c)', 'linear-gradient(135deg, #4facfe, #00f2fe)', 'linear-gradient(135deg, #43e97b, #38f9d7)', 'linear-gradient(135deg, #fa709a, #fee140)', 'linear-gradient(135deg, #a18cd1, #fbc2eb)']

function getGradient(_cat?: string) {
  return gradients[Math.floor(Math.random() * gradients.length)]
}

onMounted(loadTemplates)

async function loadTemplates() {
  const res = await dashboardAPI.templates(activeCategory.value || undefined)
  templates.value = [
    ...res.data,
    // Generate sample templates for demo
    ...(res.data.length === 0 ? generateSampleTemplates() : []),
  ]
}

function generateSampleTemplates(): Dashboard[] {
  const sampleTemplates = [
    { name: '销售业绩驾驶舱', description: '销售KPI、漏斗分析、区域销售地图', category: 'retail', gradient: 'linear-gradient(135deg, #667eea, #764ba2)' },
    { name: '生产监控大屏', description: '设备OEE、产线效率、质量缺陷分析', category: 'manufacturing', gradient: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
    { name: '财务运营报表', description: '收入/支出趋势、预算执行、现金流', category: 'finance', gradient: 'linear-gradient(135deg, #f093fb, #f5576c)' },
    { name: '供应链监控', description: '库存周转、物流时效、供应商评分', category: 'logistics', gradient: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
    { name: '医药研发看板', description: '临床试验进度、专利统计、研发投入', category: 'medical', gradient: 'linear-gradient(135deg, #fa709a, #fee140)' },
    { name: '政务数据门户', description: '民生指标、政务服务效能、舆情监控', category: 'government', gradient: 'linear-gradient(135deg, #a18cd1, #fbc2eb)' },
    { name: '电商运营看板', description: 'GMV趋势、用户增长、商品销售排行', category: 'retail', gradient: 'linear-gradient(135deg, #667eea, #764ba2)' },
    { name: '零售门店驾驶舱', description: '门店排名、品类分析、会员复购', category: 'retail', gradient: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
    { name: '校园数据大屏', description: '招生统计、就业率、科研成果', category: 'education', gradient: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
    { name: '能源监控平台', description: '能耗趋势、碳排放、设备告警', category: 'energy', gradient: 'linear-gradient(135deg, #f093fb, #f5576c)' },
    { name: '金融风控大屏', description: '交易监控、风险评分、异常告警', category: 'finance', gradient: 'linear-gradient(135deg, #667eea, #764ba2)' },
    { name: '物流运输看板', description: '运输轨迹、时效分析、成本监控', category: 'logistics', gradient: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
  ]
  return sampleTemplates.map((t, i) => ({
    id: -i - 1,
    name: t.name,
    description: t.description,
    template_category: t.category,
    dashboard_type: t.category === 'manufacturing' || t.category === 'finance' ? 'screen' : 'dashboard',
    background_config: { color: t.gradient },
    visit_count: Math.floor(Math.random() * 500) + 100,
    width: 1920,
    height: 1080,
    is_template: true,
    is_published: true,
  } as any))
}

async function useTemplate(tpl: Dashboard) {
  try {
    const res = await dashboardAPI.useTemplate(tpl.id)
    ElMessage.success('模板应用成功！')
    router.push(`/dashboard/${res.data.id}/edit`)
  } catch {
    // For demo templates (negative IDs), create a new dashboard
    if (tpl.id < 0) {
      const res = await dashboardAPI.create({
        name: tpl.name,
        description: tpl.description,
        dashboard_type: tpl.dashboard_type || 'dashboard',
        background_config: tpl.background_config || {},
        width: 1920,
        height: 1080,
      })
      ElMessage.success('模板应用成功！')
      router.push(`/dashboard/${res.data.id}/edit`)
    }
  }
}
</script>

<style scoped>
.market-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.market-header h2 {
  font-size: 22px;
  font-weight: 700;
}

.market-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 4px;
}

.search-input {
  width: 280px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.template-card {
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}
.template-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.tpl-preview {
  height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px;
  position: relative;
}

.tpl-badges {
  display: flex;
  gap: 6px;
}

.tpl-cat {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  backdrop-filter: blur(4px);
}

.tpl-type {
  background: rgba(0, 0, 0, 0.3);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
}

.tpl-views-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tpl-info {
  padding: 16px;
}

.tpl-info h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.tpl-info p {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.4;
}

.tpl-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tpl-creator {
  font-size: 12px;
  color: var(--text-light);
}
</style>
