<template>
  <view class="page">
    <view class="page-shell login-page">
      <view class="card hero-card login-hero">
        <view class="brand-chip login-chip">会员身份确认</view>
        <view class="hero-title">登录福莲会员服务</view>
      </view>

      <view class="card">
        <view class="section-header">
          <view>
            <view class="section-title">快捷登录</view>
          </view>
        </view>

        <!-- #ifdef MP-WEIXIN -->
        <button
          class="button-primary wechat-phone-btn"
          :class="{ 'button-disabled': wechatLoggingIn }"
          open-type="getPhoneNumber"
          @getphonenumber="handleWechatPhoneLogin"
        >
          {{ wechatLoggingIn ? '登录中...' : '微信手机号登录' }}
        </button>
        <!-- #endif -->
      </view>

      <view class="card">
        <view class="section-header">
          <view>
            <view class="section-title">短信验证码登录</view>
          </view>
        </view>

        <view class="field">
          <text class="field-label">手机号</text>
          <input
            v-model="phone"
            class="field-input"
            type="number"
            maxlength="11"
            placeholder="请输入会员手机号"
          />
        </view>

        <view class="field">
          <text class="field-label">验证码</text>
          <view class="code-row">
            <input
              v-model="code"
              class="field-input code-input"
              type="number"
              maxlength="6"
              placeholder="请输入验证码"
            />
            <view
              class="button-secondary code-btn"
              :class="{ 'button-disabled': !canSendCode || sendingCode || countdown > 0 }"
              @click="handleSendCode"
            >
              {{ codeButtonText }}
            </view>
          </view>
        </view>

        <view v-if="debugCode" class="debug-block">
          <view class="debug-title">开发环境验证码</view>
          <view class="debug-code">{{ debugCode }}</view>
          <view class="field-tip">该信息仅用于本地联调，正式环境不会展示。</view>
        </view>

        <view
          class="button-primary"
          :class="{ 'button-disabled': !canLogin || loggingIn }"
          @click="handleLogin"
        >
          {{ loggingIn ? '登录中...' : '短信验证码登录' }}
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, onUnmounted, ref } from 'vue'
import { loginMember, loginMemberByWechatPhone, sendMemberCode, syncMemberAvatarFromUrl } from '../../api/member'
import { setMember, setToken } from '../../utils/auth'

const phone = ref('')
const code = ref('')
const debugCode = ref('')
const countdown = ref(0)
const sendingCode = ref(false)
const loggingIn = ref(false)
const wechatLoggingIn = ref(false)
let timer = null

const phoneValid = computed(() => /^1\d{10}$/.test(phone.value))
const canSendCode = computed(() => phoneValid.value)
const canLogin = computed(() => phoneValid.value && !!code.value)
const codeButtonText = computed(() => {
  if (sendingCode.value) return '发送中...'
  if (countdown.value > 0) return `${countdown.value}s`
  return '获取验证码'
})

function startCountdown() {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function syncWechatAvatarIfNeeded(member) {
  // #ifdef MP-WEIXIN
  if (!member || member.avatar_url) return member
  try {
    const profile = await new Promise((resolve, reject) => {
      uni.getUserProfile({
        desc: '用于同步会员头像',
        success: resolve,
        fail: reject,
      })
    })
    const avatarUrl = profile?.userInfo?.avatarUrl
    if (!avatarUrl) return member
    const syncedProfile = await syncMemberAvatarFromUrl({ avatar_url: avatarUrl })
    return {
      ...member,
      avatar_url: syncedProfile?.avatar_url || member.avatar_url || '',
    }
  } catch {
    return member
  }
  // #endif
  return member
}

async function finishLogin(res, options = {}) {
  setToken(res.access_token)
  let nextMember = res.member
  if (options.syncWechatAvatar) {
    nextMember = await syncWechatAvatarIfNeeded(nextMember)
  }
  setMember(nextMember)
  uni.showToast({ title: '登录成功', icon: 'none' })
  uni.switchTab({ url: '/pages/home/index' })
}

async function handleSendCode() {
  if (!canSendCode.value || sendingCode.value || countdown.value > 0) return

  sendingCode.value = true
  debugCode.value = ''
  try {
    const res = await sendMemberCode({ phone: phone.value })
    if (res.debug_code) {
      debugCode.value = res.debug_code
      code.value = res.debug_code
      // #ifdef H5
      uni.showModal({
        title: '开发环境验证码',
        content: `验证码：${res.debug_code}`,
        showCancel: false,
      })
      // #endif
    } else {
      uni.showToast({ title: '验证码已发送', icon: 'none' })
    }
    startCountdown()
  } finally {
    sendingCode.value = false
  }
}

async function handleLogin() {
  if (!canLogin.value || loggingIn.value) return

  loggingIn.value = true
  try {
    const res = await loginMember({ phone: phone.value, code: code.value })
    await finishLogin(res)
  } finally {
    loggingIn.value = false
  }
}

async function handleWechatPhoneLogin(event) {
  if (wechatLoggingIn.value) return

  const phoneCode = event?.detail?.code
  if (!phoneCode) {
    uni.showToast({ title: '未获取到微信手机号授权', icon: 'none' })
    return
  }

  wechatLoggingIn.value = true
  try {
    const res = await loginMemberByWechatPhone({ phone_code: phoneCode })
    await finishLogin(res, { syncWechatAvatar: true })
  } finally {
    wechatLoggingIn.value = false
  }
}

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.login-page {
  justify-content: center;
  padding-top: 44rpx;
}

.login-hero {
  padding-bottom: 30rpx;
}

.login-chip {
  background: rgba(235, 233, 218, 0.16);
  color: #ede0c6;
  border-color: rgba(216, 179, 106, 0.24);
}

.wechat-phone-btn {
  width: 100%;
}

.code-row {
  display: flex;
  gap: 14rpx;
}

.code-input {
  flex: 1;
}

.code-btn {
  width: 228rpx;
  min-height: 88rpx;
  flex-shrink: 0;
}

.debug-block {
  margin-bottom: 24rpx;
  padding: 18rpx 20rpx;
  border-radius: 14rpx;
  background: #f5efe4;
  border: 1rpx dashed #cdbb98;
}

.debug-title {
  color: #6f5733;
  font-size: 22rpx;
  font-weight: 600;
}

.debug-code {
  margin-top: 8rpx;
  color: #1f5a58;
  font-size: 34rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
}
</style>
