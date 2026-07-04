<template>
  <view class="page about-page">
    <view class="about-hero">
      <image class="about-hero-image" :src="heroImage" mode="aspectFill" />
      <view class="about-hero-overlay"></view>
      <view class="about-hero-inner">
        <view class="about-hero-kicker">公开信息</view>
        <view class="about-hero-title">关于福莲</view>
        <view class="about-hero-desc">围绕产业协作、公益项目、财务公示与治理信息，形成一套清晰、连续、便于查阅的公开界面。</view>
      </view>
    </view>

    <view class="about-layout">
      <view class="about-nav">
        <view
          v-for="section in sections"
          :key="section.key"
          class="about-nav-item"
          :class="{ 'about-nav-item-active': activeSection === section.key }"
          @click="activeSection = section.key"
        >
          <view class="about-nav-texts">
            <view class="about-nav-title">{{ section.title }}</view>
            <view class="about-nav-note">{{ section.note }}</view>
          </view>
          <view class="about-nav-arrow">→</view>
        </view>
      </view>

      <view class="about-main">
        <view class="about-section-head">
          <view class="section-kicker">{{ activeSectionData.kicker }}</view>
          <view class="about-section-title">{{ activeSectionData.title }}</view>
          <view class="about-section-summary">{{ activeSectionData.summary }}</view>
        </view>

        <view class="about-feature-band">
          <view class="about-feature-index">{{ activeSectionData.index }}</view>
          <view class="about-feature-copy">
            <view class="about-feature-title">{{ activeSectionData.featureTitle }}</view>
            <view class="about-feature-desc">{{ activeSectionData.featureDesc }}</view>
          </view>
          <view
            class="about-feature-action"
            :class="{ 'about-feature-action-disabled': activeSectionData.pending }"
            @click="openSection(activeSectionData)"
          >
            {{ activeSectionData.actionText }}
          </view>
        </view>

        <view class="about-detail-list">
          <view
            v-for="item in activeSectionData.items"
            :key="item.title"
            class="about-detail-row"
            @click="openRow(item, activeSectionData)"
          >
            <view class="about-detail-main">
              <view class="row-between">
                <view class="list-title">{{ item.title }}</view>
                <text v-if="item.tag" class="about-inline-tag">{{ item.tag }}</text>
              </view>
              <view class="list-desc">{{ item.desc }}</view>
            </view>
            <view class="about-detail-tail">{{ item.tail || '查看' }}</view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import heroImage from '../../static/foundation-home-reference.jpeg'

const activeSection = ref('park')

const sections = [
  {
    key: 'park',
    title: '福莲产业园',
    note: '介绍与资讯',
    kicker: '模块一',
    index: '01',
    summary: '集中展示福莲产业园的定位、合作方向与相关资讯，作为机构协作与资源联动的重要窗口。',
    featureTitle: '产业园介绍与新闻入口',
    featureDesc: '当前版本先开放介绍与相关资讯列表，后续可继续扩展合作项目与阶段性进展展示。',
    actionText: '进入页面',
    url: '/pages/park/index',
    items: [
      { title: '产业园简介', desc: '查看福莲产业园的定位说明与发展方向。', tag: '已接入', tail: '进入', url: '/pages/park/index' },
      { title: '相关资讯', desc: '查看与产业园相关的机构新闻与合作动态。', tag: '已接入', tail: '查看', url: '/pages/park/index' },
    ],
  },
  {
    key: 'projects',
    title: '公益项目进展',
    note: '四类固定板块',
    kicker: '模块二',
    index: '02',
    summary: '围绕主基金、医学基金、公益活动与专项基金四个板块，统一展示资金概况与相关新闻。',
    featureTitle: '公益项目进展聚合页',
    featureDesc: '集中查看四类板块的资金简介、收入支出与相关资讯入口，便于统一浏览。',
    actionText: '进入页面',
    url: '/pages/projects/index',
    items: [
      { title: '福莲教育主基金', desc: '查看主基金概况、资金使用与相关资讯。', tag: '已接入', tail: '进入', url: '/pages/projects/index' },
      { title: '福莲医学基金', desc: '查看医学基金的资金情况与动态。', tag: '已接入', tail: '进入', url: '/pages/projects/index' },
      { title: '福莲公益活动 / 专项基金', desc: '统一查看活动与专项基金的资金及资讯。', tag: '已接入', tail: '进入', url: '/pages/projects/index' },
    ],
  },
  {
    key: 'finance',
    title: '财务公示',
    note: '当前已可访问',
    kicker: '模块三',
    index: '03',
    summary: '登录会员后可查看基金列表、当前余额与收支明细，是关于福莲栏目中的核心公开部分。',
    featureTitle: '基金收支与项目明细',
    featureDesc: '当前已接入基金列表与单项基金明细查询，并统一替换了旧的导入文案。',
    actionText: '进入公示',
    url: '/pages/funds/index',
    items: [
      { title: '基金列表', desc: '查看当前可公开展示的基金项目与概况信息。', tag: '已接入', tail: '进入', url: '/pages/funds/index' },
      { title: '收支明细', desc: '按基金维度查看收入、支出与余额情况。', tag: '已接入', tail: '查看', url: '/pages/funds/index' },
    ],
  },
  {
    key: 'org',
    title: '组织架构',
    note: '治理结构展示',
    kicker: '模块四',
    index: '04',
    summary: '用于展示机构治理结构、职责分工与协作关系，后续适合做成清晰的层级说明页面。',
    featureTitle: '治理结构与职责分工',
    featureDesc: '当前先保留结构位，后续可进一步接入组织架构图与岗位职责说明。',
    actionText: '建设中',
    pending: true,
    items: [
      { title: '治理层结构', desc: '展示理事、监事与执行层的基本结构。', tag: '预留', tail: '待上线' },
      { title: '职责分工', desc: '说明主要职责分工与协作关系。', tag: '预留', tail: '待上线' },
    ],
  },
  {
    key: 'supervision',
    title: '监察报告',
    note: '监督与报告公开',
    kicker: '模块五',
    index: '05',
    summary: '用于后续公开监督材料、监察说明与阶段报告，使机构治理信息更加完整。',
    featureTitle: '监督与监察公开窗口',
    featureDesc: '当前先保留结构位，后续可接入监察报告与监督摘要，形成长期公开页面。',
    actionText: '建设中',
    pending: true,
    items: [
      { title: '监察说明', desc: '介绍监督机制、范围与公开口径。', tag: '预留', tail: '待上线' },
      { title: '阶段报告', desc: '用于发布监察报告与监督摘要。', tag: '预留', tail: '待上线' },
    ],
  },
]

