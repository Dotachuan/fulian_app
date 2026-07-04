<template>
  <view class="page">
    <view class="page-shell">
      <view class="card card-soft">
        <view class="section-title">新闻列表</view>
        <view class="section-subtitle">展示近期新闻与公众号推文精选，作为机构资讯的持续更新栏目。</view>
      </view>

      <view class="card">
        <view v-if="items.length" class="news-list">
          <view v-for="item in items" :key="item.id" class="news-item" @click="openDetail(item)">
            <view class="news-kicker">{{ item.published_at || '近期更新' }}</view>
            <view class="list-title">{{ item.title }}</view>
            <view class="list-desc">{{ item.summary || '点击查看详情' }}</view>
          </view>
        </view>
        <view v-else class="empty-block">暂无新闻</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { getPublicNews } from '../../api/public'
import { openExternalLink } from '../../utils/external-link'

const items = ref([])

async function loadData() {
  const res = await getPublicNews({ page: 1, page_size: 20, featured_only: false })
  items.value = res.items || []
}

function openDetail(item) {
  openExternalLink(item?.source_url, item?.title || '公众号推文')
}

loadData().catch(() => {})
</script>

<style scoped>
.news-list {
  display: flex;
  flex-direction: column;
}

.news-item {
  padding: 22rpx 0;
}

.news-item + .news-item {
  border-top: 1rpx solid #ebe2d5;
}

.news-kicker {
  color: #9a7a4e;
  font-size: 21rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
}
</style>
