<template>
  <view class="page home-page">
    <view class="hero-stage">
      <image class="hero-image" :src="heroImage" mode="aspectFill" />
      <view class="hero-overlay"></view>

      <view class="hero-topbar">
        <view class="brand-block">
          <image class="brand-mark" :src="foundationLogo" mode="aspectFit" />
          <view class="brand-texts">
            <view class="brand-name">福莲教育促进会</view>
            <view class="brand-sub">Fulian Education Foundation</view>
          </view>
        </view>
      </view>

      <view class="hero-copy">
        <view class="hero-kicker">教育发展 · 公益透明</view>
        <view class="hero-heading">花开福莲,香逸四海</view>
        <view class="hero-summary">
          您的福业，福莲的未来。
          <text class="hero-summary-break">福莲欢迎、并期待着您的加入！</text>
        </view>
      </view>
    </view>

    <view class="anchor-bar">
      <view
        v-for="item in sectionAnchors"
        :key="item.id"
        class="anchor-item"
        @click="jumpTo(item.id)"
      >
        {{ item.label }}
      </view>
    </view>

    <view class="home-content">
      <view id="intro" class="section-band intro-band">
        <view class="section-head">
          <view>
            <view class="section-title home-title">关于福莲</view>
          </view>
        </view>

        <view class="intro-layout">
          <view class="intro-main">
            <view class="intro-title">{{ aboutTitle }}</view>
            <view class="intro-text">{{ aboutSummary }}</view>
            <view class="intro-actions">
            </view>
          </view>

          <view class="intro-side">
            <view class="side-block">
              <view class="side-title">{{ missionTitle }}</view>
              <view class="side-text">{{ missionSummary }}</view>
            </view>
            <view class="side-divider"></view>
            <view class="side-block">
              <view class="side-title">{{ visionTitle }}</view>
              <view class="side-text">{{ visionSummary }}</view>
            </view>
          </view>
        </view>
      </view>

      <view id="news" class="section-band news-band">
        <view class="section-head">
          <view>
            <view class="section-title home-title">新闻动态</view>
          </view>
          <text class="link-text" @click="openNewsList">全部新闻</text>
        </view>

        <view v-if="newsFeatureItems.length" class="news-layout">
          <view
            v-for="(item, index) in newsFeatureItems"
            :key="item.id"
            class="news-panel"
            :class="{ 'news-panel-accent': index === 1 }"
            @click="openNews(item)"
          >
            <image
              v-if="item.cover_url"
              class="news-panel-image"
              :src="item.cover_url"
              mode="aspectFill"
            />
            <view v-else class="news-panel-image news-panel-fallback"></view>
            <view class="news-panel-overlay"></view>
            <view class="news-panel-content">
              <view class="news-date">{{ formatDate(item.published_at) }}</view>
              <view class="news-title">{{ item.title }}</view>
              <view class="news-summary">{{ item.summary || '点击查看完整内容。' }}</view>
              <view class="news-arrow">→</view>
            </view>
          </view>
        </view>
        <view v-else class="empty-state">暂未获取到新闻内容</view>
      </view>

      <view id="activities" class="section-band activity-band">
        <view class="section-head">
          <view>
            <view class="section-title home-title">近期活动</view>
          </view>
        </view>

        <view class="activity-tabs">
          <view
            v-for="(item, index) in activityItems"
            :key="`${item.title}-${index}`"
            class="activity-tab"
            :class="{ 'activity-tab-active': index === activeActivityIndex }"
            @click="activeActivityIndex = index"
          >
            {{ item.tag }}
          </view>
        </view>

        <view class="activity-stage">
          <view class="activity-ghost"></view>
          <view class="activity-focus">
            <image
              v-if="currentActivity.image"
              class="activity-image"
              :src="currentActivity.image"
              mode="aspectFill"
            />
            <view v-else class="activity-image activity-image-fallback"></view>
            <view class="activity-overlay"></view>
            <view class="activity-copy">
              <view class="activity-tagline">{{ currentActivity.tag }}</view>
              <view class="activity-title">{{ currentActivity.title }}</view>
              <view class="activity-desc">{{ currentActivity.desc }}</view>
              <view class="button-secondary activity-btn" @click="openActivityTarget(currentActivity)">
                {{ currentActivity.actionText }}
              </view>
            </view>
          </view>
          <view class="activity-ghost"></view>
        </view>
      </view>

      <view id="notices" class="section-band notice-band">
        <view class="section-head">
          <view>
            <view class="section-title home-title">公告与提醒</view>
          </view>
          <text class="link-text" @click="openNoticeList">全部公告</text>
        </view>

        <view v-if="noticeItems.length" class="notice-flow">
          <view
            v-for="item in noticeItems"
            :key="item.id"
            class="notice-row"
            @click="openNotice(item.id)"
          >
            <view class="notice-line"></view>
            <view class="notice-content">
              <view class="row-between">
                <view class="list-title">{{ item.title }}</view>
                <text v-if="item.is_pinned" class="badge badge-warning">置顶</text>
              </view>
              <view class="list-desc">{{ item.summary || '点击查看公告详情。' }}</view>
              <view class="list-meta">{{ formatDate(item.published_at) }}</view>
            </view>
          </view>
        </view>
        <view v-else class="empty-state">暂未获取到公告内容</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { getPublicNews, getPublicNotices, getPublicSiteContent } from '../../api/public'
