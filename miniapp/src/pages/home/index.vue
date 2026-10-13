<template>
  <view class="page home-page">
    <view class="brand-stage">
      <view class="hero-topbar">
        <view class="brand-block">
          <image class="brand-mark" :src="foundationLogo" mode="aspectFit" />
          <view class="brand-texts">
            <view class="brand-name">福莲教育促进会</view>
            <view class="brand-sub">Fulian Education Foundation</view>
          </view>
        </view>

        <button class="share-button" open-type="share">分享</button>
      </view>

    </view>

    <view class="home-content">
      <view class="home-reader">
        <view class="home-reader-title">福莲教育是一个怎么样的公益组织</view>

        <view class="home-ppt-flow">
          <view v-for="(slide, index) in homePptSlides" :key="slide.no" class="home-ppt-page">
            <image
              v-if="!failedHomeSlides[slide.no]"
              class="home-ppt-image"
              :src="slide.url"
              mode="widthFix"
              lazy-load
              show-menu-by-longpress
              @click="previewHomeSlide(index)"
              @error="markHomeSlideFailed(slide.no)"
            />
            <view v-else class="home-ppt-error">该页图片暂未加载</view>
          </view>
        </view>
      </view>

    </view>
  </view>
</template>

<script>
export default {
  onShareAppMessage() {
    return {
      title: '福莲教育促进会',
      path: '/pages/home/index',
    }
  },
}
</script>

<script setup>
import { ref } from 'vue'
import { getFulianPptImagePath } from '../../utils/fulian-ppt'
import { normalizeMediaUrl } from '../../utils/media'
import foundationLogo from '../../static/foundation-logo.jpg'

const failedHomeSlides = ref({})
const homePptSlides = Array.from({ length: 39 }, (_, index) => {
  const no = index + 1
  return {
    no,
    url: normalizeMediaUrl(getFulianPptImagePath(no)),
  }
})

function previewHomeSlide(index) {
  uni.previewImage({
    current: homePptSlides[index].url,
    urls: homePptSlides.map((slide) => slide.url),
  })
}

function markHomeSlideFailed(slideNo) {
  failedHomeSlides.value = {
    ...failedHomeSlides.value,
    [slideNo]: true,
  }
}

</script>

<style scoped>
.home-page {
  padding: 0 0 56rpx;
  background: linear-gradient(180deg, #f6f8fc 0%, #f9fbfe 100%);
}

.brand-stage {
  background: #ffffff;
  border-bottom: 1rpx solid rgba(215, 224, 236, 0.9);
}

.hero-topbar {
  position: relative;
  z-index: 2;
  width: calc(100% - 56rpx);
  margin: 0 auto;
}

.hero-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 28rpx 0 26rpx;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14rpx;
  padding: 0;
}

.brand-mark {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: #ffffff;
  border: 1rpx solid rgba(90, 102, 116, 0.12);
  flex-shrink: 0;
}

.brand-name {
  color: #1b2536;
  font-size: 27rpx;
  font-weight: 700;
  line-height: 1.28;
}

.brand-sub {
  margin-top: 2rpx;
  color: #8390a4;
  font-size: 19rpx;
}

.share-button {
  margin: 0;
  min-width: 112rpx;
  height: 64rpx;
  padding: 0 22rpx;
  border: 0;
  border-radius: 999rpx;
  background: #f1f4fa;
  color: #485291;
  font-size: 23rpx;
  font-weight: 700;
  line-height: 64rpx;
}

.share-button::after {
  border: 0;
}

.hero-entry {
  min-width: 162rpx;
  min-height: 68rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(18rpx);
  color: #485291;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23rpx;
  font-weight: 600;
}

.anchor-bar {
  position: relative;
  z-index: 3;
  display: flex;
  justify-content: center;
  gap: 14rpx;
  width: calc(100% - 80rpx);
  margin: -44rpx auto 0;
  padding: 12rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(18rpx);
  box-shadow: 0 18rpx 34rpx rgba(28, 37, 45, 0.08);
}

.anchor-item {
  min-width: 116rpx;
  min-height: 58rpx;
  padding: 0 16rpx;
  border-radius: 999rpx;
  color: #55637b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23rpx;
  font-weight: 600;
}

.home-content {
  padding: 0;
}

.home-reader {
  padding: 30rpx 28rpx 48rpx;
}

.home-reader-title {
  padding: 8rpx 12rpx 30rpx;
  color: #111827;
  font-size: 46rpx;
  font-weight: 800;
  line-height: 1.36;
  text-align: center;
}

