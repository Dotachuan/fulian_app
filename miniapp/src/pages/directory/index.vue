<template>
  <view class="page directory-page">
    <view class="directory-header">
      <view class="directory-title">会员通讯录</view>
      <view class="directory-subtitle">仅展示姓名、工作单位、常驻地与会员身份，不公开电话等隐私字段。</view>
    </view>

    <view v-if="!loggedIn" class="directory-state">
      <view class="directory-state-title">请先登录</view>
      <view class="directory-state-desc">登录后可按姓名或常驻地查询会员基础公开信息。</view>
      <view class="button-primary directory-state-action" @click="goLogin">去登录</view>
    </view>

    <template v-else>
      <view class="directory-toolbar">
        <view class="directory-tabs">
          <view
            v-for="tab in searchTabs"
            :key="tab.key"
            class="directory-tab"
            :class="{ 'directory-tab-active': activeTab === tab.key }"
            @click="switchTab(tab.key)"
          >
            {{ tab.label }}
          </view>
        </view>

        <view class="directory-search">
          <view class="search-icon">
            <view class="search-icon-circle"></view>
            <view class="search-icon-handle"></view>
          </view>
          <input
            v-model="keyword"
            class="directory-search-input"
            :placeholder="activeTab === 'name' ? '输入姓名进行查询' : '输入常驻地进行查询'"
            @confirm="loadData"
          />
          <view class="search-action" @click="loadData">查询</view>
        </view>
      </view>

      <view class="directory-meta">
        <view class="directory-count">检索结果（{{ items.length }}人）</view>
        <view v-if="loading" class="directory-loading">加载中...</view>
      </view>

      <view v-if="items.length" class="directory-main">
        <view class="directory-groups">
          <view
            v-for="group in groupedItems"
            :id="`group-${group.label}`"
            :key="group.label"
            class="directory-group"
          >
            <view class="directory-group-label">{{ group.label }}</view>

            <view
              v-for="item in group.items"
              :key="item.id"
              class="directory-row"
              @click="openDetail(item)"
            >
              <view class="directory-avatar">
                <image
                  v-if="item.avatar_url"
                  class="directory-avatar-image"
                  :src="item.avatar_url"
                  mode="aspectFill"
                />
                <view v-else class="directory-avatar-text">{{ getAvatarText(item.name) }}</view>
              </view>

              <view class="directory-copy">
                <view class="row-between">
                  <view class="directory-name">{{ item.name || '未命名会员' }}</view>
                  <text class="badge" :class="levelBadgeClass(item.member_level)">{{ item.member_level_label }}</text>
                </view>
                <view class="directory-unit">{{ item.work_unit || '未填写工作单位' }}</view>
                <view class="directory-city">{{ item.resident_city || '未填写常驻地' }}</view>
              </view>

              <view class="directory-action">→</view>
            </view>
          </view>
        </view>

        <view class="directory-rail">
          <view
            v-for="group in groupedItems"
            :key="group.label"
            class="directory-rail-item"
            @click="jumpToGroup(group.label)"
          >
            {{ group.label }}
          </view>
        </view>
      </view>

      <view v-else-if="!loading" class="directory-empty">暂无匹配会员</view>

      <view v-if="detailVisible && activeMember" class="directory-detail-mask" @click="closeDetail">
        <view class="directory-detail" @click.stop>
          <view class="directory-detail-handle"></view>
          <view class="directory-detail-hero">
            <view class="directory-detail-avatar">
              <image
                v-if="activeMember.avatar_url"
                class="directory-avatar-image"
                :src="activeMember.avatar_url"
                mode="aspectFill"
              />
              <template v-else>{{ getAvatarText(activeMember.name) }}</template>
            </view>
            <view class="directory-detail-main">
              <view class="directory-detail-name">{{ activeMember.name || '未命名会员' }}</view>
              <view class="directory-detail-meta">
                <text class="badge" :class="levelBadgeClass(activeMember.member_level)">{{ activeMember.member_level_label }}</text>
              </view>
              <view class="directory-detail-unit">{{ activeMember.work_unit || '未填写工作单位' }}</view>
            </view>
          </view>

          <view class="directory-detail-list">
            <view class="directory-detail-row">
              <view class="directory-detail-label">工作单位</view>
              <view class="directory-detail-value">{{ activeMember.work_unit || '未填写工作单位' }}</view>
            </view>
            <view class="directory-detail-row">
              <view class="directory-detail-label">常驻地</view>
              <view class="directory-detail-value">{{ activeMember.resident_city || '未填写常驻地' }}</view>
            </view>
            <view class="directory-detail-row">
              <view class="directory-detail-label">公开范围</view>
              <view class="directory-detail-value">仅展示姓名、工作单位和常驻地</view>
            </view>
          </view>

          <view class="directory-detail-note">当前版本通讯录仅开放基础公开信息，电话号码不会在此页显示。</view>
          <view class="directory-detail-actions">
            <view class="button-secondary detail-button" @click="closeDetail">关闭</view>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMemberDirectory } from '../../api/member'