import { openExternalLink } from '../../utils/external-link'
import { normalizeMediaUrl } from '../../utils/media'
import heroImage from '../../static/home-hero-lotus.jpg'
import foundationLogo from '../../static/foundation-logo.jpg'

const newsItems = ref([])
const noticeItems = ref([])
const siteContents = ref([])
const activeActivityIndex = ref(0)

const sectionAnchors = [
  { id: 'intro', label: '简介' },
  { id: 'news', label: '新闻' },
  { id: 'activities', label: '活动' },
  { id: 'notices', label: '公告' },
]


const aboutItem = computed(() => siteContents.value.find((item) => item.key === 'about') || {})
const missionItem = computed(() => siteContents.value.find((item) => item.key === 'mission') || {})
const visionItem = computed(() => siteContents.value.find((item) => item.key === 'vision') || {})

const aboutTitle = computed(() => aboutItem.value.title || '机构简介')
const aboutSummary = computed(
  () =>
    aboutItem.value.summary ||
    aboutItem.value.content ||
    '福莲教育促进会持续围绕教育公益、校友协作与长期资助展开服务与行动。'
)
const missionTitle = computed(() => missionItem.value.title || '使命')
const missionSummary = computed(
  () => missionItem.value.summary || missionItem.value.content || '以长期行动支持教育发展。'
)
const visionTitle = computed(() => visionItem.value.title || '愿景')
const visionSummary = computed(
  () => visionItem.value.summary || visionItem.value.content || '连接更多力量，形成可持续的公益支持。'
)

const newsFeatureItems = computed(() =>
  newsItems.value.slice(0, 2).map((item) => ({
    ...item,
    cover_url: normalizeMediaUrl(item.cover_url),
  }))
)
const activityItems = computed(() => {
  const derived = newsItems.value.slice(0, 3).map((item, index) => ({
    tag: ['近期活动', '项目走访', '会员交流'][index] || '福莲活动',
    title: item.title,
    desc: item.summary || '围绕福莲教育公益与会员服务的近期活动内容。',
    image: normalizeMediaUrl(item.cover_url) || heroImage,
    type: 'news',
    targetUrl: item.source_url,
    targetTitle: item.title,
    actionText: '查看详情',
  }))

  if (derived.length) return derived

  return [
    {
      tag: '近期活动',
      title: '活动内容筹备中',
      desc: '当前版本先预留活动展示位，后续接入独立活动数据后可直接切换为真实内容。',
      image: heroImage,
      type: 'placeholder',
      actionText: '查看公告',
    },
  ]
})

const currentActivity = computed(
  () => activityItems.value[activeActivityIndex.value] || activityItems.value[0] || {}
)

function formatDate(value) {
  if (!value) return '近期更新'
  return String(value)
}

async function loadData() {
  try {
    const [newsRes, noticeRes, siteRes] = await Promise.all([
      getPublicNews({ page: 1, page_size: 6, featured_only: false }),
      getPublicNotices({ page: 1, page_size: 4 }),
      getPublicSiteContent(),
    ])
    newsItems.value = newsRes.items || []
    noticeItems.value = noticeRes.items || []
    siteContents.value = siteRes || []
    activeActivityIndex.value = 0
  } catch (error) {
    newsItems.value = []
    noticeItems.value = []
    siteContents.value = []
    activeActivityIndex.value = 0
  }
}

function jumpTo(id) {
  uni.pageScrollTo({
    selector: `#${id}`,
    duration: 240,
  })
}

function goAbout() {
  uni.switchTab({ url: '/pages/about/index' })
}

function openNews(item) {
  openExternalLink(item?.source_url, item?.title || '公众号推文')
}

function openNewsList() {
  uni.navigateTo({ url: '/pages/news/index' })
}

function openActivityTarget(item) {
  if (item.type === 'news' && item.targetUrl) {
    openExternalLink(item.targetUrl, item.targetTitle || '公众号推文')
    return
  }
  openNoticeList()
}

