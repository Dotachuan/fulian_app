<template>
  <section class="home-hero">
    <div class="hero-inner">
      <p class="hero-kicker">公开透明 · 便捷查询 · 在线申请</p>
      <h1>基金会服务平台</h1>
      <p class="hero-copy">
        面向捐赠人和公众提供捐赠记录查询、基金使用公开查询、电子票据开票申请等服务。
      </p>
      <div class="hero-actions">
        <el-button type="primary" :icon="Search" @click="$router.push('/donation-query')">查询捐赠</el-button>
        <el-button :icon="Tickets" @click="$router.push('/invoice-request')">申请开票</el-button>
      </div>
    </div>
  </section>

  <section class="page home-grid" aria-label="服务入口">
    <RouterLink class="service-card" to="/donation-query">
      <el-icon><Search /></el-icon>
      <h2>捐赠查询</h2>
      <p>按捐赠人、日期或年份查询捐赠记录，并查看累计捐赠笔数和金额。</p>
    </RouterLink>

    <RouterLink class="service-card" to="/fund-usage">
      <el-icon><DataAnalysis /></el-icon>
      <h2>基金使用查询</h2>
      <p>查看主体基金和子基金的收入、支出、结余及项目明细。</p>
    </RouterLink>

    <RouterLink class="service-card" to="/invoice-request">
      <el-icon><Tickets /></el-icon>
      <h2>开票申请</h2>
      <p>在线提交开票所需信息，后台统一处理并留档导出。</p>
    </RouterLink>
  </section>

  <section class="page news-section">
    <div class="section-head">
      <div>
        <p class="section-kicker">最新动态</p>
        <h2>公众号推文</h2>
      </div>
      <el-button :icon="ArrowRight" @click="$router.push('/news')">查看更多</el-button>
    </div>

    <div v-if="newsItems.length" class="news-grid">
      <article v-for="item in newsItems" :key="item.id" class="news-card" @click="openNews(item)">
        <div v-if="item.cover_url" class="news-cover">
          <img :src="item.cover_url" :alt="item.title" />
        </div>
        <div class="news-body">
          <div class="news-meta">
            <span>{{ item.source }}</span>
            <span v-if="item.published_at">{{ item.published_at }}</span>
          </div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.summary || '点击查看公众号原文。' }}</p>
          <el-button link type="primary">查看原文</el-button>
        </div>
      </article>
    </div>
    <div v-else class="news-empty">
      暂无已发布推文。管理员可在后台“新闻推文管理”中添加公众号文章。
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ArrowRight, DataAnalysis, Search, Tickets } from '@element-plus/icons-vue'
import { getPublicNewsApi } from '@/api/public'

const newsItems = ref([])

function openNews(item) {
  window.open(item.source_url, '_blank', 'noopener,noreferrer')
}

async function loadNews() {
  const res = await getPublicNewsApi({ page: 1, page_size: 6, featured_only: true })
  newsItems.value = res.items || []
}

onMounted(loadNews)
</script>

<style scoped>
.home-hero {
  color: #fff;
  background:
    linear-gradient(120deg, rgba(15, 118, 110, 0.94), rgba(37, 99, 235, 0.82)),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='620' viewBox='0 0 1200 620'%3E%3Cpath d='M0 470c150-68 262-77 420-30 132 39 247 35 393-27 154-65 255-69 387-19v226H0z' fill='%23ffffff' fill-opacity='.18'/%3E%3Cpath d='M93 143h188v278H93zM339 202h188v219H339zM585 102h188v319H585zM831 171h188v250H831z' fill='%23ffffff' fill-opacity='.12'/%3E%3C/svg%3E");
  background-size: cover;
}

.hero-inner {
  width: min(1120px, calc(100% - 32px));
  min-height: 390px;
  margin: 0 auto;
  padding: 72px 0 88px;
}

.hero-kicker {
  margin: 0 0 14px;
  font-weight: 700;
}

h1 {
  margin: 0;
  font-size: 46px;
  line-height: 1.2;
}

.hero-copy {
  max-width: 640px;
  margin: 18px 0 0;
  font-size: 18px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.home-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: -50px;
}

.service-card {
  display: block;
  min-height: 190px;
  padding: 24px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 16px 45px rgba(15, 23, 42, 0.08);
}

.service-card .el-icon {
  width: 42px;
  height: 42px;
  color: #0f766e;
  font-size: 28px;
  background: #e8f5f2;
  border-radius: 8px;
}

.service-card h2 {
  margin: 18px 0 8px;
  font-size: 20px;
}

.service-card p {
  margin: 0;
  color: #6b7280;
  line-height: 1.7;
}

.news-section {
  padding-top: 0;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin-bottom: 18px;
}

.section-kicker {
  margin: 0 0 6px;
  color: #0f766e;
  font-weight: 700;
}

.section-head h2 {
  margin: 0;
  font-size: 28px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.news-card {
  overflow: hidden;
  cursor: pointer;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: transform 0.18s, box-shadow 0.18s;
}

.news-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.1);
}

.news-cover {
  aspect-ratio: 16 / 9;
  background: #e8f5f2;
}

.news-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.news-body {
  padding: 18px;
}

.news-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #6b7280;
  font-size: 13px;
}

.news-body h3 {
  margin: 10px 0 8px;
  font-size: 18px;
  line-height: 1.45;
}

.news-body p {
  min-height: 48px;
  margin: 0 0 10px;
  color: #6b7280;
  line-height: 1.7;
}

.news-empty {
  padding: 28px;
  color: #6b7280;
  text-align: center;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

@media (max-width: 860px) {
  .home-grid,
  .news-grid {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 34px;
  }
}
</style>
