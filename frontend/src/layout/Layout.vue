<template>
  <el-container class="layout-wrapper">
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '220px'" class="layout-aside">
      <div class="logo-wrap">
        <img src="/favicon.svg" class="logo-icon" alt="logo" />
        <span v-show="!appStore.sidebarCollapsed" class="logo-title">捐赠管理系统</span>
      </div>

      <div class="menu-scroll">
        <el-menu
          :default-active="$route.path"
          :collapse="appStore.sidebarCollapsed"
          background-color="#001529"
          text-color="#ffffffa6"
          active-text-color="#ffffff"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>数据概览</template>
          </el-menu-item>

          <el-menu-item index="/donation">
            <el-icon><List /></el-icon>
            <template #title>捐赠查询</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/donor">
            <el-icon><User /></el-icon>
            <template #title>捐赠人管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/target">
            <el-icon><Flag /></el-icon>
            <template #title>捐赠目标</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission('admin')" index="/stats">
            <el-icon><TrendCharts /></el-icon>
            <template #title>统计报表</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/fund-usage">
            <el-icon><Money /></el-icon>
            <template #title>基金使用管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/invoice-requests">
            <el-icon><Tickets /></el-icon>
            <template #title>开票申请管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/imports/donations">
            <el-icon><UploadFilled /></el-icon>
            <template #title>捐赠数据导入</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/news">
            <el-icon><MessageBox /></el-icon>
            <template #title>新闻推文管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/notices">
            <el-icon><Bell /></el-icon>
            <template #title>公告管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/members">
            <el-icon><UserFilled /></el-icon>
            <template #title>会员管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/member-suggestions">
            <el-icon><ChatDotRound /></el-icon>
            <template #title>意见建议管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/site-contents">
            <el-icon><Memo /></el-icon>
            <template #title>站点内容配置</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/park-links">
            <el-icon><Link /></el-icon>
            <template #title>产业园链接管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission(['admin', 'operator'])" index="/project-links">
            <el-icon><Picture /></el-icon>
            <template #title>公益项目链接管理</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission('admin')" index="/log">
            <el-icon><Document /></el-icon>
            <template #title>操作日志</template>
          </el-menu-item>

          <el-menu-item v-if="hasPermission('admin')" index="/admin/users">
            <el-icon><Setting /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="appStore.toggleSidebar()">
            <component :is="appStore.sidebarCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ userStore.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { hasPermission } from '@/utils/permission'

const appStore = useAppStore()
const userStore = useUserStore()
const router = useRouter()

async function handleCommand(cmd) {
  if (cmd === 'logout') {
    await userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-wrapper {
  height: 100vh;
}

.layout-aside {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.logo-wrap {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid #0d2136;
}

.logo-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-title {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.el-menu {
  border-right: none;
  min-height: 100%;
}

.menu-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.menu-scroll::-webkit-scrollbar {
  width: 8px;
}

.menu-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.18);
  border-radius: 999px;
}

.menu-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.layout-header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #595959;
}

.collapse-btn:hover {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}

.username {
  font-size: 14px;
}

.layout-main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