function openNotice(id) {
  uni.navigateTo({ url: `/pages/notice-detail/index?id=${id}` })
}

function openNoticeList() {
  uni.navigateTo({ url: '/pages/notices/index' })
}

loadData().catch(() => {})
</script>

<style scoped>
.home-page {
  padding: 0 0 56rpx;
  background: linear-gradient(180deg, #f6f8fc 0%, #f9fbfe 100%);
}

.hero-stage {
  position: relative;
  min-height: 860rpx;
  overflow: hidden;
}

.hero-image,
.hero-overlay {
  position: absolute;
  inset: 0;
}

.hero-image {
  width: 100%;
  height: 100%;
}

.hero-overlay {
  background:
    linear-gradient(180deg, rgba(11, 21, 29, 0.1) 0%, rgba(11, 21, 29, 0.34) 40%, rgba(11, 21, 29, 0.76) 100%);
}

.hero-topbar,
.hero-copy {
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
  padding-top: 38rpx;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14rpx;
  padding: 14rpx 18rpx;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(18rpx);
  border-radius: 18rpx;
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

.hero-copy {
  padding-top: 246rpx;
}

.hero-kicker {
  color: rgba(232, 237, 248, 0.86);
  font-size: 22rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.hero-heading {
  max-width: 580rpx;
  margin-top: 18rpx;
  color: #f7f9fc;
  font-size: 60rpx;
  font-weight: 700;
  line-height: 1.12;
}

.hero-summary {
  max-width: 590rpx;
  margin-top: 18rpx;
  color: rgba(237, 242, 251, 0.9);
  font-size: 26rpx;
  line-height: 1.84;
}

.hero-summary-break {
  display: block;
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
  padding: 34rpx 0 0;
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
  background: linear-gradient(180deg, #fbfcff 0%, #f2f6fb 100%);
}

.intro-layout {
  display: grid;
  grid-template-columns: 1.24fr 0.76fr;
  gap: 30rpx;
  align-items: start;
}

.intro-main {
  padding: 12rpx 0 0;
}

.intro-title {
  max-width: 470rpx;
  color: #1b2536;
  font-size: 50rpx;
  font-weight: 700;
  line-height: 1.16;
}

.intro-text {
  max-width: 520rpx;
  margin-top: 20rpx;
  color: #667791;
  font-size: 27rpx;
  line-height: 1.92;
}

.intro-actions {
  display: flex;
  gap: 14rpx;
  max-width: 420rpx;
  margin-top: 30rpx;
}

.intro-btn {
  flex: 1;
}

.intro-side {
  padding: 10rpx 0 0 24rpx;
  border-left: 2rpx solid rgba(72, 82, 145, 0.18);
}

.side-block + .side-block {
  margin-top: 26rpx;
}

.side-divider {
  width: 100%;
  height: 1rpx;
  margin-top: 24rpx;
  background: rgba(215, 224, 236, 0.9);
}

.side-kicker {
  color: #5a67aa;
  font-size: 21rpx;
  font-weight: 700;
  letter-spacing: 1.5rpx;
}

.side-title {
  margin-top: 14rpx;
  color: #1b2536;
  font-size: 32rpx;
  font-weight: 700;
}

.side-text {
  margin-top: 10rpx;
  color: #6f7f98;
  font-size: 24rpx;
  line-height: 1.84;
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
  background: linear-gradient(180deg, rgba(10, 21, 28, 0.1) 0%, rgba(10, 21, 28, 0.8) 100%);
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
  margin-top: 12rpx;
  color: #f7f9fc;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.34;
}

.news-summary {
  margin-top: 12rpx;
  color: rgba(236, 241, 250, 0.88);
  font-size: 23rpx;
  line-height: 1.72;
}

.news-arrow {
  width: 72rpx;
  height: 72rpx;
  margin-top: 22rpx;
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
  background: linear-gradient(90deg, rgba(11, 24, 31, 0.72) 0%, rgba(11, 24, 31, 0.16) 66%, rgba(11, 24, 31, 0.06) 100%);
}

.activity-copy {
  position: relative;
  z-index: 2;
  max-width: 380rpx;
  padding: 42rpx 38rpx;
  color: #f7f9fc;
}

.activity-tagline {
  color: rgba(233, 238, 248, 0.84);
  font-size: 21rpx;
  font-weight: 700;
}

.activity-title {
  margin-top: 14rpx;
  font-size: 48rpx;
  font-weight: 700;
  line-height: 1.16;
}

.activity-desc {
  margin-top: 16rpx;
  color: rgba(236, 241, 250, 0.88);
  font-size: 24rpx;
  line-height: 1.84;
}

.activity-btn {
  width: 188rpx;
  margin-top: 24rpx;
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