import { goLogin, isLoggedIn } from '../../utils/auth'
import { normalizeMediaUrl } from '../../utils/media'

const keyword = ref('')
const items = ref([])
const loading = ref(false)
const loggedIn = ref(isLoggedIn())
const activeTab = ref('name')
const detailVisible = ref(false)
const activeMember = ref(null)

const searchTabs = [
  { key: 'name', label: '按姓名查询' },
  { key: 'resident_city', label: '按常驻地查询' },
]

const normalizedItems = computed(() => {
  const list = [...items.value]
  return list.sort((a, b) => {
    const keyA = activeTab.value === 'resident_city' ? (a.resident_city || a.name || '') : (a.name || '')
    const keyB = activeTab.value === 'resident_city' ? (b.resident_city || b.name || '') : (b.name || '')
    return keyA.localeCompare(keyB, 'zh-Hans-CN')
  })
})

const groupedItems = computed(() => {
  const groups = []
  normalizedItems.value.forEach((item) => {
    const label = getGroupLabel(item)
    const existing = groups.find((group) => group.label === label)
    if (existing) {
      existing.items.push(item)
      return
    }
    groups.push({ label, items: [item] })
  })
  return groups
})

function levelBadgeClass(level) {
  return {
    director: 'badge-primary',
    member: 'badge-info',
    non_member: 'badge-muted',
  }[level || 'non_member']
}

function getGroupLabel(item) {
  const source = activeTab.value === 'resident_city' ? item.resident_city || item.name || '' : item.name || ''
  if (!source) return '#'
  return source.trim().slice(0, 1).toUpperCase()
}

function getAvatarText(name) {
  if (!name) return '福'
  return String(name).trim().slice(0, 1)
}

async function loadData() {
  loggedIn.value = isLoggedIn()
  if (!loggedIn.value) return
  loading.value = true
  try {
    const params = { page: 1, page_size: 100 }
    if (activeTab.value === 'name') {
      params.name = keyword.value
    } else {
      params.resident_city = keyword.value
    }
    const res = await getMemberDirectory(params)
    items.value = (res.items || []).map((item) => ({
      ...item,
      avatar_url: normalizeMediaUrl(item.avatar_url || ''),
    }))
  } finally {
    loading.value = false
  }
}

function switchTab(key) {
  activeTab.value = key
  keyword.value = ''
  loadData().catch(() => {})
}

function jumpToGroup(label) {
  uni.pageScrollTo({
    selector: `#group-${label}`,
    duration: 180,
  })
}

function openDetail(item) {
  activeMember.value = item
  detailVisible.value = true
}

function closeDetail() {
  detailVisible.value = false
}

onShow(() => {
  loggedIn.value = isLoggedIn()
  loadData().catch(() => {})
})
</script>

<style scoped>
.directory-page {
  padding: 0 0 42rpx;
  background: linear-gradient(180deg, #f4f7fc 0%, #f8fbfe 28%, #fbfcff 100%);
}

.directory-header {
  padding: 34rpx 28rpx 18rpx;
}

.directory-title {
  color: #1b2536;
  font-size: 46rpx;
  font-weight: 700;
}

.directory-subtitle,
.directory-state-desc,
.directory-count,
.directory-loading,
.directory-empty,
.directory-detail-note {
  color: #7a89a0;
  font-size: 24rpx;
  line-height: 1.74;
}

.directory-subtitle {
  margin-top: 10rpx;
}

.directory-state {
  padding: 34rpx 28rpx 8rpx;
}

.directory-state-title {
  color: #1b2536;
  font-size: 34rpx;
  font-weight: 700;
}

.directory-state-action {
  margin-top: 22rpx;
}

.directory-toolbar {
  padding: 10rpx 28rpx 0;
}

.directory-tabs {
  display: flex;
  gap: 20rpx;
  margin-bottom: 18rpx;
}

.directory-tab {
  position: relative;
  min-height: 62rpx;
  color: #48576a;
  display: flex;
  align-items: center;
  font-size: 28rpx;
  font-weight: 600;
  white-space: nowrap;
}

.directory-tab-active {
  color: #485291;
}

.directory-tab-active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -10rpx;
  height: 5rpx;
  border-radius: 999rpx;
  background: #485291;
}

