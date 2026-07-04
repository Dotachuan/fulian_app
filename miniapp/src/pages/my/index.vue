<template>
  <view class="page profile-page">
    <view class="profile-header">
      <view class="profile-topline">
        <view class="profile-top-kicker">会员中心</view>
        <view v-if="member" class="profile-status">{{ member.status === 'active' ? '账号已启用' : '账号已停用' }}</view>
      </view>

      <view class="profile-identity">
        <view class="profile-avatar-wrap">
          <view class="profile-avatar">
            <image v-if="avatarUrl" class="profile-avatar-image" :src="avatarUrl" mode="aspectFill" />
            <template v-else>
              <view class="avatar-head"></view>
              <view class="avatar-body"></view>
            </template>
          </view>
          <view v-if="member" class="avatar-edit-link" @click="chooseAvatarFromAlbum">
            {{ avatarUploading ? '上传中...' : '更换头像' }}
          </view>
        </view>

        <view class="profile-main">
          <view class="profile-name">{{ member?.name || '福莲会员' }}</view>
          <view class="profile-phone">{{ maskedPhone }}</view>
          <view class="profile-badges">
            <text v-if="member" class="badge" :class="memberLevelClass">{{ memberLevelLabel }}</text>
            <text class="badge" :class="bindingBadgeClass">{{ bindingText }}</text>
          </view>
        </view>

        <view class="profile-enter" @click="member ? scrollToProfile() : goLogin()">→</view>
      </view>
    </view>

    <view class="profile-band">
      <view class="band-head">
        <view class="band-title">服务入口</view>
      </view>

      <view class="service-list">
        <view class="service-row" @click="openPage('/pages/donations/index')">
          <view class="service-icon service-icon-donation">
            <view class="glyph-book"></view>
            <view class="glyph-coin"></view>
          </view>
          <view class="service-copy">
            <view class="service-title">查看我的捐赠</view>
            <view class="service-desc">查看累计金额、捐赠明细与捐赠证书。</view>
          </view>
          <view class="service-arrow">→</view>
        </view>

        <view class="service-row" @click="openPage('/pages/certificate/index')">
          <view class="service-icon service-icon-certificate">
            <view class="glyph-scroll"></view>
            <view class="glyph-ribbon"></view>
          </view>
          <view class="service-copy">
            <view class="service-title">捐赠证书</view>
            <view class="service-desc">生成正式捐赠证书并保存到相册留存。</view>
          </view>
          <view class="service-arrow">→</view>
        </view>

        <view class="service-row" @click="openPage('/pages/invoice/index')">
          <view class="service-icon service-icon-invoice">
            <view class="glyph-receipt"></view>
            <view class="glyph-line glyph-line-one"></view>
            <view class="glyph-line glyph-line-two"></view>
          </view>
          <view class="service-copy">
            <view class="service-title">开票申请</view>
            <view class="service-desc">保存开票资料并提交新的开票申请。</view>
          </view>
          <view class="service-arrow">→</view>
        </view>

        <view class="service-row" @click="scrollToSuggestion()">
          <view class="service-icon service-icon-suggestion">
            <view class="glyph-chat"></view>
            <view class="glyph-chat-line glyph-chat-line-one"></view>
            <view class="glyph-chat-line glyph-chat-line-two"></view>
          </view>
          <view class="service-copy">
            <view class="service-title">意见建议</view>
            <view class="service-desc">提交使用反馈、问题记录或希望新增的功能建议。</view>
          </view>
          <view class="service-arrow">→</view>
        </view>
      </view>
    </view>

    <view id="member-profile" class="profile-band">
      <view class="band-head">
        <view class="band-title">会员信息</view>
      </view>

      <view v-if="!member" class="band-empty">
        <view class="band-empty-copy">登录后可填写会员信息并同步到通讯录展示。</view>
        <view class="button-primary login-btn" @click="goLogin">去登录</view>
      </view>

      <view v-else class="profile-form">
        <view class="form-row">
          <view class="form-label">姓名</view>
          <input v-model="profileForm.name" class="form-input" placeholder="请输入姓名" />
        </view>
        <view class="form-row">
          <view class="form-label">工作单位</view>
          <input v-model="profileForm.work_unit" class="form-input" placeholder="请输入工作单位" />
        </view>
        <view class="form-row">
          <view class="form-label">常驻地</view>
          <input v-model="profileForm.resident_city" class="form-input" placeholder="请输入常驻地" />
        </view>
        <view class="form-row">
          <view class="form-label">电话号码</view>
          <input v-model="profileForm.phone" class="form-input" placeholder="请输入手机号码" type="number" />
        </view>
        <view class="form-note">电话号码仅用于身份验证，不会在会员通讯录中公开展示。</view>
        <view class="form-actions">
          <view class="button-primary form-save" @click="saveProfile">{{ saving ? '保存中...' : '保存会员信息' }}</view>
        </view>
      </view>
    </view>

    <view v-if="member && memberState !== 'bound'" class="profile-band profile-band-muted">
      <view class="band-head compact-head">
        <view class="band-title">输入绑定码</view>
      </view>
      <view class="state-copy">如果当前手机号没有自动匹配到唯一捐赠人，可联系管理员获取绑定码，在这里完成身份绑定。</view>
      <view class="binding-code-row">
        <input
          v-model="bindingCodeForm.code"
          class="binding-code-input"
          placeholder="请输入绑定码"
          maxlength="16"
        />
        <view class="binding-code-btn" @click="submitBindingCode">{{ redeeming ? '提交中...' : '确认绑定' }}</view>
      </view>
    </view>

    <view v-if="memberState !== 'bound'" class="profile-band profile-band-muted">
      <view class="band-head compact-head">
        <view class="band-title">当前状态说明</view>
      </view>
      <view class="state-copy">{{ bindingDescription }}</view>
    </view>

    <view id="suggestion-section" class="profile-band">
      <view class="band-head">
        <view class="band-title">意见建议</view>
        <view class="band-subtitle">欢迎提交你在使用过程中的想法、问题或改进建议。</view>
      </view>

      <view v-if="!member" class="band-empty">
        <view class="band-empty-copy">登录后可提交意见建议，帮助我们持续完善服务体验。</view>
        <view class="button-primary login-btn" @click="goLogin">去登录</view>
      </view>

      <view v-else class="suggestion-form">
        <view class="form-row">
          <view class="form-label">联系方式</view>
          <input v-model="suggestionForm.contact" class="form-input" placeholder="可填写手机号、微信号或邮箱（选填）" />
        </view>
        <view class="form-row form-row-textarea">
          <view class="form-label">建议内容</view>
          <textarea
            v-model="suggestionForm.content"
            class="form-textarea"
            maxlength="2000"
            placeholder="请输入你的建议、反馈的问题，或希望新增的功能"
          />
          <view class="textarea-count">{{ suggestionForm.content.length }}/2000</view>
        </view>
        <view class="form-actions">
          <view class="button-primary form-save" @click="submitSuggestion">
            {{ submittingSuggestion ? '提交中...' : '提交建议' }}
          </view>
        </view>
      </view>
    </view>

    <view class="profile-band">
      <view class="band-head">
        <view class="band-title">联系我们</view>
      </view>

      <view v-if="contactRows.length" class="contact-list">
        <view v-for="item in contactRows" :key="item.label" class="contact-row" @click="copyContact(item)">
          <view class="contact-label">{{ item.label }}</view>
          <view class="contact-value">{{ item.value }}</view>
        </view>
      </view>
      <view v-else class="band-empty-copy">暂未配置联系方式</view>
    </view>

    <view v-if="member" class="logout-row">
      <view class="logout-link" @click="logout">退出登录</view>
    </view>
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import {
  createMemberSuggestion,
  getMemberMe,
  getMemberProfile,
  redeemMemberBindingCode,
  updateMemberProfile,
  uploadMemberAvatar,
} from '../../api/member'
import { getPublicContact } from '../../api/public'
import { normalizeMediaUrl } from '../../utils/media'
import {
  getBindingBadgeClass,
  getBindingDescription,
  getBindingText,
  getMember,
  getMemberAccessState,
  getMemberLevelClass,
  getMemberLevelLabel,
  goLogin,
  logoutMember,
  setMember,
} from '../../utils/auth'

