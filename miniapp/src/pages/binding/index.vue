<template>
  <view class="page binding-page">
    <view class="binding-hero">
      <view class="binding-kicker">会员服务</view>
      <view class="binding-title">会员绑定</view>
      <view class="binding-desc">填写真实姓名后，系统会自动匹配已有会员档案。</view>
    </view>

    <view v-if="!member" class="binding-band">
      <view class="band-title">请先登录</view>
      <view class="state-copy">登录后可自动匹配会员档案。</view>
      <view class="button-primary action-btn" @click="goLogin">去登录</view>
    </view>

    <template v-else>
      <view class="binding-band">
        <view class="band-head">
          <view class="band-title">当前状态</view>
          <text class="binding-badge" :class="bindingBadgeClass">{{ bindingText }}</text>
        </view>

        <view class="state-copy">
          {{ memberState === 'bound' ? '当前账号已完成会员档案绑定。' : bindingDescription }}
        </view>

        <template v-if="memberState === 'bound'">
          <view class="status-line">
            <text>绑定状态</text>
            <text>已完成绑定</text>
          </view>
          <view v-if="bindingRequest?.status === 'pending'" class="status-box">
            <view class="status-line">
              <text>更正申请</text>
              <text>待人工确认</text>
            </view>
          </view>
          <view class="correction-entry" @click="openCorrectionForm">绑定信息有误</view>
        </template>
        <view v-else-if="bindingRequest" class="status-box">
          <view class="status-line">
            <text>最近申请</text>
            <text>{{ requestStatusText(bindingRequest.status) }}</text>
          </view>
          <view v-if="bindingRequest.admin_note" class="request-note">{{ bindingRequest.admin_note }}</view>
        </view>
      </view>

      <view v-if="memberState !== 'bound' || showCorrectionForm" class="binding-band">
        <view class="band-title">{{ memberState === 'bound' ? '申请更正绑定' : '验证会员身份' }}</view>
        <view class="binding-form">
          <view class="form-row">
            <view class="form-label">姓名</view>
            <input v-model="form.name" class="form-input" placeholder="请输入真实姓名" maxlength="64" />
          </view>
          <view class="form-row">
            <view class="form-label">当前登录手机号</view>
            <view class="form-value">{{ form.phone || '-' }}</view>
            <view class="form-hint">手机号已通过登录验证，无需重复填写</view>
          </view>
          <view class="form-actions">
            <view
              class="button-primary action-btn"
              @click="memberState === 'bound' ? submitCorrection() : submitAutoBinding()"
            >
              {{ submitting ? '提交中...' : memberState === 'bound' ? '提交更正申请' : '立即匹配' }}
            </view>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import {
  autoBindMember,
  createMemberBindingCorrection,
  getLatestMemberBindingRequest,
  getMemberMe,
  getMemberProfile,
} from '../../api/member'
import {
  getBindingBadgeClass,
  getBindingDescription,
  getBindingText,
  getMember,
  getMemberAccessState,
  goLogin,
  setMember,
} from '../../utils/auth'

const member = ref(getMember())
const bindingRequest = ref(null)
const submitting = ref(false)
const showCorrectionForm = ref(false)
const form = reactive({
  name: '',
  phone: '',
})

const memberState = computed(() => getMemberAccessState(member.value))
const bindingText = computed(() => getBindingText(member.value))
const bindingBadgeClass = computed(() => getBindingBadgeClass(member.value))
const bindingDescription = computed(() => getBindingDescription(member.value))

function requestStatusText(status) {
  return { pending: '待人工确认', approved: '已通过', rejected: '已驳回' }[status] || status || '-'
}

async function loadData() {
  const cached = getMember()
  member.value = cached
  if (!cached) return

  const [latestMember, profile] = await Promise.all([getMemberMe(), getMemberProfile()])
  member.value = latestMember
  setMember(latestMember)

  const latestRequest = await getLatestMemberBindingRequest().catch(() => null)
  if (latestMember?.binding_status !== 'bound') {
    bindingRequest.value = latestRequest
    form.name = bindingRequest.value?.name || profile.name || latestMember.name || ''
    form.phone = latestMember.phone || profile.phone || ''
  } else {
    bindingRequest.value = latestRequest?.status === 'pending' ? latestRequest : null
    form.name = profile.name || latestMember.name || ''
    form.phone = profile.phone || latestMember.phone || ''
  }
}

