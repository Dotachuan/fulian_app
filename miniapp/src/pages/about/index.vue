<template>
  <view class="page finance-tab-page">
    <view class="finance-hero">
      <view class="hero-mark">FULIAN DISCLOSURE</view>
      <view class="finance-title">财务公示</view>
    </view>

    <view v-if="!loggedIn" class="finance-state">
      <view class="state-title">请先登录</view>
      <view class="state-desc">财务公示面向登录会员开放。</view>
      <view class="button-primary state-action" @click="goLogin">去登录</view>
    </view>

    <template v-else>
      <view class="report-section">
        <view class="section-heading">
          <view>
            <view class="section-title">年度报告</view>
            <view class="section-line"></view>
          </view>
          <view class="section-note">点击报告浏览</view>
        </view>

        <view v-if="reports.length" class="report-list">
          <view
            v-for="report in reports"
            :key="report.id"
            class="report-row"
            :class="{ disabled: !report.url }"
            @click="openReport(report)"
          >
            <view class="report-year">{{ report.year }}</view>
            <view class="report-main">
              <view class="report-title">{{ report.title }}</view>
              <view class="report-meta">{{ report.period }}</view>
            </view>
            <view class="report-action">
              <view v-if="report.url" class="action-text">浏览</view>
              <view v-else class="pending-text">待上传</view>
              <view class="arrow-line"></view>
            </view>
          </view>
        </view>

        <view v-else class="empty-block">暂无财务报告</view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAssetOrigin } from '../../config/env'
import { goLogin, isLoggedIn } from '../../utils/auth'

const loggedIn = ref(isLoggedIn())
const reportBaseUrl = `${getAssetOrigin()}/uploads/finance-reports`

const reports = ref([
  {
    id: '2026-q1',
    year: '2026',
    title: '福莲教育促进会 2026 年 1-3 月财务情况报告',
    period: '2026 年第一季度',
    url: `${reportBaseUrl}/fulian-finance-2026-q1.pdf`,
  },
  {
    id: '2025-annual',
    year: '2025',
    title: '福莲教育促进会 2025 年 1-12 月财务情况报告',
    period: '2025 年度',
    url: `${reportBaseUrl}/fulian-finance-2025-annual.pdf`,
  },
  {
    id: '2025-q3',
    year: '2025',
    title: '福莲教育促进会 2025 年 1-9 月财务情况报告',
    period: '2025 年前三季度',
    url: `${reportBaseUrl}/fulian-finance-2025-q3.pdf`,
  },
  {
    id: '2025-h1',
    year: '2025',
    title: '福莲教育促进会 2025 年 1-6 月财务情况报告',
    period: '2025 年上半年',
    url: `${reportBaseUrl}/fulian-finance-2025-h1.pdf`,
  },
  {
    id: '2025-q1',
    year: '2025',
    title: '福莲教育促进会 2025 年 1-3 月财务情况报告',
    period: '2025 年第一季度',
    url: `${reportBaseUrl}/fulian-finance-2025-q1.pdf`,
  },
  {
    id: '2024-annual',
    year: '2024',
    title: '福莲教育促进会 2024 年 1-12 月财务情况报告',
    period: '2024 年度',
    url: `${reportBaseUrl}/fulian-finance-2024-annual.pdf`,
  },
  {
    id: '2024-q3',
    year: '2024',
    title: '福莲教育促进会 2024 年 1-9 月财务情况报告',
    period: '2024 年前三季度',
    url: `${reportBaseUrl}/fulian-finance-2024-q3.pdf`,
  },
  {
    id: '2024-h1',
    year: '2024',
    title: '福莲教育促进会 2024 年 1-6 月财务情况报告',
    period: '2024 年上半年',
    url: `${reportBaseUrl}/fulian-finance-2024-h1.pdf`,
  },
  {
    id: '2024-q1',
    year: '2024',
    title: '福莲教育促进会 2024 年 1-3 月财务情况报告',
    period: '2024 年第一季度',
    url: `${reportBaseUrl}/fulian-finance-2024-q1.pdf`,
  },
  {
    id: '2023-annual',
    year: '2023',
    title: '福莲教育促进会 2023 年 1-12 月财务情况报告',
    period: '2023 年度',
    url: `${reportBaseUrl}/fulian-finance-2023-annual.pdf`,
  },
  {
    id: '2023-q3',
    year: '2023',
    title: '福莲教育促进会 2023 年 1-9 月财务情况报告',
    period: '2023 年前三季度',
    url: `${reportBaseUrl}/fulian-finance-2023-q3.pdf`,
  },
  {
    id: '2023-h1',
    year: '2023',
    title: '福莲教育促进会 2023 年 1-6 月财务情况报告',
    period: '2023 年上半年',
    url: `${reportBaseUrl}/fulian-finance-2023-h1.pdf`,
  },
  {
    id: '2023-q1',
    year: '2023',
    title: '福莲教育促进会 2023 年 1-3 月财务情况报告',
    period: '2023 年第一季度',
    url: `${reportBaseUrl}/fulian-finance-2023-q1.pdf`,
  },
  {
    id: '2022-annual',
    year: '2022',
    title: '福莲教育促进会 2022 年 1-12 月财务情况报告',
    period: '2022 年度',
    url: `${reportBaseUrl}/fulian-finance-2022-annual.pdf`,
  },
  {
    id: '2021-annual',
    year: '2021',
    title: '福莲教育促进会 2021 年 1-12 月财务情况报告',
    period: '2021 年度',
    url: `${reportBaseUrl}/fulian-finance-2021-annual.pdf`,
  },
  {
    id: '2020-annual',
    year: '2020',
    title: '福莲教育促进会 2020 年 1-12 月财务情况报告',
    period: '2020 年度',
    url: `${reportBaseUrl}/fulian-finance-2020-annual.pdf`,
  },
])

