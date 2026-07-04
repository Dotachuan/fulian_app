<template>
  <view class="page">
    <view class="page-shell">
      <view class="card card-soft">
        <view class="section-title">公告列表</view>
        <view class="section-subtitle">查看机构公告、通知与重点提醒。</view>
      </view>

      <view class="card">
        <view v-if="items.length" class="notice-list">
          <view v-for="item in items" :key="item.id" class="notice-item" @click="openDetail(item.id)">
            <view class="row-between">
              <view class="list-title">{{ item.title }}</view>
              <text v-if="item.is_pinned" class="badge badge-warning">置顶</text>
            </view>
            <view class="list-desc">{{ item.summary || '点击查看详情' }}</view>
          </view>
        </view>
        <view v-else class="empty-block">暂无公告</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { getPublicNotices } from '../../api/public'

const items = ref([])

async function loadData() {
  const res = await getPublicNotices({ page: 1, page_size: 20 })
  items.value = res.items || []
}

function openDetail(id) {
  uni.navigateTo({ url: `/pages/notice-detail/index?id=${id}` })
}

loadData().catch(() => {})
</script>

<style scoped>
.notice-list {
  display: flex;
  flex-direction: column;
}

.notice-item {
  padding: 22rpx 0;
}

.notice-item + .notice-item {
  border-top: 1rpx solid #ebe2d5;
}
</style>
