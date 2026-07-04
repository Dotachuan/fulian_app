<template>
  <view class="page">
    <view class="page-shell">
      <view class="card card-soft">
        <view class="section-title">机构简介</view>
        <view class="section-subtitle">展示福莲的使命、愿景与机构简介。</view>
      </view>

      <view v-for="item in items" :key="item.key" class="card intro-card">
        <view class="intro-kicker">{{ item.title }}</view>
        <view v-if="item.summary" class="section-subtitle">{{ item.summary }}</view>
        <view class="soft-divider"></view>
        <view class="content">{{ item.content || '暂无内容' }}</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { getPublicSiteContent } from '../../api/public'

const items = ref([])

async function loadData() {
  try {
    items.value = await getPublicSiteContent()
  } catch (error) {
    items.value = []
  }
}

loadData().catch(() => {})
</script>

<style scoped>
.intro-kicker {
  color: #9a7a4e;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
}

.content {
  line-height: 1.9;
  color: #4f5d6b;
  white-space: pre-wrap;
}
</style>