const member = ref(getMember())
const saving = ref(false)
const redeeming = ref(false)
const submittingSuggestion = ref(false)
const avatarUploading = ref(false)
const profileForm = reactive({
  name: '',
  work_unit: '',
  resident_city: '',
  phone: '',
})
const bindingCodeForm = reactive({
  code: '',
})
const suggestionForm = reactive({
  contact: '',
  content: '',
})
const contact = ref(null)

const memberState = computed(() => getMemberAccessState(member.value))
const bindingText = computed(() => getBindingText(member.value))
const bindingBadgeClass = computed(() => getBindingBadgeClass(member.value))
const bindingDescription = computed(() => getBindingDescription(member.value))
const memberLevelLabel = computed(() => getMemberLevelLabel(member.value))
const memberLevelClass = computed(() => getMemberLevelClass(member.value))
const avatarUrl = computed(() => normalizeMediaUrl(member.value?.avatar_url || ''))
const contactSummary = computed(() => contact.value?.summary || '基金会联系方式与对外沟通渠道。')
const contactRows = computed(() => {
  const content = String(contact.value?.content || '').trim()
  if (!content) return []
  return content
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const index = line.indexOf('：')
      if (index > -1) {
        return {
          label: line.slice(0, index).trim(),
          value: line.slice(index + 1).trim(),
        }
      }
      return {
        label: '联系信息',
        value: line,
      }
    })
    .filter((item) => item.value)
})
const maskedPhone = computed(() => {
  const phone = member.value?.phone
  if (!phone) return '登录后查看会员信息'
  return String(phone).replace(/^(\d{3})\d{4}(\d{2,4})$/, '$1******$2')
})

