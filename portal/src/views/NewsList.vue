<template>
  <section class="page">
    <h1 class="page-title">最新动态</h1>
    <p class="page-desc">浏览基金会公众号推文和近期动态，点击卡片可跳转到公众号原文。</p>

    <div v-if="items.length" class="news-grid">
      <article v-for="item in items" :key="item.id" class="news-card" @click="openNews(item)">
        <div v-if="item.cover_url" class="news-cover">
          <img :src="item.cover_url" :alt="item.title" />
        </div>
        <div class="news-body">
          <div class="news-meta">
            <span>{{ item.source }}</span>
            <span v-if="item.published_at">{{ item.published_at }}</span>
          </div>
          <h2>{{ item.title }}</h2>
          <p>{{ item.summary || '点击查看公众号原文。' }}</p>
          <el-button link type="primary">查看原文</el-button>
        </div>
      </article>
    </div>

    <div v-else class="news-empty">
      暂无已发布推文。
    </div>

    <el-pagination
      v-if="total > pageSize"
      class="pager"
      layout="prev, pager, next, total"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="handlePageChange"
    />
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getPublicNewsApi } from '@/api/public'

const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 9

function openNews(item) {
  window.open(item.source_url, '_blank', 'noopener,noreferrer')
}

async function loadNews() {
  const res = await getPublicNewsApi({
    page: page.value,
    page_size: pageSize,
    featured_only: false,
  })
  items.value = res.items || []
  total.value = res.total || 0
}

function handlePageChange(value) {
  page.value = value
  loadNews()
}

onMounted(loadNews)
</script>

<style scoped>
.news-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 24px;
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
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
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

.news-body h2 {
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
  margin-top: 24px;
  padding: 28px;
  color: #6b7280;
  text-align: center;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.pager {
  justify-content: center;
  margin-top: 24px;
}

@media (max-width: 860px) {
  .news-grid {
    grid-template-columns: 1fr;
  }
}
</style>
