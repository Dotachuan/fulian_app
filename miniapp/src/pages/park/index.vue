<template>
  <view class="page park-page">
    <view class="park-hero">
      <image class="park-hero-image" :src="heroImage" mode="aspectFill" />
      <view class="park-hero-overlay"></view>

      <view class="park-hero-topbar">
        <view class="park-brand">
          <image class="park-brand-logo" :src="foundationLogo" mode="aspectFit" />
          <view class="park-brand-texts">
            <view class="park-brand-name">福莲教育促进会</view>
            <view class="park-brand-sub">Fulian Education Foundation</view>
          </view>
        </view>
      </view>

      <view class="park-hero-copy">
        <view class="park-kicker">产业协作 · 公益联动</view>
        <view class="park-title">{{ park.title || '福莲产业园' }}</view>
        <view class="park-summary">{{ park.summary || defaultSummary }}</view>
      </view>
    </view>

    <view class="park-anchor-bar">
      <view v-for="item in anchors" :key="item.id" class="park-anchor-item" @click="jumpTo(item.id)">
        {{ item.label }}
      </view>
    </view>

    <view class="park-content">
      <view id="intro" class="section-band intro-band">
        <view class="section-head">
          <view>
            <view class="section-kicker">园区简介</view>
            <view class="section-title">关于福莲产业园</view>
          </view>
        </view>

        <view class="intro-layout">
          <view class="intro-copy">{{ park.content || defaultContent }}</view>
          <view class="intro-side">
            <view class="intro-side-block">
              <view class="intro-side-label">合作方向</view>
              <view class="intro-side-title">订单招商与产业协同</view>
              <view class="intro-side-text">依托华勤技术供应链资源，推动连城产业链、供应链企业协同聚集。</view>
            </view>
            <view class="intro-side-divider"></view>
            <view class="intro-side-block">
              <view class="intro-side-label">公益联动</view>
              <view class="intro-side-title">教育与医疗公益长效支持</view>
              <view class="intro-side-text">把产业发展与公益事业紧密连接起来，形成长期支撑机制。</view>
            </view>
          </view>
        </view>
      </view>

      <view id="links" class="section-band link-band">
        <view class="section-head">
          <view>
            <view class="section-kicker">相关链接</view>
            <view class="section-title">园区资讯与合作窗口</view>
          </view>
        </view>

        <view v-if="park.links?.length" class="link-stage">
          <view
            v-for="(item, index) in park.links.slice(0, 3)"
            :key="item.id"
            class="link-panel"
            :class="{ 'link-panel-offset': index === 1 }"
            @click="openLink(item)"
          >
            <image class="link-image" :src="item.image_url" mode="aspectFill" />
            <view class="link-overlay"></view>
            <view class="link-copy">
              <view class="link-date">{{ formatDate(item.published_at) }}</view>
              <view class="link-title">{{ item.title }}</view>
              <view class="link-desc">{{ item.summary || '点击查看相关资讯详情。' }}</view>
              <view class="link-arrow">→</view>
            </view>
          </view>
        </view>
        <view v-else class="empty-state">管理员暂未配置产业园链接</view>
      </view>

      <view id="news" class="section-band news-band">
        <view class="section-head">
          <view>
            <view class="section-kicker">相关新闻</view>
            <view class="section-title">资讯动态</view>
          </view>
        </view>

        <view v-if="park.news_items?.length" class="list-block">
          <view
            v-for="item in park.news_items"
            :key="item.id"
            class="list-item news-row"
            @click="openNews(item)"
          >
            <view class="news-row-main">
              <view class="list-title">{{ item.title }}</view>
              <view class="list-desc">{{ item.summary || '点击查看资讯详情。' }}</view>
              <view class="list-meta">{{ formatDate(item.published_at) }}</view>
            </view>
            <view class="news-row-tail">查看</view>
          </view>
        </view>
        <view v-else class="empty-state">暂无相关新闻</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import heroImage from '../../static/foundation-home-reference.jpeg'
import foundationLogo from '../../static/foundation-logo.jpg'
import { getPublicIndustrialPark } from '../../api/public'
import { openExternalLink } from '../../utils/external-link'
import { normalizeMediaUrl } from '../../utils/media'

const park = ref({ links: [], news_items: [] })

const anchors = [
  { id: 'intro', label: '简介' },
  { id: 'links', label: '链接' },
  { id: 'news', label: '资讯' },
]

const defaultSummary =
  '聚焦订单招商、产业协作与公益联动，持续展示福莲产业园的发展定位、合作进展与相关资讯。'

const defaultContent = `2024年5月2日，连城县人民政府、华勤技术股份有限公司、福莲教育促进会三方合作备忘录签订仪式举行，共同建设“福莲产业园”。华勤技术股份有限公司董事长邱文生，福莲教育促进会会长罗培新，福莲教育促进会秘书长吴菲、苏州高新区经发委副主任詹国辉、芜湖立德智兴半导体有限公司首席技术官李元雄，连城县领导蔡东阳、陈聚水、李霞，县直有关单位负责人，连城兴康成生物技术有限公司、昆山合兴源电子有限公司、广东省明科智能设备有限公司、东莞市数控刀具协会、广东华瑞德精密科技有限公司、福建省致锋精密科技有限公司、鼎泰高科技术股份有限公司、东莞市瑞山硬质合金刀具有限公司、深圳市准银科技有限公司、福建省龙勤智能设备有限公司、福建中成新材料有限公司、东莞市凯华环保新材料有限公司等华勤供应链相关企业负责人参加仪式。

为促进产业发展与公益事业的有效联结，助力福莲教育、医疗公益事业的兴旺长盛，推动连城革命老区高质量发展，连城县人民政府、华勤技术股份有限公司、福莲教育促进会三方达成一致合作意向，建设“福莲产业园”。“福莲产业园”入园企业享受《连城县“一园两区”鼓励投资工业项目优惠办法》及相关产业园追加政策。

2024年以来，连城县深化拓展“三争”行动，实施“135”工作思路，深入开展招商引资提效攻坚行动，乘时借势，不断完善招商引资工作模式，积极探索开展“订单招商”，发挥华勤技术等乡贤“头部企业”的支持引领作用，抢抓住建部对口支援、与中建海峡建立战略合作关系机遇，以订单换投资，促进产业链、供应链企业聚集。`

