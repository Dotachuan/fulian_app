<template>
  <view class="page projects-page">
    <view class="projects-hero">
      <image class="projects-hero-image" :src="heroImage" mode="aspectFill" />
      <view class="projects-hero-overlay"></view>
      <view class="projects-hero-copy">
        <view class="projects-kicker">公益项目 · 资金进展</view>
        <view class="projects-title">公益项目进展</view>
        <view class="projects-summary">
          围绕福莲教育主基金、福莲医学基金、福莲公益活动与专项基金四个板块，集中展示项目简介、资金概况与相关资讯。
        </view>
      </view>
    </view>

    <view class="projects-tabbar">
      <view
        v-for="item in sectionTabs"
        :key="item.key"
        class="projects-tab"
        :class="{ 'projects-tab-active': activeSection === item.key }"
        @click="activeSection = item.key"
      >
        {{ item.title }}
      </view>
    </view>

    <view v-if="currentSection" class="project-stage">
      <view class="section-band intro-band">
        <view class="section-head">
          <view>
            <view class="section-kicker">{{ currentSection.title }}</view>
            <view class="section-title">{{ currentSection.title }}</view>
          </view>
        </view>

        <view class="project-intro-layout">
          <view class="project-intro-copy">{{ currentSection.summary }}</view>
          <view class="project-metric-strip">
            <view class="project-metric">
              <view class="project-metric-label">累计收入</view>
              <view class="project-metric-value">{{ formatAmount(currentSection.total_income) }}</view>
            </view>
            <view class="project-metric">
              <view class="project-metric-label">累计支出</view>
              <view class="project-metric-value">{{ formatAmount(currentSection.total_expense) }}</view>
            </view>
            <view class="project-metric">
              <view class="project-metric-label">当前余额</view>
              <view class="project-metric-value">{{ formatAmount(currentSection.balance) }}</view>
            </view>
          </view>
        </view>
      </view>

      <view class="section-band showcase-band">
        <view class="section-head">
          <view>
            <view class="section-kicker">项目资讯</view>
            <view class="section-title">图文展示</view>
          </view>
          <text class="link-text" @click="openProjectLinkList">查看更多</text>
        </view>

        <view v-if="showcaseCarouselItems.length" class="showcase-stage">
          <swiper
            class="showcase-swiper"
            circular
            easing-function="easeOutCubic"
            :duration="360"
            :current="activeShowcaseIndex"
            :previous-margin="showcaseSideMargin"
            :next-margin="showcaseSideMargin"
            @change="handleShowcaseChange"
          >
            <swiper-item
              v-for="(item, index) in showcaseCarouselItems"
              :key="item.id || item.title || index"
              class="showcase-swiper-item"
            >
              <view
                class="showcase-slide"
                :class="{ 'showcase-slide-active': index === activeShowcaseIndex }"
                @click="openLink(item)"
              >
                <image class="showcase-image" :src="item.image_url || heroImage" mode="aspectFill" />
                <view class="showcase-overlay"></view>
                <view class="showcase-copy">
                  <view class="showcase-date">{{ formatDate(item.published_at) }}</view>
                  <view class="showcase-title">{{ item.title }}</view>
                  <view class="showcase-desc">{{ item.summary || '点击查看完整资讯。' }}</view>
                </view>
              </view>
            </swiper-item>
          </swiper>

          <view v-if="showcaseCarouselItems.length > 1" class="showcase-dots">
            <view
              v-for="(item, index) in showcaseCarouselItems"
              :key="item.id || `dot-${index}`"
              class="showcase-dot"
              :class="{ 'showcase-dot-active': index === activeShowcaseIndex }"
            ></view>
          </view>
        </view>
        <view v-else class="empty-state">管理员暂未配置该板块的图文资讯</view>
      </view>

      <view class="section-band funds-band">
        <view class="section-head">
          <view>
            <view class="section-kicker">基金概览</view>
            <view class="section-title">相关资金简介</view>
          </view>
        </view>

        <view v-if="currentSection.funds?.length" class="funds-flow">
          <view v-for="fund in currentSection.funds" :key="fund.id" class="fund-row">
            <view class="fund-row-main">
              <view class="list-title">{{ fund.name }}</view>
              <view class="list-desc">{{ fund.description || '暂无简介' }}</view>
            </view>
            <view class="fund-row-side">
              <view class="fund-money">{{ formatAmount(fund.balance) }}</view>
              <view class="fund-money-label">当前余额</view>
            </view>
          </view>
        </view>
        <view v-else class="empty-state">暂无基金数据</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import heroImage from '../../static/foundation-home-reference.jpeg'