const activeSectionData = computed(() => sections.find((item) => item.key === activeSection.value) || sections[0])

function openSection(section) {
  if (section.pending) {
    uni.showToast({ title: '该模块正在建设中', icon: 'none' })
    return
  }
  if (section.url) {
    uni.navigateTo({ url: section.url })
  }
}

function openRow(item, section) {
  if (item.url) {
    uni.navigateTo({ url: item.url })
    return
  }
  openSection(section)
}
</script>

<style scoped>
.about-page {
  padding: 0 0 60rpx;
  background: #f7f9fc;
}

.about-hero {
  position: relative;
  min-height: 420rpx;
  overflow: hidden;
}

.about-hero-image,
.about-hero-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.about-hero-overlay {
  background: linear-gradient(180deg, rgba(17, 22, 28, 0.34) 0%, rgba(17, 22, 28, 0.6) 100%);
}

.about-hero-inner {
  position: relative;
  z-index: 2;
  width: calc(100% - 72rpx);
  margin: 0 auto;
  padding-top: 182rpx;
}

.about-hero-kicker {
  color: rgba(232, 237, 248, 0.84);
  font-size: 22rpx;
  letter-spacing: 2rpx;
}

.about-hero-title {
  margin-top: 14rpx;
  color: #f7f9fc;
  font-size: 62rpx;
  font-weight: 700;
}

.about-hero-desc {
  max-width: 620rpx;
  margin-top: 16rpx;
  color: rgba(237, 242, 251, 0.9);
  font-size: 25rpx;
  line-height: 1.88;
}

.about-layout {
  display: grid;
  grid-template-columns: 240rpx minmax(0, 1fr);
  background: #fbfcff;
  border-top: 1rpx solid rgba(214, 224, 238, 0.5);
  border-bottom: 1rpx solid rgba(214, 224, 238, 0.4);
}

.about-nav {
  padding: 20rpx 0;
  background: #f2f6fb;
  border-right: 1rpx solid rgba(214, 224, 238, 0.56);
}

.about-nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  min-height: 110rpx;
  padding: 0 20rpx 0 26rpx;
  border-left: 6rpx solid transparent;
}

.about-nav-item + .about-nav-item {
  border-top: 1rpx solid rgba(223, 231, 242, 0.82);
}

.about-nav-item-active {
  background: #ffffff;
  border-left-color: #5a67aa;
}

.about-nav-title {
  color: #1b2536;
  font-size: 28rpx;
  font-weight: 700;
}

.about-nav-note {
  margin-top: 8rpx;
  color: #8390a4;
  font-size: 21rpx;
}

.about-nav-arrow {
  color: #7a87bb;
  font-size: 24rpx;
}

.about-main {
  padding: 36rpx 30rpx 44rpx;
  background: #ffffff;
}

.about-section-head {
  padding-bottom: 24rpx;
  border-bottom: 1rpx solid rgba(228, 235, 244, 0.96);
}

.about-section-title {
  margin-top: 10rpx;
  color: #1b2536;
  font-size: 50rpx;
  font-weight: 700;
}

.about-section-summary,
.about-feature-desc {
  margin-top: 16rpx;
  color: #68778f;
  font-size: 25rpx;
  line-height: 1.88;
}

.about-feature-band {
  display: grid;
  grid-template-columns: 108rpx minmax(0, 1fr) 168rpx;
  gap: 22rpx;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid rgba(228, 235, 244, 0.96);
}

.about-feature-index {
  color: #5a67aa;
  font-size: 52rpx;
  font-weight: 700;
}

.about-feature-title {
  color: #1b2536;
  font-size: 34rpx;
  font-weight: 700;
}

.about-feature-action {
  min-height: 76rpx;
  padding: 0 16rpx;
  border: 1rpx solid rgba(90, 103, 170, 0.34);
  color: #485291;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 600;
}

.about-feature-action-disabled {
  opacity: 0.62;
}

.about-detail-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 96rpx;
  gap: 20rpx;
  align-items: center;
  min-height: 138rpx;
  border-bottom: 1rpx solid rgba(229, 236, 245, 0.96);
}

.about-detail-tail {
  color: #5a67aa;
  font-size: 23rpx;
  text-align: right;
}

.about-inline-tag {
  color: #5a67aa;
  font-size: 21rpx;
  font-weight: 600;
}
</style>