.home-ppt-flow {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.home-ppt-page {
  overflow: hidden;
  width: 100%;
  background: #eef3f8;
}

.home-ppt-image {
  display: block;
  width: 100%;
}

.home-ppt-error {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 360rpx;
  background: #f3f6fa;
  color: #7c899c;
  font-size: 24rpx;
}

.section-band {
  padding: 40rpx 28rpx;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.section-kicker {
  color: #5a67aa;
  font-size: 21rpx;
  font-weight: 700;
  letter-spacing: 1.5rpx;
}

.home-title {
  margin-top: 8rpx;
  color: #1b2536;
  font-size: 44rpx;
  font-weight: 700;
}

.intro-band {
  padding-top: 24rpx;
  padding-bottom: 20rpx;
  background: linear-gradient(180deg, #fbfcff 0%, #f2f6fb 100%);
}

.intro-layout {
  position: relative;
  overflow: hidden;
  padding: 32rpx 30rpx;
  border-radius: 8rpx;
  background: #eef2f0;
  box-shadow: 0 18rpx 42rpx rgba(29, 45, 68, 0.06);
}

.intro-background,
.intro-background-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.intro-background-overlay {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.92) 0%,
    rgba(255, 255, 255, 0.82) 58%,
    rgba(255, 255, 255, 0.7) 100%
  );
}

.intro-main {
  position: relative;
  z-index: 2;
}

.intro-title {
  color: #1b2536;
  font-size: 50rpx;
  font-weight: 700;
  line-height: 1.16;
}

.intro-text {
  margin-top: 20rpx;
  color: #667791;
  font-size: 27rpx;
  line-height: 1.92;
}

.ppt-band {
  padding-top: 20rpx;
  background: #ffffff;
}

.ppt-grid-head {
  margin-bottom: 26rpx;
}

.ppt-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.ppt-grid-card {
  position: relative;
  height: 184rpx;
  overflow: hidden;
  border: 1rpx solid rgba(215, 224, 236, 0.95);
  border-radius: 8rpx;
  background: #ffffff;
  box-shadow: 0 18rpx 42rpx rgba(29, 45, 68, 0.06);
}

.ppt-card-media {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.ppt-card-cover {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.news-band {
  background: #ffffff;
}

.news-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20rpx;
}

.news-panel {
  position: relative;
  min-height: 420rpx;
  overflow: hidden;
  border-radius: 30rpx;
  background: #dde5f1;
}

.news-panel-accent {
  margin-top: 40rpx;
}

.news-panel-image,
.news-panel-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.news-panel-fallback {
  background: linear-gradient(140deg, #475291 0%, #6674b5 100%);
}

.news-panel-overlay {
  background: linear-gradient(180deg, rgba(10, 21, 28, 0.04) 0%, rgba(10, 21, 28, 0.64) 100%);
}

.news-panel-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
  padding: 28rpx;
}

.news-date {
  color: rgba(233, 238, 248, 0.84);
  font-size: 20rpx;
}

.news-title {
  margin-top: 10rpx;
  color: #f7f9fc;
  font-size: 27rpx;
  font-weight: 700;
  line-height: 1.42;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.news-summary {
  margin-top: 8rpx;
  color: rgba(236, 241, 250, 0.78);
  font-size: 20rpx;
  line-height: 1.58;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.news-arrow {
  width: 72rpx;
  height: 72rpx;
  margin-top: 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.92);
  color: #485291;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
}

.activity-band {
  background: linear-gradient(180deg, #f2f6fb 0%, #f9fbfe 100%);
}

.activity-tabs {
  display: flex;
  justify-content: center;
  gap: 18rpx;
  margin-bottom: 22rpx;
  flex-wrap: wrap;
}

.activity-tab {
  min-height: 60rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  color: #98a5b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23rpx;
  font-weight: 600;
}

.activity-tab-active {
  background: #e9eef8;
  color: #5a67aa;
}

.activity-stage {
  display: grid;
  grid-template-columns: 0.22fr 1.56fr 0.22fr;
  gap: 16rpx;
  align-items: stretch;
}

.activity-ghost {
  border-radius: 28rpx;
  background: linear-gradient(180deg, rgba(239, 244, 251, 0.92) 0%, rgba(231, 238, 248, 0.98) 100%);
}

.activity-focus {
  position: relative;
  min-height: 410rpx;
  overflow: hidden;
  border-radius: 30rpx;
}

.activity-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.activity-image-fallback {
  background: linear-gradient(145deg, #475291 0%, #5d69ab 100%);
}

.activity-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(11, 24, 31, 0.04) 0%, rgba(11, 24, 31, 0.12) 44%, rgba(11, 24, 31, 0.62) 100%);
}

.activity-copy {
  position: absolute;
  left: 34rpx;
  bottom: 34rpx;
  z-index: 2;
  max-width: 340rpx;
  color: #f7f9fc;
}

.activity-title {
  font-size: 29rpx;
  font-weight: 700;
  line-height: 1.38;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.activity-btn {
  width: 168rpx;
  margin-top: 18rpx;
  background: rgba(255, 255, 255, 0.95);
  color: #485291;
}

.notice-band {
  background: #ffffff;
}

.notice-flow {
  display: flex;
  flex-direction: column;
}

.notice-row {
  display: flex;
  gap: 18rpx;
  padding: 24rpx 0;
}

.notice-row + .notice-row {
  border-top: 1rpx solid #e6edf5;
}

.notice-line {
  width: 6rpx;
  border-radius: 999rpx;
  background: linear-gradient(180deg, #7180bf 0%, #485291 100%);
  flex-shrink: 0;
}

.notice-content {
  flex: 1;
}

.empty-state {
  padding: 46rpx 0 16rpx;
  color: #8390a4;
  font-size: 24rpx;
  text-align: center;
}
</style>