function fillProfileForm(payload = {}) {
  profileForm.name = payload.name || ''
  profileForm.work_unit = payload.work_unit || ''
  profileForm.resident_city = payload.resident_city || ''
  profileForm.phone = payload.phone || member.value?.phone || ''
}

async function loadProfile() {
  const cached = getMember()
  member.value = cached
  if (!cached) {
    fillProfileForm({})
    return
  }

  const [latestMember, profile] = await Promise.all([getMemberMe(), getMemberProfile()])
  member.value = latestMember
  setMember(latestMember)
  fillProfileForm(profile)
}

async function loadContact() {
  try {
    contact.value = await getPublicContact()
  } catch {
    contact.value = null
  }
}

function openPage(url) {
  if (!member.value) {
    goLogin()
    return
  }
  uni.navigateTo({ url })
}

function switchTabPage(url) {
  if (!member.value) {
    goLogin()
    return
  }
  uni.switchTab({ url })
}

function scrollToProfile() {
  uni.pageScrollTo({
    selector: '#member-profile',
    duration: 220,
  })
}

function scrollToSuggestion() {
  if (!member.value) {
    goLogin()
    return
  }
  uni.pageScrollTo({
    selector: '#suggestion-section',
    duration: 220,
  })
}

async function saveProfile() {
  if (!member.value || saving.value) return
  saving.value = true
  try {
    await updateMemberProfile({ ...profileForm })
    const latestMember = await getMemberMe()
    member.value = latestMember
    setMember(latestMember)
    uni.showToast({ title: '会员信息已保存', icon: 'none' })
  } finally {
    saving.value = false
  }
}

async function chooseAvatarFromAlbum() {
  if (!member.value || avatarUploading.value) return
  avatarUploading.value = true
  try {
    const picker = await new Promise((resolve, reject) => {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album'],
        success: resolve,
        fail: reject,
      })
    })
    const filePath = picker?.tempFilePaths?.[0]
    if (!filePath) return
    const profile = await uploadMemberAvatar(filePath)
    member.value = {
      ...member.value,
      avatar_url: profile.avatar_url || '',
    }
    setMember(member.value)
    uni.showToast({ title: '头像已更新', icon: 'none' })
  } catch (error) {
    if (!String(error?.errMsg || '').includes('cancel')) {
      uni.showToast({ title: '头像上传失败', icon: 'none' })
    }
  } finally {
    avatarUploading.value = false
  }
}

