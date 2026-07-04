import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: () => import('@/layout/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据概览', icon: 'DataAnalysis' },
      },
      {
        path: 'donation',
        name: 'DonationList',
        component: () => import('@/views/donation/DonationList.vue'),
        meta: { title: '捐赠查询', icon: 'List', roles: ['admin', 'operator', 'reviewer', 'viewer'] },
      },
      {
        path: 'donation/create',
        name: 'DonationCreate',
        component: () => import('@/views/donation/DonationForm.vue'),
        meta: { title: '新增捐赠', roles: ['admin', 'operator'] },
      },
      {
        path: 'donation/edit/:id',
        name: 'DonationEdit',
        component: () => import('@/views/donation/DonationForm.vue'),
        meta: { title: '编辑捐赠', roles: ['admin', 'operator'] },
      },
      {
        path: 'donation/:id',
        name: 'DonationDetail',
        component: () => import('@/views/donation/DonationDetail.vue'),
        meta: { title: '捐赠详情', roles: ['admin', 'operator', 'reviewer', 'viewer'] },
      },
      {
        path: 'donor',
        name: 'DonorList',
        component: () => import('@/views/donor/DonorList.vue'),
        meta: { title: '捐赠人管理', icon: 'User', roles: ['admin', 'operator'] },
      },
      {
        path: 'target',
        name: 'TargetList',
        component: () => import('@/views/target/TargetList.vue'),
        meta: { title: '捐赠目标', icon: 'Flag', roles: ['admin', 'operator'] },
      },
      {
        path: 'stats',
        name: 'Statistics',
        component: () => import('@/views/stats/Statistics.vue'),
        meta: { title: '统计报表', icon: 'TrendCharts', roles: ['admin'] },
      },
      {
        path: 'fund-usage',
        name: 'FundUsageManage',
        component: () => import('@/views/fund/FundUsageManage.vue'),
        meta: { title: '基金使用管理', icon: 'Money', roles: ['admin', 'operator'] },
      },
      {
        path: 'invoice-requests',
        name: 'InvoiceRequestManage',
        component: () => import('@/views/invoice/InvoiceRequestManage.vue'),
        meta: { title: '开票申请管理', icon: 'Tickets', roles: ['admin', 'operator'] },
      },
      {
        path: 'imports/donations',
        name: 'DonationImport',
        component: () => import('@/views/import/DonationImport.vue'),
        meta: { title: '捐赠数据导入', icon: 'UploadFilled', roles: ['admin', 'operator'] },
      },
      {
        path: 'news',
        name: 'NewsManage',
        component: () => import('@/views/news/NewsManage.vue'),
        meta: { title: '新闻推文管理', icon: 'MessageBox', roles: ['admin', 'operator'] },
      },
      {
        path: 'notices',
        name: 'NoticeManage',
        component: () => import('@/views/notice/NoticeManage.vue'),
        meta: { title: '公告管理', icon: 'Bell', roles: ['admin', 'operator'] },
      },
      {
        path: 'members',
        name: 'MemberManage',
        component: () => import('@/views/member/MemberManage.vue'),
        meta: { title: '会员管理', icon: 'UserFilled', roles: ['admin', 'operator'] },
      },
      {
        path: 'member-suggestions',
        name: 'MemberSuggestionManage',
        component: () => import('@/views/member/MemberSuggestionManage.vue'),
        meta: { title: '意见建议管理', icon: 'ChatDotRound', roles: ['admin', 'operator'] },
      },
      {
        path: 'site-contents',
        name: 'SiteContentManage',
        component: () => import('@/views/site/SiteContentManage.vue'),
        meta: { title: '站点内容配置', icon: 'Memo', roles: ['admin', 'operator'] },
      },
      {
        path: 'park-links',
        name: 'ParkLinkManage',
        component: () => import('@/views/park/ParkLinkManage.vue'),
        meta: { title: '产业园链接管理', icon: 'Link', roles: ['admin', 'operator'] },
      },
      {
        path: 'project-links',
        name: 'ProjectLinkManage',
        component: () => import('@/views/project/ProjectLinkManage.vue'),
        meta: { title: '公益项目链接管理', icon: 'Picture', roles: ['admin', 'operator'] },
      },
      {
        path: 'log',
        name: 'LogList',
        component: () => import('@/views/log/LogList.vue'),
        meta: { title: '操作日志', icon: 'Document', roles: ['admin'] },
      },
      {
        path: 'admin/users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理', icon: 'Setting', roles: ['admin'] },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '首页'} - 基金会捐赠管理系统`

  const userStore = useUserStore()
  const token = userStore.token

  if (to.meta.public) {
    next()
    return
  }

  if (!token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  const roles = to.meta.roles
  if (roles && !roles.includes(userStore.role)) {
    ElMessage.error('无权限访问该页面')
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
