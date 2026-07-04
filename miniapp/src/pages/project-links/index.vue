<template>
  <view class="page">
    <view class="page-shell">
      <view class="news-header">
        <view class="section-kicker">项目资讯</view>
        <view class="section-title">{{ pageTitle }}</view>
        <view class="section-subtitle">当前仅展示该项目板块下的资讯内容，不与其他项目混合。</view>
      </view>

      <view v-if="items.length" class="project-link-list">
        <view
          v-for="item in items"
          :key="item.id"
          class="project-link-row"
          @click="openLink(item)"
        >
          <image
            v-if="item.image_url"
            class="project-link-thumb"
            :src="item.image_url"
            mode="aspectFill"
          />
          <view v-else class="project-link-thumb project-link-thumb-fallback"></view>

          <view class="project-link-main">
            <view class="project-link-date">{{ item.published_at || '近期更新' }}</view>
            <view class="list-title">{{ item.title }}</view>
            <view class="list-desc">{{ item.summary || '点击查看完整资讯。' }}</view>
          </view>

          <view class="project-link-tail">查看</view>
        </view>
      </view>

      <view v-else-if="loading" class="empty-block">正在加载资讯...</view>
      <view v-else-if="errorText" class="empty-block">{{ errorText }}</view>
      <view v-else class="empty-block">当前板块暂未配置更多资讯</view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { getPublicProjectLinks } from '../../api/public'
import { openExternalLink } from '../../utils/external-link'
import { normalizeMediaUrl } from '../../utils/media'

const items = ref([])
const loading = ref(false)
const errorText = ref('')
const pageTitle = ref('项目资讯')
const sectionKey = ref('')

function parseCurrentPageOptions() {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1]
  const directOptions = current?.options || {}
  if (directOptions.section_key || directOptions.title) {
    return directOptions
  }

  const fullPath = current?.$page?.fullPath || ''
  const queryString = fullPath.includes('?') ? fullPath.split('?')[1] : ''
  if (!queryString) return {}

  const params = new URLSearchParams(queryString)
  return {
    section_key: params.get('section_key') || '',
    title: params.get('title') || '',
  }
}

function inferSectionKeyByTitle(title) {
  if (title.includes('主基金')) return 'main'
  if (title.includes('医学')) return 'medical'
  if (title.includes('公益活动')) return 'activity'
  if (title.includes('专项')) return 'special'
  return ''
}

function applyPayload(payload) {
  if (!payload || typeof payload !== 'object') return false
  const payloadItems = Array.isArray(payload.items) ? payload.items : []
  if (!payloadItems.length) return false

  pageTitle.value = payload.title || '项目资讯'
  sectionKey.value = payload.section_key || inferSectionKeyByTitle(pageTitle.value)
  items.value = payloadItems.map((item) => ({
    ...item,
    image_url: normalizeMediaUrl(item.image_url),
  }))
  errorText.value = ''
  loading.value = false
  uni.setNavigationBarTitle({ title: pageTitle.value })
  return true
}

function readQuery(options = {}) {
  const cachedPayload = uni.getStorageSync('project_links_view_payload')
  if (applyPayload(cachedPayload)) {
    return
  }

  const merged = {
    ...parseCurrentPageOptions(),
    ...(options || {}),
  }

  const rawTitle = merged.title || '项目资讯'
  pageTitle.value = decodeURIComponent(rawTitle)
  sectionKey.value = merged.section_key || inferSectionKeyByTitle(pageTitle.value)

  if (pageTitle.value) {
    uni.setNavigationBarTitle({ title: pageTitle.value })
  }
}

async function loadData() {
  const cachedPayload = uni.getStorageSync('project_links_view_payload')
  if (applyPayload(cachedPayload)) {
    return
  }

  loading.value = true
  errorText.value = ''

  if (!sectionKey.value) {
    items.value = []
    loading.value = false
    errorText.value = '未识别到当前项目板块参数'
    return
  }

  try {
    const res = await getPublicProjectLinks({
      section_key: sectionKey.value,
      page: 1,
      page_size: 100,
    })
    items.value = (res.items || []).map((item) => ({
      ...item,
      image_url: normalizeMediaUrl(item.image_url),
    }))
  } catch (error) {
    items.value = []
    errorText.value = error?.detail || '资讯加载失败'
  } finally {
    loading.value = false
  }
}

function openLink(item) {
  openExternalLink(item?.target_url, item?.title || '公众号推文')
}

onLoad((options) => {
  readQuery(options || {})
  loadData()
})

onShow(() => {
  if (!items.value.length || !sectionKey.value) {
    readQuery()
    if (!items.value.length && sectionKey.value) {
      loadData()
    }
  }
})
</script>

<style scoped>
.news-header {
  padding: 8rpx 0 30rpx;
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

.section-subtitle {
  margin-top: 14rpx;
  color: #6f7f98;
  font-size: 25rpx;
  line-height: 1.8;
}

.project-link-list {
  display: flex;
  flex-direction: column;
}

.project-link-row {
  display: grid;
  grid-template-columns: 180rpx minmax(0, 1fr) 82rpx;
  gap: 18rpx;
  align-items: center;
  padding: 24rpx 0;
}

.project-link-row + .project-link-row {
  border-top: 1rpx solid #e6edf5;
}

.project-link-thumb {
  width: 180rpx;
  height: 136rpx;
  border-radius: 18rpx;
  background: #dde5f1;
}

.project-link-thumb-fallback {
  background: linear-gradient(145deg, #475291 0%, #5d69ab 100%);
}

.project-link-main {
  min-width: 0;
}

.project-link-date {
  color: #8390a4;
  font-size: 20rpx;
}

.project-link-tail {
  color: #5a67aa;
  font-size: 23rpx;
  text-align: right;
}
</style>