async function submitBindingCode() {
  if (!member.value || redeeming.value) return
  const code = String(bindingCodeForm.code || '').trim().toUpperCase()
  if (!code) {
    uni.showToast({ title: '请输入绑定码', icon: 'none' })
    return
  }
  redeeming.value = true
  try {
    await redeemMemberBindingCode({ code })
    bindingCodeForm.code = ''
    const latestMember = await getMemberMe()
    member.value = latestMember
    setMember(latestMember)
    uni.showToast({ title: '绑定成功', icon: 'none' })
  } finally {
    redeeming.value = false
  }
}

async function submitSuggestion() {
  if (!member.value || submittingSuggestion.value) return
  if (!String(suggestionForm.content || '').trim()) {
    uni.showToast({ title: '请输入建议内容', icon: 'none' })
    return
  }
  submittingSuggestion.value = true
  try {
    await createMemberSuggestion({
      contact: suggestionForm.contact,
      content: suggestionForm.content,
    })
    suggestionForm.contact = ''
    suggestionForm.content = ''
    uni.showToast({ title: '感谢你的建议', icon: 'none' })
  } finally {
    submittingSuggestion.value = false
  }
}

function logout() {
  logoutMember()
  member.value = null
  fillProfileForm({})
  uni.showToast({ title: '已退出登录', icon: 'none' })
}

function copyContact(item) {
  if (!item?.value) return
  uni.setClipboardData({
    data: item.value,
    success: () => {
      uni.showToast({ title: `${item.label}已复制`, icon: 'none' })
    },
  })
}

onShow(() => {
  loadProfile().catch(() => {})
  loadContact().catch(() => {})
})
</script>