function openReport(report) {
  if (!report.url) {
    uni.showToast({ title: '报告文件待上传', icon: 'none' })
    return
  }

  // #ifdef H5
  window.open(report.url, '_blank', 'noopener,noreferrer')
  // #endif

  // #ifndef H5
  uni.showLoading({ title: '打开中...' })
  uni.downloadFile({
    url: report.url,
    success: (res) => {
      if (res.statusCode < 200 || res.statusCode >= 300) {
        uni.showToast({ title: '报告下载失败', icon: 'none' })
        return
      }
      uni.openDocument({
        filePath: res.tempFilePath,
        showMenu: true,
        success: () => {},
        fail: () => {
          uni.showToast({ title: '当前文件暂无法浏览', icon: 'none' })
        },
      })
    },
    fail: () => {
      uni.showToast({ title: '报告下载失败', icon: 'none' })
    },
    complete: () => {
      uni.hideLoading()
    },
  })
  // #endif
}

onShow(() => {
  loggedIn.value = isLoggedIn()
})
</script>

<style scoped>
.finance-tab-page {
  min-height: 100vh;
  padding-bottom: 56rpx;
  background:
    linear-gradient(180deg, rgba(243, 247, 252, 0.96) 0%, rgba(250, 252, 255, 0.98) 42%, #ffffff 100%),
    radial-gradient(circle at 88% 8%, rgba(72, 82, 145, 0.12), transparent 34%);
}

.finance-hero {
  padding: 56rpx 34rpx 42rpx;
}

.hero-mark {
  color: #6d7890;
  font-size: 20rpx;
  font-weight: 700;
  letter-spacing: 4rpx;
}

.finance-title {
  margin-top: 18rpx;
  color: #172233;
  font-size: 64rpx;
  font-weight: 800;
  line-height: 1.08;
}

.finance-state {
  margin: 0 34rpx;
  padding: 34rpx 0;
  border-top: 1rpx solid rgba(210, 220, 234, 0.9);
}

.state-title {
  color: #172233;
  font-size: 34rpx;
  font-weight: 700;
}

.state-desc {
  margin-top: 14rpx;
  color: #6f7f96;
  font-size: 26rpx;
  line-height: 1.72;
}

.state-action {
  margin-top: 24rpx;
}

.archive-strip {
  display: grid;
  grid-template-columns: 1fr 1rpx 1fr;
  align-items: center;
  margin: 0 34rpx 34rpx;
  padding: 26rpx 0;
  border-top: 1rpx solid rgba(200, 210, 225, 0.92);
  border-bottom: 1rpx solid rgba(200, 210, 225, 0.92);
}

.archive-item {
  min-width: 0;
}

.archive-divider {
  width: 1rpx;
  height: 58rpx;
  background: rgba(195, 164, 112, 0.55);
}

.archive-number {
  color: #485291;
  font-size: 42rpx;
  font-weight: 800;
  line-height: 1.1;
}

.archive-label {
  margin-top: 8rpx;
  color: #77869a;
  font-size: 23rpx;
}

.report-section {
  margin: 0 34rpx;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 18rpx;
}

.section-title {
  color: #172233;
  font-size: 36rpx;
  font-weight: 800;
}

.section-line {
  width: 72rpx;
  height: 4rpx;
  margin-top: 14rpx;
  background: linear-gradient(90deg, #485291, #bfa176);
}

.section-note {
  color: #8b97a8;
  font-size: 22rpx;
}

.report-list {
  border-top: 1rpx solid rgba(218, 226, 238, 0.95);
}

.report-row {
  display: grid;
  grid-template-columns: 112rpx minmax(0, 1fr) 110rpx;
  align-items: center;
  gap: 20rpx;
  min-height: 150rpx;
  border-bottom: 1rpx solid rgba(218, 226, 238, 0.95);
}

.report-row.disabled {
  opacity: 0.68;
}

.report-year {
  color: #b09362;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 42rpx;
  font-weight: 700;
  line-height: 1;
}

.report-main {
  min-width: 0;
}

.report-title {
  color: #1b2536;
  font-size: 29rpx;
  font-weight: 700;
  line-height: 1.45;
}

.report-meta {
  margin-top: 10rpx;
  color: #7c8a9e;
  font-size: 23rpx;
}

.report-action {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12rpx;
}

.action-text,
.pending-text {
  font-size: 24rpx;
  font-weight: 700;
}

.action-text {
  color: #485291;
}

.pending-text {
  color: #9aa6b6;
}

.arrow-line {
  width: 54rpx;
  height: 1rpx;
  background: linear-gradient(90deg, transparent, #bfa176);
}
</style>
