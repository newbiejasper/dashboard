<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-left">
        <div class="brand">
          <div class="brand-icon">D</div>
          <h1>DDYL</h1>
          <p class="slogan">人人可用的数据可视化神器</p>
        </div>
        <div class="features">
          <div class="feature-item" v-for="f in features" :key="f.title">
            <el-icon :size="24" :color="f.color">{{ f.icon }}</el-icon>
            <div>
              <h4>{{ f.title }}</h4>
              <p>{{ f.desc }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="login-right">
        <el-card class="login-card" shadow="never">
          <h2>{{ isRegister ? '创建账号' : '欢迎回来' }}</h2>
          <p class="login-desc">{{ isRegister ? '注册后即可开始数据可视化之旅' : '登录后继续使用DDYL平台' }}</p>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            size="large"
            @submit.prevent="handleSubmit"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" />
            </el-form-item>

            <el-form-item v-if="isRegister" label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱（选填）" />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" native-type="submit" :loading="loading" class="submit-btn">
                {{ isRegister ? '注册' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="login-switch">
            <span>{{ isRegister ? '已有账号？' : '没有账号？' }}</span>
            <el-button link @click="isRegister = !isRegister">
              {{ isRegister ? '去登录' : '立即注册' }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const isRegister = ref(false)

const form = reactive({
  username: 'admin',
  password: 'admin123',
  email: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
}

const features = [
  { title: '零代码拖拽', desc: '无需SQL/开发能力', color: '#4F46E5', icon: 'Pointer' },
  { title: '30+图表类型', desc: 'ECharts/AntV 专业可视化', color: '#10B981', icon: 'DataLine' },
  { title: '多源数据融合', desc: '支持20+种数据源连接', color: '#F59E0B', icon: 'Connection' },
  { title: '实时大屏', desc: '秒级响应，TB级数据', color: '#EF4444', icon: 'Monitor' },
]

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (isRegister.value) {
      await userStore.login(form.username, form.password)
      ElMessage.success('注册成功！')
    } else {
      await userStore.login(form.username, form.password)
      ElMessage.success('登录成功！')
    }
    router.push('/workbench')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 50%, #C7D2FE 100%);
}

.login-container {
  display: flex;
  width: 900px;
  max-width: 95vw;
  min-height: 520px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.login-left {
  flex: 1;
  padding: 48px;
  background: linear-gradient(135deg, #1E293B, #334155);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 16px;
}

.brand h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 4px;
}

.slogan {
  color: var(--text-sidebar);
  font-size: 16px;
  margin-bottom: 40px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.feature-item h4 {
  font-size: 14px;
  font-weight: 600;
}

.feature-item p {
  font-size: 12px;
  color: var(--text-sidebar);
}

.login-right {
  width: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.login-card {
  width: 100%;
  border: none;
}

.login-card h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.login-desc {
  color: var(--text-secondary);
  margin-bottom: 24px;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
}

.login-switch {
  text-align: center;
  margin-top: 16px;
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
