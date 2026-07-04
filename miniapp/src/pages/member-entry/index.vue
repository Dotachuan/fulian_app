<template>
  <view class="page">
    <view class="page-shell">
      <view v-if="!loggedIn" class="card card-soft">
        <view class="section-title">会员入口</view>
        <view class="section-subtitle">登录后可查看本人捐赠、提交开票申请并浏览会员名录，所有数据均围绕会员本人展开。</view>
        <view class="trust-note">
          <view class="trust-note-mark">守</view>
          <view class="trust-note-text">该模块仅展示当前会员本人可见信息，不开放跨人查询。</view>
        </view>
        <view class="button-primary state-action" @click="goLogin">去登录</view>
      </view>

      <template v-else>
        <view class="card hero-card entry-hero">
          <view class="brand-chip entry-chip">会员专属服务</view>
          <view class="hero-title">{{ member?.name || '福莲会员' }}</view>
          <view class="hero-desc">{{ bindingDescription }}</view>
          <view class="hero-meta">{{ member?.phone || '' }}</view>

          <view class="entry-meta-grid">
            <view class="entry-meta-item">
              <view class="entry-meta-label">信息范围</view>
              <view class="entry-meta-value">仅本人可见</view>
            </view>
            <view class="entry-meta-item">
              <view class="entry-meta-label">服务类型</view>
              <view class="entry-meta-value">查询与申请</view>
            </view>
          </view>
        </view>

        <view class="card">
          <view class="section-header">
            <view>
              <view class="section-title">会员服务矩阵</view>
              <view class="section-subtitle">以资料可信、操作可追溯为前提，组织当前一期核心能力。</view>
            </view>
          </view>

          <view class="service-stack">
            <view
              v-for="item in entryItems"
              :key="item.url"
              class="service-card"
              @click="openItem(item)"
            >
              <view class="service-top">
                <view class="service-no">{{ item.no }}</view>
                <view class="service-arrow">→</view>
              </view>
              <view class="service-title">{{ item.title }}</view>
              <view class="service-desc">{{ item.desc }}</view>
              <view class="service-note">{{ item.note }}</view>
            </view>
          </view>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getBindingDescription, getMember, goLogin, isLoggedIn } from '../../utils/auth'

const member = ref(getMember())
const loggedIn = ref(isLoggedIn())
const bindingDescription = computed(() => getBindingDescription(member.value))

const entryItems = [
  {
    no: '01',
    title: '我的捐赠',
    desc: '查看累计捐赠、逐笔明细与捐赠证书，形成完整的个人捐赠档案。',
    note: '适合快速确认历年捐赠与当前累计情况。',
    url: '/pages/donations/index',
  },
  {
    no: '02',
    title: '开票申请',
    desc: '保存常用开票资料，并在需要时发起新的申请，减少重复填写。',
    note: '适合处理票据信息补录与日常申请。',
    url: '/pages/invoice/index',
  },
  {
    no: '03',
    title: '会员名录',
    desc: '浏览会员姓名与工作单位，帮助形成相对克制而清晰的内部联系感。',
    note: '不展示电话，仅提供基础身份识别信息。',
    url: '/pages/directory/index',
  },
]

function openItem(item) {
  uni.navigateTo({ url: item.url })
}

onShow(() => {
  member.value = getMember()
  loggedIn.value = isLoggedIn()
})
</script>

<style scoped>
.entry-hero {
  min-height: 250rpx;
}

.entry-chip {
  background: rgba(235, 233, 218, 0.16);
  color: #ede0c6;
  border-color: rgba(216, 179, 106, 0.24);
}

.entry-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14rpx;
  margin-top: 24rpx;
}

.entry-meta-item {
  padding: 18rpx 18rpx;
  border-radius: 14rpx;
  background: rgba(247, 243, 236, 0.08);
  border: 1rpx solid rgba(237, 224, 198, 0.12);
}

.entry-meta-label {
  color: rgba(237, 224, 198, 0.72);
  font-size: 21rpx;
}

.entry-meta-value {
  margin-top: 8rpx;
  color: #f7f3ec;
  font-size: 25rpx;
  font-weight: 600;
}

.service-stack {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.service-card {
  padding: 24rpx 22rpx;
  border-radius: 16rpx;
  background: linear-gradient(180deg, #fffdf8 0%, #f7f1e8 100%);
  border: 1rpx solid rgba(154, 122, 78, 0.14);
}

.service-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.service-no {
  color: #9a7a4e;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
}

.service-arrow {
  color: #2a6a66;
  font-size: 30rpx;
  line-height: 1;
}

.service-title {
  margin-top: 14rpx;
  color: #16232e;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.42;
}

.service-desc {
  margin-top: 10rpx;
  color: #556371;
  font-size: 24rpx;
  line-height: 1.72;
}

.service-note {
  margin-top: 14rpx;
  color: #8b98a7;
  font-size: 22rpx;
  line-height: 1.62;
}

.state-action {
  margin-top: 24rpx;
}
</style>