<style scoped>
.profile-page {
  padding: 0 0 56rpx;
  background: linear-gradient(180deg, #f4f7fc 0%, #f8fbfe 26%, #f7f9fc 100%);
}

.profile-header {
  padding: 42rpx 28rpx 24rpx;
  background: linear-gradient(180deg, rgba(225, 232, 247, 0.92) 0%, rgba(247, 250, 255, 0.98) 100%);
}

.profile-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.profile-top-kicker,
.profile-status {
  color: #667791;
  font-size: 22rpx;
  letter-spacing: 1.5rpx;
}

.profile-identity {
  display: grid;
  grid-template-columns: 112rpx minmax(0, 1fr) 48rpx;
  gap: 22rpx;
  align-items: center;
  margin-top: 26rpx;
}

.profile-avatar-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.profile-avatar {
  position: relative;
  width: 112rpx;
  height: 112rpx;
  border-radius: 28rpx;
  background: linear-gradient(180deg, #ffffff 0%, #eef3fa 100%);
  overflow: hidden;
}

.profile-avatar-image {
  width: 100%;
  height: 100%;
  display: block;
}

.avatar-head {
  position: absolute;
  top: 20rpx;
  left: 34rpx;
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: #bcc8db;
}

.avatar-body {
  position: absolute;
  left: 20rpx;
  bottom: 18rpx;
  width: 72rpx;
  height: 42rpx;
  border-radius: 24rpx 24rpx 14rpx 14rpx;
  background: #bcc8db;
}

.avatar-edit-link {
  color: #64758d;
  font-size: 22rpx;
  line-height: 1;
}

.profile-name {
  color: #1b2536;
  font-size: 50rpx;
  font-weight: 700;
}

.profile-phone {
  display: inline-flex;
  align-items: center;
  min-height: 48rpx;
  margin-top: 12rpx;
  padding: 0 20rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.72);
  color: #64758d;
  font-size: 24rpx;
}

.profile-badges {
  display: flex;
  gap: 10rpx;
  margin-top: 14rpx;
  flex-wrap: wrap;
}

.profile-enter {
  color: #a9b6c9;
  font-size: 40rpx;
  text-align: right;
}

.profile-band {
  padding: 30rpx 28rpx 8rpx;
  background: #ffffff;
}

.profile-band + .profile-band {
  margin-top: 16rpx;
}

.profile-band-muted {
  background: #f9fbff;
}

.band-head {
  margin-bottom: 12rpx;
}

.compact-head {
  margin-bottom: 4rpx;
}

.band-title {
  color: #1b2536;
  font-size: 40rpx;
  font-weight: 700;
}

.band-subtitle {
  margin-top: 8rpx;
  color: #8390a4;
  font-size: 23rpx;
  line-height: 1.7;
}

.service-list,
.profile-form,
.suggestion-form {
  border-top: 1rpx solid #e6edf5;
}

.service-row {
  display: grid;
  grid-template-columns: 88rpx minmax(0, 1fr) 36rpx;
  gap: 18rpx;
  align-items: center;
  min-height: 132rpx;
  border-bottom: 1rpx solid #e6edf5;
}

.service-icon {
  position: relative;
  width: 62rpx;
  height: 62rpx;
}

.service-title {
  color: #1b2536;
  font-size: 31rpx;
  font-weight: 700;
}

.service-desc {
  margin-top: 8rpx;
  color: #72829a;
  font-size: 23rpx;
  line-height: 1.68;
}

.service-arrow {
  color: #a9b6c9;
  font-size: 32rpx;
  text-align: right;
}

.service-icon-donation,
.service-icon-certificate,
.service-icon-invoice,
.service-icon-directory,
.service-icon-suggestion {
  border-radius: 18rpx;
  background: linear-gradient(135deg, #eef2fb 0%, #dde5f6 100%);
}

.glyph-scroll {
  position: absolute;
  left: 14rpx;
  top: 12rpx;
  width: 34rpx;
  height: 38rpx;
  border: 3rpx solid #7e6640;
  border-radius: 8rpx;
  background: #fffaf0;
}

.glyph-scroll::before,
.glyph-scroll::after {
  content: '';
  position: absolute;
  width: 8rpx;
  height: 38rpx;
  top: -3rpx;
  border-radius: 999rpx;
  background: #d8c29a;
}

.glyph-scroll::before {
  left: -6rpx;
}

.glyph-scroll::after {
  right: -6rpx;
}

.glyph-ribbon {
  position: absolute;
  right: 10rpx;
  bottom: 10rpx;
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: #caa15e;
}

.glyph-ribbon::after {
  content: '';
  position: absolute;
  left: 6rpx;
  top: 16rpx;
  width: 6rpx;
  height: 12rpx;
  background: linear-gradient(180deg, #caa15e 0%, #9f7d43 100%);
  clip-path: polygon(0 0, 100% 0, 100% 78%, 50% 100%, 0 78%);
}

.glyph-book {
  position: absolute;
  left: 12rpx;
  top: 14rpx;
  width: 30rpx;
  height: 24rpx;
  border: 3rpx solid #5a67aa;
  border-right-width: 2rpx;
  border-radius: 8rpx 6rpx 6rpx 8rpx;
  background: rgba(255, 255, 255, 0.72);
}

.glyph-book::after {
  content: '';
  position: absolute;
  right: -9rpx;
  top: -3rpx;
  width: 22rpx;
  height: 24rpx;
  border: 3rpx solid #5a67aa;
  border-left-width: 2rpx;
  border-radius: 6rpx 8rpx 8rpx 6rpx;
  background: rgba(255, 255, 255, 0.82);
}

.glyph-coin {
  position: absolute;
  right: 8rpx;
  bottom: 8rpx;
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: #c1a670;
}

.glyph-receipt {
  position: absolute;
  left: 16rpx;
  top: 10rpx;
  width: 30rpx;
  height: 42rpx;
  background: #ffffff;
  border-radius: 8rpx;
}

.glyph-receipt::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -4rpx;
  width: 30rpx;
  height: 8rpx;
  background:
    linear-gradient(-45deg, transparent 33%, #ffffff 33%, #ffffff 66%, transparent 66%) 0 0 / 10rpx 8rpx repeat-x;
}

.glyph-line {
  position: absolute;
  left: 22rpx;
  width: 18rpx;
  height: 4rpx;
  border-radius: 999rpx;
  background: #5a67aa;
}

.glyph-line-one {
  top: 22rpx;
}

.glyph-line-two {
  top: 32rpx;
}

.glyph-user {
  position: absolute;
  background: #5a67aa;
  border-radius: 50%;
}

.glyph-user::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  background: #5a67aa;
  border-radius: 20rpx 20rpx 12rpx 12rpx;
}

.glyph-user-main {
  width: 18rpx;
  height: 18rpx;
  left: 22rpx;
  top: 14rpx;
}

.glyph-user-main::after {
  top: 16rpx;
  width: 24rpx;
  height: 16rpx;
}

.glyph-user-left,
.glyph-user-right {
  width: 14rpx;
  height: 14rpx;
  top: 20rpx;
  opacity: 0.72;
}

.glyph-user-left {
  left: 8rpx;
}

.glyph-user-right {
  right: 8rpx;
}

.glyph-user-left::after,
.glyph-user-right::after {
  top: 12rpx;
  width: 18rpx;
  height: 12rpx;
}

.glyph-chat {
  position: absolute;
  left: 10rpx;
  top: 12rpx;
  width: 42rpx;
  height: 30rpx;
  border-radius: 14rpx;
  background: #ffffff;
  border: 3rpx solid #5a67aa;
}

.glyph-chat::after {
  content: '';
  position: absolute;
  left: 8rpx;
  bottom: -10rpx;
  width: 16rpx;
  height: 16rpx;
  background: #ffffff;
  border-left: 3rpx solid #5a67aa;
  border-bottom: 3rpx solid #5a67aa;
  transform: rotate(-18deg);
  border-bottom-left-radius: 8rpx;
}

.glyph-chat-line {
  position: absolute;
  left: 20rpx;
  height: 4rpx;
  border-radius: 999rpx;
  background: #5a67aa;
  z-index: 1;
}

.glyph-chat-line-one {
  top: 24rpx;
  width: 22rpx;
}

.glyph-chat-line-two {
  top: 34rpx;
  width: 16rpx;
}

.band-empty {
  padding: 24rpx 0 20rpx;
}

.band-empty-copy {
  color: #72829a;
  font-size: 24rpx;
  line-height: 1.76;
}

.login-btn {
  margin-top: 20rpx;
}

.form-row {
  min-height: 112rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #e6edf5;
}

.form-row-textarea {
  min-height: auto;
}

.form-label {
  color: #68778f;
  font-size: 23rpx;
}

.form-input {
  margin-top: 14rpx;
  color: #1b2536;
  font-size: 28rpx;
  min-height: 42rpx;
}

.form-textarea {
  width: 100%;
  min-height: 220rpx;
  margin-top: 14rpx;
  color: #1b2536;
  font-size: 28rpx;
  line-height: 1.7;
}

.textarea-count {
  padding: 8rpx 0 0;
  color: #8a96a8;
  font-size: 22rpx;
  text-align: right;
}

.form-note {
  padding: 20rpx 0 0;
  color: #7b8799;
  font-size: 22rpx;
  line-height: 1.7;
}

.form-actions {
  padding: 24rpx 0 18rpx;
}

.form-save {
  width: 100%;
}

.state-copy {
  padding: 12rpx 0 22rpx;
  color: #6f7f98;
  font-size: 24rpx;
  line-height: 1.78;
}

.contact-list {
  border-top: 1rpx solid #e6edf5;
}

.contact-row {
  display: grid;
  grid-template-columns: 164rpx minmax(0, 1fr);
  gap: 18rpx;
  align-items: flex-start;
  min-height: 98rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #e6edf5;
}

.contact-label {
  color: #8390a4;
  font-size: 23rpx;
}

.contact-value {
  color: #1b2536;
  font-size: 27rpx;
  font-weight: 600;
  line-height: 1.62;
  word-break: break-all;
}

.binding-code-row {
  display: flex;
  gap: 16rpx;
  padding-bottom: 22rpx;
}

.binding-code-input {
  flex: 1;
  height: 88rpx;
  padding: 0 24rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.92);
  color: #1b2536;
  font-size: 28rpx;
}

.binding-code-btn {
  min-width: 176rpx;
  height: 88rpx;
  padding: 0 28rpx;
  border-radius: 22rpx;
  background: #384e85;
  color: #ffffff;
  font-size: 26rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-row {
  padding: 26rpx 0 0;
}

.logout-link {
  color: #7f5b57;
  font-size: 27rpx;
  text-align: center;
}
</style>
