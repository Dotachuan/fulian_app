<template>
  <view class="page">
    <view class="page-shell">
      <view v-if="!loggedIn" class="card card-soft">
        <view class="section-title">请先登录</view>
        <view class="section-subtitle">登录后可查看本人捐赠记录、累计金额与捐赠证书。</view>
        <view class="button-primary state-action" @click="goLogin">去登录</view>
      </view>

      <view v-else-if="memberState !== 'bound'" class="card card-soft">
        <view class="section-title">{{ stateTitle }}</view>
        <view class="section-subtitle">{{ stateDescription }}</view>
        <view class="button-ghost state-action" @click="goMy">查看会员状态</view>
      </view>

      <template v-else>
        <view class="card hero-card donation-hero">
          <view class="brand-chip donation-chip">个人捐赠档案</view>
          <view class="hero-title">{{ summary.donor_name || member?.name || '会员捐赠' }}</view>
          <view class="hero-desc">
            截至目前，已累计捐赠 {{ formatAmount(summary.total_amount) }} 元，共 {{ summary.total_count || 0 }} 笔。
          </view>
          <view class="hero-meta">加入福莲第 {{ summary.support_years || 0 }} 年</view>
          <view class="button-secondary cert-btn" @click="openCertificate">查看捐赠证书</view>
        </view>

        <view class="summary-grid">
          <view class="summary-tile">
            <view class="summary-label">累计金额</view>
            <view class="summary-value money-strong">{{ formatAmount(summary.total_amount) }}</view>
          </view>
          <view class="summary-tile">
            <view class="summary-label">累计笔数</view>
            <view class="summary-value">{{ summary.total_count || 0 }}</view>
          </view>
        </view>

        <view class="card">
          <view class="section-header">
            <view>
              <view class="section-title">捐赠明细</view>
              <view class="section-subtitle">仅展示当前登录会员本人可见的捐赠记录。</view>
            </view>
          </view>

          <view v-if="loading" class="empty-block">捐赠数据加载中</view>
          <view v-else-if="items.length" class="record-list">
            <view v-for="item in items" :key="item.donation_no" class="record-item">
              <view class="record-date">{{ item.donation_date }}</view>
              <view class="record-body">
                <view class="row-between">
                  <view class="list-title">{{ item.target_name || '未命名项目' }}</view>
                  <text class="money-strong">{{ formatAmount(item.amount) }}</text>
                </view>
                <view class="list-desc">{{ item.donation_no }}</view>
              </view>
            </view>
          </view>
          <view v-else class="empty-block">暂无捐赠记录</view>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMemberDonationSummary, getMemberDonations } from '../../api/member'
import {
  getBindingDescription,
  getMember,
  getMemberAccessState,
  goLogin,
  isLoggedIn,
  setMember,
} from '../../utils/auth'

const member = ref(getMember())
const summary = ref({})
const items = ref([])
const loading = ref(false)

const loggedIn = computed(() => isLoggedIn())
const memberState = computed(() => getMemberAccessState(member.value))
const stateTitle = computed(() => {
  return {
    pending: '待管理员绑定',
    ambiguous: '待人工处理',
  }[memberState.value] || '当前不可查看'
})
const stateDescription = computed(() => getBindingDescription(member.value))

function formatAmount(value) {
  return Number(value || 0).toFixed(2)
}

async function loadData() {
  member.value = getMember()
  if (!loggedIn.value || memberState.value !== 'bound') {
    summary.value = {}
    items.value = []
    return
  }

  loading.value = true
  try {
    const [summaryRes, listRes] = await Promise.all([
      getMemberDonationSummary(),
      getMemberDonations({ page: 1, page_size: 50 }),
    ])
    summary.value = summaryRes || {}
    items.value = listRes.items || []
  } finally {
    loading.value = false
  }
}

function goMy() {
  uni.switchTab({ url: '/pages/my/index' })
}

function openCertificate() {
  uni.navigateTo({ url: '/pages/certificate/index' })
}

onShow(() => {
  const latest = getMember()
  member.value = latest
  if (latest) {
    setMember(latest)
  }
  loadData().catch(() => {})
})
</script>

<style scoped>
.donation-hero {
  min-height: 250rpx;
}

.donation-chip {
  background: rgba(235, 233, 218, 0.16);
  color: #ede0c6;
  border-color: rgba(216, 179, 106, 0.24);
}

.cert-btn {
  margin-top: 20rpx;
  background: rgba(247, 243, 236, 0.14);
  color: #f7f3ec;
  border: 1rpx solid rgba(237, 224, 198, 0.14);
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.record-item {
  display: flex;
  gap: 16rpx;
}

.record-date {
  width: 132rpx;
  color: #8b98a7;
  font-size: 22rpx;
  line-height: 1.7;
  flex-shrink: 0;
}

.record-body {
  flex: 1;
  padding: 0 0 18rpx 18rpx;
  border-left: 2rpx solid #e2d8c8;
}

.state-action {
  margin-top: 24rpx;
}
</style>
