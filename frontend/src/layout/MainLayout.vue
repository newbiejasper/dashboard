<template>
  <div class="main-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">D</div>
        <span class="logo-text">DDYL</span>
        <span class="logo-sub">BI Platform</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :router="true"
        class="sidebar-menu"
        background-color="#1E293B"
        text-color="#CBD5E1"
        active-text-color="#FFFFFF"
      >
        <el-menu-item index="/workbench">
          <el-icon><Odometer /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据准备</span>
        </el-menu-item>
        <el-menu-item index="/market">
          <el-icon><ShoppingBag /></el-icon>
          <span>模板市场</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="32" :src="user?.avatar">
              {{ user?.display_name?.[0] || 'U' }}
            </el-avatar>
            <div class="user-text">
              <span class="user-name">{{ user?.display_name || user?.username || '用户' }}</span>
              <span class="user-role">管理员</span>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="settings">系统设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="main-area">
      <header class="top-header">
        <div class="header-left">
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索仪表板、数据集..."
            :prefix-icon="Search"
            class="search-input"
            clearable
          />
          <el-button circle @click="refreshCurrent">
            <el-icon><Refresh /></el-icon>
          </el-button>
          <el-button circle @click="showHelp">
            <el-icon><QuestionFilled /></el-icon>
          </el-button>
        </div>
      </header>

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Search } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const searchQuery = ref('')

const user = computed(() => userStore.user)
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => (route.meta?.title as string) || 'DDYL')

onMounted(async () => {
  if (userStore.isLoggedIn && !userStore.user) {
    await userStore.fetchUser()
  }
})

function refreshCurrent() {
  router.go(0)
}

function showHelp() {
  window.open('/docs', '_blank')
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: white;
  letter-spacing: 1px;
}

.logo-sub {
  font-size: 10px;
  color: var(--text-light);
  margin-left: auto;
}

.sidebar-menu {
  flex: 1;
  border: none;
  padding: 8px;
}

.sidebar-menu .el-menu-item {
  border-radius: 8px;
  margin: 2px 0;
  height: 44px;
  line-height: 44px;
}

.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: background 0.2s;
}
.user-info:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.user-name {
  color: var(--text-sidebar);
  font-size: 13px;
  font-weight: 500;
}

.user-role {
  color: var(--text-light);
  font-size: 11px;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.top-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: white;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.header-left h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  width: 260px;
}

.content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
