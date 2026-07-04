<template>
  <view class="page funds-page">
    <view class="page-shell">
      <view v-if="!loggedIn" class="state-band">
        <view class="section-title">请先登录</view>
        <view class="section-subtitle">会员登录后可查看基金列表、当前余额与收支明细。</view>
        <view class="button-primary state-action" @click="goLogin">去登录</view>
      </view>

      <template v-else>
        <view class="funds-head">
          <view class="section-kicker">财务公示</view>
          <view class="funds-title">基金列表</view>
          <view class="funds-summary">登录会员可查看基金余额、简介与后续收支明细。</view>
        </view>

        <view class="funds-list">
          <view v-if="loading" class="empty-block">基金数据加载中...</view>
          <view v-else-if="items.length">
            <view v-for="item in items" :key="item.id" class="fund-row" @click="openDetail(item.id)">
              <view class="fund-row-main">
                <view class="row-between">
                  <view class="list-title fund-row-title">{{ item.name }}</view>
                  <text class="fund-row-balance">余额 {{ formatAmount(item.balance) }}</text>
                </view>
                <view class="list-desc">{{ item.description || '暂无说明' }}</view>
              </view>
              <view class="fund-row-tail">→</view>
            </view>
          </view>
          <view v-else class="empty-block">暂无基金数据</view>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMemberFunds } from '../../api/member'
import { goLogin, isLoggedIn } from '../../utils/auth'

const items = ref([])
const loading = ref(false)
const loggedIn = ref(isLoggedIn())

function formatAmount(value) {
  return Number(value || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

async function loadData() {
  loggedIn.value = isLoggedIn()
  if (!loggedIn.value) return
  loading.value = true
  try {
    const res = await getMemberFunds()
    items.value = res.items || []
  } finally {
    loading.value = false
  }
}

function openDetail(id) {
  uni.navigateTo({ url: `/pages/fund-detail/index?id=${id}` })
}

onShow(() => {
  loggedIn.value = isLoggedIn()
  loadData().catch(() => {})
})
</script>

<style scoped>
.funds-page {
  background: linear-gradient(180deg, #f4f7fc 0%, #f8fbfe 100%);
}

.state-band,
.funds-head,
.funds-list {
  background: #ffffff;
  padding: 30rpx 28rpx;
}

.funds-list {
  margin-top: 16rpx;
}

.funds-title {
  margin-top: 10rpx;
  color: #1b2536;
  font-size: 50rpx;
  font-weight: 700;
}

.funds-summary {
  margin-top: 16rpx;
  color: #68778f;
  font-size: 25rpx;
  line-height: 1.88;
}

.fund-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 40rpx;
  gap: 16rpx;
  min-height: 120rpx;
  align-items: center;
  border-top: 1rpx solid #e6edf5;
}

.fund-row-title {
  flex: 1;
  min-width: 0;
}

.fund-row-balance {
  max-width: 260rpx;
  color: #485291;
  font-size: 24rpx;
  font-weight: 700;
  text-align: right;
  word-break: break-all;
}

.fund-row-tail {
  color: #7a87bb;
  font-size: 30rpx;
  text-align: right;
}

.state-action {
  margin-top: 24rpx;
}
</style>