function confirmNewProfile(name) {
  return new Promise((resolve) => {
    uni.showModal({
      title: '确认姓名',
      content: `未找到“${name}”对应的会员档案。请再次核对姓名，确认无误后将创建新档案。`,
      confirmText: '确认创建',
      cancelText: '重新填写',
      success: (result) => resolve(result.confirm),
      fail: () => resolve(false),
    })
  })
}

async function refreshBindingState() {
  const latestMember = await getMemberMe()
  member.value = latestMember
  setMember(latestMember)
  const latestRequest = await getLatestMemberBindingRequest().catch(() => null)
  bindingRequest.value =
    latestMember?.binding_status === 'bound' && latestRequest?.status !== 'pending' ? null : latestRequest
}

function openCorrectionForm() {
  form.name = ''
  showCorrectionForm.value = true
}

async function submitAutoBinding() {
  if (!member.value || submitting.value) return
  const name = String(form.name || '').trim()
  const phone = String(member.value.phone || form.phone || '').trim()
  if (!name) {
    uni.showToast({ title: '请输入姓名', icon: 'none' })
    return
  }
  if (!/^1[3-9]\d{9}$/.test(phone)) {
    uni.showToast({ title: '请输入正确手机号', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    let result = await autoBindMember({ name, phone, confirm_create: false })
    if (result.result === 'confirm_create') {
      const confirmed = await confirmNewProfile(name)
      if (!confirmed) return
      result = await autoBindMember({ name, phone, confirm_create: true })
    }

    await refreshBindingState()
    uni.showToast({
      title: result.result === 'bound' ? '绑定成功' : '已转人工确认',
      icon: 'none',
    })
  } finally {
    submitting.value = false
  }
}

async function submitCorrection() {
  if (!member.value || submitting.value) return
  const name = String(form.name || '').trim()
  const phone = String(member.value.phone || form.phone || '').trim()
  if (!name) {
    uni.showToast({ title: '请输入正确姓名', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    bindingRequest.value = await createMemberBindingCorrection({ name, phone })
    showCorrectionForm.value = false
    uni.showToast({ title: '更正申请已提交', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onShow(() => {
  loadData().catch(() => {
    uni.showToast({ title: '绑定信息加载失败', icon: 'none' })
  })
})
</script>

<style scoped>
.binding-page {
  min-height: 100vh;
  padding-bottom: 56rpx;
  background: linear-gradient(180deg, #f4f7fc 0%, #f8fbfe 30%, #ffffff 100%);
}

.binding-hero {
  padding: 46rpx 30rpx 28rpx;
}

.binding-kicker {
  color: #667791;
  font-size: 22rpx;
  letter-spacing: 1.5rpx;
}

.binding-title {
  margin-top: 14rpx;
  color: #1b2536;
  font-size: 56rpx;
  font-weight: 800;
  line-height: 1.14;
}

.binding-desc,
.state-copy {
  margin-top: 14rpx;
  color: #6f7f98;
  font-size: 25rpx;
  line-height: 1.76;
}

.binding-band {
  margin-top: 16rpx;
  padding: 30rpx 28rpx 8rpx;
  background: #ffffff;
}

.band-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
}

.band-title {
  color: #1b2536;
  font-size: 38rpx;
  font-weight: 700;
}

.binding-badge {
  flex-shrink: 0;
  max-width: 220rpx;
  min-height: 36rpx;
  padding: 0 14rpx;
  border-radius: 999rpx;
  font-size: 21rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-box {
  margin-top: 18rpx;
}

.status-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  min-height: 86rpx;
  border-top: 1rpx solid #e6edf5;
  color: #273244;
  font-size: 26rpx;
  font-weight: 700;
}

.request-note {
  padding: 14rpx 0 18rpx;
  color: #74829a;
  font-size: 24rpx;
  line-height: 1.6;
  border-top: 1rpx solid #e6edf5;
}

.correction-entry {
  padding: 20rpx 0 8rpx;
  color: #52619d;
  font-size: 24rpx;
  text-align: right;
}

.binding-form {
  margin-top: 14rpx;
  border-top: 1rpx solid #e6edf5;
}

.form-row {
  min-height: 112rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #e6edf5;
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

.form-value {
  margin-top: 14rpx;
  color: #1b2536;
  font-size: 28rpx;
  line-height: 42rpx;
}

.form-hint {
  margin-top: 6rpx;
  color: #8b97a8;
  font-size: 22rpx;
  line-height: 1.5;
}

.form-actions {
  padding: 26rpx 0 20rpx;
}

.action-btn {
  width: 100%;
}
</style>
