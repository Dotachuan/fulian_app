<template>
  <view class="page">
    <view class="page-shell">
      <view class="card" v-if="detail">
        <view class="meta-text">{{ detail.published_at || '' }}</view>
        <view class="section-title detail-title">{{ detail.title }}</view>
        <view class="soft-divider"></view>
        <view class="content">{{ detail.content || detail.summary || '' }}</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getPublicNoticeDetail } from '../../api/public'

const detail = ref(null)

async function loadData(id) {
  detail.value = await getPublicNoticeDetail(id)
}

onLoad((options) => {
  loadData(options.id).catch(() => {})
})
</script>

<style scoped>
.detail-title {
  margin-top: 12rpx;
}

.content {
  line-height: 1.9;
  color: #4f5d6b;
  white-space: pre-wrap;
}
</style>