async function loadData() {
  const res = await getPublicIndustrialPark()
  park.value = {
    ...res,
    links: (res.links || []).map((item) => ({
      ...item,
      image_url: normalizeMediaUrl(item.image_url),
    })),
  }
}

function formatDate(value) {
  return value || '近期更新'
}

function jumpTo(id) {
  uni.pageScrollTo({ selector: `#${id}`, duration: 240 })
}

function openNews(item) {
  openExternalLink(item?.source_url, item?.title || '公众号推文')
}

function openLink(item) {
  openExternalLink(item?.target_url, item?.title || '公众号推文')
}

loadData().catch(() => {})
</script>

<style scoped>
.park-page {
  padding: 0 0 56rpx;
  background: linear-gradient(180deg, #f6f8fc 0%, #f9fbfe 100%);
}

.park-hero {
  position: relative;
  min-height: 820rpx;
  overflow: hidden;
}

.park-hero-image,
.park-hero-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.park-hero-overlay {
  background: linear-gradient(180deg, rgba(11, 21, 29, 0.12) 0%, rgba(11, 21, 29, 0.38) 38%, rgba(11, 21, 29, 0.78) 100%);
}

.park-hero-topbar,
.park-hero-copy {
  position: relative;
  z-index: 2;
  width: calc(100% - 56rpx);
  margin: 0 auto;
}

.park-hero-topbar {
  padding-top: 38rpx;
}

.park-brand {
  display: inline-flex;
  align-items: center;
  gap: 14rpx;
  padding: 14rpx 18rpx;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18rpx);
  border-radius: 18rpx;
}

.park-brand-logo {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: #ffffff;
}

.park-brand-name {
  color: #1b2536;
  font-size: 27rpx;
  font-weight: 700;
}

.park-brand-sub {
  margin-top: 4rpx;
  color: #8390a4;
  font-size: 19rpx;
}

.park-hero-copy {
  padding-top: 244rpx;
}

.park-kicker {
  color: rgba(232, 237, 248, 0.86);
  font-size: 22rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.park-title {
  margin-top: 18rpx;
  color: #f7f9fc;
  font-size: 60rpx;
  font-weight: 700;
  line-height: 1.12;
}

.park-summary {
  max-width: 620rpx;
  margin-top: 18rpx;
  color: rgba(237, 242, 251, 0.92);
  font-size: 26rpx;
  line-height: 1.82;
}

.park-anchor-bar {
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

.park-anchor-item {
  min-width: 116rpx;
  min-height: 58rpx;
  padding: 0 16rpx;
  color: #55637b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23rpx;
  font-weight: 600;
}

.park-content {
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

.intro-layout {
  display: grid;
  grid-template-columns: 1.25fr 0.75fr;
  gap: 30rpx;
}

.intro-copy {
  color: #667791;
  font-size: 27rpx;
  line-height: 1.92;
  white-space: pre-wrap;
}

.intro-side {
  padding: 10rpx 0 0 24rpx;
  border-left: 2rpx solid rgba(72, 82, 145, 0.18);
}

.intro-side-label {
  color: #5a67aa;
  font-size: 21rpx;
  font-weight: 700;
  letter-spacing: 1.5rpx;
}

.intro-side-title {
  margin-top: 14rpx;
  color: #1b2536;
  font-size: 32rpx;
  font-weight: 700;
}

.intro-side-text {
  margin-top: 10rpx;
  color: #6f7f98;
  font-size: 24rpx;
  line-height: 1.84;
}

.intro-side-divider {
  width: 100%;
  height: 1rpx;
  margin: 24rpx 0;
  background: rgba(215, 224, 236, 0.9);
}

.link-band,
.news-band {
  background: #ffffff;
}

.link-stage {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20rpx;
}

.link-panel {
  position: relative;
  min-height: 360rpx;
  overflow: hidden;
  border-radius: 30rpx;
  background: #dde5f1;
}

.link-panel-offset {
  margin-top: 40rpx;
}

.link-image,
.link-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.link-overlay {
  background: linear-gradient(180deg, rgba(10, 21, 28, 0.08) 0%, rgba(10, 21, 28, 0.78) 100%);
}

.link-copy {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
  padding: 28rpx;
}

.link-date {
  color: rgba(233, 238, 248, 0.84);
  font-size: 20rpx;
}

.link-title {
  margin-top: 12rpx;
  color: #f7f9fc;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.34;
}

.link-desc {
  margin-top: 12rpx;
  color: rgba(236, 241, 250, 0.88);
  font-size: 23rpx;
  line-height: 1.72;
}

.link-arrow {
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

.news-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 96rpx;
  gap: 18rpx;
  align-items: center;
}

.news-row-tail {
  color: #5a67aa;
  font-size: 23rpx;
  text-align: right;
}

.empty-state {
  padding: 46rpx 0 16rpx;
  color: #8390a4;
  font-size: 24rpx;
  text-align: center;
}
</style>