.directory-search {
  display: grid;
  grid-template-columns: 28rpx minmax(0, 1fr) 72rpx;
  gap: 14rpx;
  align-items: center;
  min-height: 88rpx;
  padding: 0 22rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.84);
  border: 1rpx solid rgba(216, 224, 236, 0.96);
}

.search-icon {
  position: relative;
  width: 28rpx;
  height: 28rpx;
}

.search-icon-circle {
  position: absolute;
  left: 0;
  top: 0;
  width: 18rpx;
  height: 18rpx;
  border: 3rpx solid #8ea0b8;
  border-radius: 50%;
}

.search-icon-handle {
  position: absolute;
  right: 1rpx;
  bottom: 2rpx;
  width: 10rpx;
  height: 3rpx;
  border-radius: 999rpx;
  background: #8ea0b8;
  transform: rotate(45deg);
  transform-origin: right center;
}

.directory-search-input {
  min-height: 88rpx;
  color: #1b2536;
  font-size: 27rpx;
}

.search-action {
  color: #485291;
  font-size: 25rpx;
  font-weight: 600;
  text-align: right;
}

.directory-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 28rpx 28rpx 10rpx;
}

.directory-main {
  position: relative;
  padding: 0 54rpx 0 28rpx;
}

.directory-group-label {
  padding: 16rpx 0 12rpx;
  color: #72829a;
  font-size: 24rpx;
  font-weight: 600;
}

.directory-row {
  display: grid;
  grid-template-columns: 88rpx minmax(0, 1fr) 44rpx;
  gap: 18rpx;
  align-items: center;
  min-height: 138rpx;
  border-top: 1rpx solid rgba(232, 236, 241, 0.96);
}

.directory-avatar,
.directory-detail-avatar {
  overflow: hidden;
  width: 66rpx;
  height: 66rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #e6eef9 0%, #d5e2f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #485291;
  font-size: 28rpx;
  font-weight: 700;
}

.directory-avatar-image {
  width: 100%;
  height: 100%;
  display: block;
}

.directory-copy {
  min-width: 0;
}

.directory-name,
.directory-detail-name {
  color: #1b2536;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.34;
}

.directory-unit,
.directory-city,
.directory-detail-unit,
.directory-detail-label,
.directory-detail-value {
  margin-top: 8rpx;
  color: #72829a;
  font-size: 24rpx;
  line-height: 1.68;
}

.directory-action {
  color: #a9b6c9;
  font-size: 30rpx;
  text-align: right;
}

.directory-rail {
  position: absolute;
  right: 8rpx;
  top: 4rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  align-items: center;
}

.directory-rail-item {
  color: #8796ab;
  font-size: 20rpx;
  line-height: 1;
}

.directory-detail-mask {
  position: fixed;
  inset: 0;
  z-index: 20;
  background: rgba(18, 24, 32, 0.22);
  display: flex;
  align-items: flex-end;
}

.directory-detail {
  width: 100%;
  padding: 16rpx 28rpx 32rpx;
  background: #ffffff;
  border-radius: 34rpx 34rpx 0 0;
}

.directory-detail-handle {
  width: 84rpx;
  height: 8rpx;
  margin: 0 auto 24rpx;
  border-radius: 999rpx;
  background: #d8dee7;
}

.directory-detail-hero {
  display: grid;
  grid-template-columns: 116rpx minmax(0, 1fr);
  gap: 22rpx;
  align-items: center;
  padding-bottom: 20rpx;
}

.directory-detail-avatar {
  width: 104rpx;
  height: 104rpx;
}

.directory-detail-meta {
  display: flex;
  gap: 10rpx;
  margin-top: 12rpx;
}

.directory-detail-list {
  border-top: 1rpx solid #e6edf5;
  border-bottom: 1rpx solid #e6edf5;
}

.directory-detail-row {
  display: grid;
  grid-template-columns: 140rpx minmax(0, 1fr);
  gap: 18rpx;
  align-items: center;
  min-height: 96rpx;
}

.directory-detail-row + .directory-detail-row {
  border-top: 1rpx solid #e6edf5;
}

.directory-detail-value {
  color: #1b2536;
  margin-top: 0;
}

.directory-detail-actions {
  padding-top: 24rpx;
}

.detail-button {
  width: 100%;
}
</style>