import { getPublicProjectProgress } from '../../api/public'
import { openExternalLink } from '../../utils/external-link'
import { normalizeMediaUrl } from '../../utils/media'

const sections = ref([])
const activeSection = ref('main')
const activeShowcaseIndex = ref(0)
const showcaseSideMargin = '92rpx'

const sectionTabs = computed(() => sections.value.map((item) => ({ key: item.key, title: item.title })))
const currentSection = computed(() => sections.value.find((item) => item.key === activeSection.value) || sections.value[0] || null)
const showcaseLinkItems = computed(() => (currentSection.value?.links || []).slice(0, 3))
const showcaseCarouselItems = computed(() => {
  const items = showcaseLinkItems.value
  if (!items.length) return []
  if (items.length === 1) return [items[0]]
  if (items.length === 2) return [items[1], items[0]]
  return [items[1], items[0], items[2]]
})

watch(
  showcaseCarouselItems,
  (items) => {
    activeShowcaseIndex.value = items.length > 1 ? 1 : 0
  },
  { immediate: true },
)

function formatAmount(value) {
  return Number(value || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatDate(value) {
  return value || '近期更新'
}

async function loadData() {
  const res = await getPublicProjectProgress()
  sections.value = (res.sections || []).map((section) => ({
    ...section,
    links: (section.links || []).map((item) => ({
      ...item,
      image_url: normalizeMediaUrl(item.image_url),
    })),
  }))
  if (!sections.value.find((item) => item.key === activeSection.value) && sections.value.length) {
    activeSection.value = sections.value[0].key
  }
}

function handleShowcaseChange(event) {
  activeShowcaseIndex.value = event?.detail?.current ?? 0
}

function openLink(item) {
  openExternalLink(item?.target_url, item?.title || '公众号推文')
}

function openProjectLinkList() {
  if (!currentSection.value) return
  uni.setStorageSync('project_links_view_payload', {
    section_key: currentSection.value.key,
    title: currentSection.value.title,
    items: currentSection.value.links || [],
  })
  uni.navigateTo({ url: '/pages/project-links/index' })
}

loadData().catch(() => {})
</script>

<style scoped>
.projects-page {
  padding: 0 0 56rpx;
  background: linear-gradient(180deg, #f6f8fc 0%, #f9fbfe 100%);
}

.projects-hero {
  position: relative;
  min-height: 700rpx;
  overflow: hidden;
}

.projects-hero-image,
.projects-hero-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.projects-hero-overlay {
  background: linear-gradient(180deg, rgba(11, 21, 29, 0.14) 0%, rgba(11, 21, 29, 0.34) 38%, rgba(11, 21, 29, 0.76) 100%);
}

.projects-hero-copy {
  position: relative;
  z-index: 2;
  width: calc(100% - 56rpx);
  margin: 0 auto;
  padding-top: 244rpx;
}

.projects-kicker {
  color: rgba(232, 237, 248, 0.86);
  font-size: 22rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.projects-title {
  margin-top: 18rpx;
  color: #f7f9fc;
  font-size: 60rpx;
  font-weight: 700;
  line-height: 1.12;
}

.projects-summary {
  max-width: 620rpx;
  margin-top: 18rpx;
  color: rgba(237, 242, 251, 0.92);
  font-size: 26rpx;
  line-height: 1.82;
}

.projects-tabbar {
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
  flex-wrap: wrap;
}

.projects-tab {
  min-width: 136rpx;
  min-height: 58rpx;
  padding: 0 18rpx;
  color: #55637b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23rpx;
  font-weight: 600;
}

.projects-tab-active {
  border-radius: 999rpx;
  background: #e9eef8;
  color: #485291;
}

.project-stage {
  padding-top: 34rpx;
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

.section-title {
  margin-top: 8rpx;
  color: #1b2536;
  font-size: 44rpx;
  font-weight: 700;
}

.intro-band {
  background: linear-gradient(180deg, #fbfcff 0%, #f2f6fb 100%);
}

.project-intro-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24rpx;
}

.project-intro-copy {
  color: #667791;
  font-size: 27rpx;
  line-height: 1.92;
}

.project-metric-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18rpx;
  padding: 24rpx 0;
  border-top: 1rpx solid rgba(215, 224, 236, 0.9);
  border-bottom: 1rpx solid rgba(215, 224, 236, 0.9);
}

.project-metric {
  text-align: center;
}

.project-metric-label {
  color: #8390a4;
  font-size: 22rpx;
}

.project-metric-value {
  margin-top: 10rpx;
  color: #1b2536;
  font-size: 34rpx;
  font-weight: 700;
  word-break: break-all;
}

.showcase-band,
.funds-band {
  background: #ffffff;
}

.link-text {
  color: #5a67aa;
  font-size: 24rpx;
  font-weight: 600;
}

.showcase-stage {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.showcase-swiper {
  height: 492rpx;
  overflow: visible;
}

.showcase-swiper-item {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

.showcase-slide {
  position: relative;
  width: 100%;
  height: 436rpx;
  overflow: hidden;
  border-radius: 36rpx;
  background: #dde5f1;
  box-shadow: 0 14rpx 28rpx rgba(29, 42, 72, 0.08);
  transform: scale(0.88);
  opacity: 0.62;
  transition: transform 0.3s ease, opacity 0.3s ease, box-shadow 0.3s ease;
}

.showcase-slide-active {
  transform: scale(1);
  opacity: 1;
  box-shadow: 0 22rpx 44rpx rgba(29, 42, 72, 0.14);
}

.showcase-image,
.showcase-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.showcase-overlay {
  background: linear-gradient(180deg, rgba(10, 21, 28, 0.08) 0%, rgba(10, 21, 28, 0.78) 100%);
}

.showcase-copy {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
  padding: 32rpx;
}

.showcase-date {
  color: rgba(233, 238, 248, 0.84);
  font-size: 20rpx;
}

.showcase-title {
  margin-top: 14rpx;
  color: #f7f9fc;
  font-size: 36rpx;
  font-weight: 700;
  line-height: 1.32;
}

.showcase-desc {
  margin-top: 14rpx;
  color: rgba(236, 241, 250, 0.88);
  font-size: 24rpx;
  line-height: 1.74;
  max-width: 420rpx;
}

.showcase-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.showcase-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 999rpx;
  background: rgba(90, 103, 170, 0.18);
  transition: all 0.28s ease;
}

.showcase-dot-active {
  width: 34rpx;
  background: #5a67aa;
}

.funds-flow {
  display: flex;
  flex-direction: column;
}

.fund-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180rpx;
  gap: 20rpx;
  align-items: center;
  min-height: 132rpx;
  border-top: 1rpx solid #e6edf5;
}

.fund-row-main {
  padding: 20rpx 0;
}

.fund-row-side {
  text-align: right;
}

.fund-money {
  color: #485291;
  font-size: 28rpx;
  font-weight: 700;
  word-break: break-all;
}

.fund-money-label {
  margin-top: 8rpx;
  color: #8390a4;
  font-size: 21rpx;
}

.empty-state {
  padding: 46rpx 0 16rpx;
  color: #8390a4;
  font-size: 24rpx;
  text-align: center;
}
</style>
