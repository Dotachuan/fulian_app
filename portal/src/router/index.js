import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/donation-query',
    name: 'DonationQuery',
    component: () => import('@/views/DonationQuery.vue'),
    meta: { title: '捐赠查询' },
  },
  {
    path: '/fund-usage',
    name: 'FundUsage',
    component: () => import('@/views/FundUsage.vue'),
    meta: { title: '基金使用查询' },
  },
  {
    path: '/invoice-request',
    name: 'InvoiceRequest',
    component: () => import('@/views/InvoiceRequest.vue'),
    meta: { title: '开票申请' },
  },
  {
    path: '/news',
    name: 'NewsList',
    component: () => import('@/views/NewsList.vue'),
    meta: { title: '最新动态' },
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

router.beforeEach((to) => {
  document.title = `${to.meta.title || '首页'} - 基金会服务平台`
})

export default router
