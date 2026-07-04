<template>
  <view class="page fund-detail-page">
    <view class="page-shell">
      <view class="fund-head">
        <view class="section-kicker">基金明细</view>
        <view class="fund-title">{{ summary.fund_name || '基金明细' }}</view>
        <view class="fund-summary">{{ summary.description || '查看该基金的当前收支情况。' }}</view>
      </view>

      <view class="fund-metrics">
        <view class="metric-item">
          <view class="metric-label">总收入</view>
          <view class="metric-value">{{ formatAmount(summary.total_income) }}</view>
        </view>
        <view class="metric-item">
          <view class="metric-label">总支出</view>
          <view class="metric-value">{{ formatAmount(summary.total_expense) }}</view>
        </view>
        <view class="metric-item">
          <view class="metric-label">余额</view>
          <view class="metric-value metric-strong">{{ formatAmount(summary.balance) }}</view>
        </view>
      </view>

      <view class="fund-records">
        <view class="section-title">收支记录</view>
        <view class="section-subtitle">展示当前基金的收入与支出明细。</view>

        <view v-if="items.length" class="record-list">
          <view v-for="(item, index) in items" :key="index" class="record-row">
            <view class="record-date">{{ item.record_date }}</view>
            <view class="record-body">
              <view class="row-between">
                <view class="list-title">{{ item.project_desc }}</view>
                <text class="record-amount">{{ formatAmount(item.income_amount || item.expense_amount) }}</text>
              </view>
              <view class="list-desc">{{ item.income_amount ? '收入' : '支出' }}</view>
            </view>
          </view>
        </view>
        <view v-else class="empty-block">暂无记录</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getMemberFundUsage } from '../../api/member'
import { requireMemberAuth } from '../../utils/auth'

const summary = ref({})
const items = ref([])

function formatAmount(value) {
  return Number(value || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

async function loadData(id) {
  if (!requireMemberAuth()) return
  const res = await getMemberFundUsage(id, { page: 1, page_size: 100 })
  summary.value = res.summary || {}
  items.value = res.items || []
}

onLoad((options) => {
  loadData(options.id).catch(() => {})
})
</script>

<style scoped>
.fund-detail-page {
  background: linear-gradient(180deg, #f4f7fc 0%, #f8fbfe 100%);
}

.fund-head,
.fund-metrics,
.fund-records {
  background: #ffffff;
  padding: 30rpx 28rpx;
}

.fund-metrics,
.fund-records {
  margin-top: 16rpx;
}

.fund-title {
  margin-top: 10rpx;
  color: #1b2536;
  font-size: 50rpx;
  font-weight: 700;
}

.fund-summary {
  margin-top: 16rpx;
  color: #68778f;
  font-size: 25rpx;
  line-height: 1.88;
}

.fund-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18rpx;
}

.metric-label {
  color: #8390a4;
  font-size: 22rpx;
}

.metric-value {
  margin-top: 10rpx;
  color: #1b2536;
  font-size: 30rpx;
  font-weight: 700;
  word-break: break-all;
}

.metric-strong,
.record-amount {
  color: #485291;
}

.record-row {
  display: grid;
  grid-template-columns: 156rpx minmax(0, 1fr);
  gap: 18rpx;
  min-height: 112rpx;
  align-items: start;
  padding: 18rpx 0;
  border-top: 1rpx solid #e6edf5;
}

.record-date {
  color: #8b98a7;
  font-size: 22rpx;
  line-height: 1.7;
}
</style>
