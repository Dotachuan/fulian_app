<template>
  <view class="page">
    <view class="page-shell">
      <view v-if="!loggedIn" class="card card-soft">
        <view class="section-title">请先登录</view>
        <view class="section-subtitle">登录后可保存默认开票资料，并提交新的开票申请。</view>
        <view class="button-primary state-action" @click="goLogin">去登录</view>
      </view>

      <template v-else>
        <view v-if="memberState !== 'bound'" class="card card-soft">
          <view class="section-title">当前会员状态说明</view>
          <view class="section-subtitle">{{ bindingDescription }}</view>
        </view>

        <view class="card">
          <view class="section-header">
            <view>
              <view class="section-title">默认开票资料</view>
              <view class="section-subtitle">首次录入后会自动保存，后续提交申请时可直接复用。</view>
            </view>
          </view>

          <view class="field">
            <text class="field-label">抬头 / 姓名</text>
            <input v-model="profile.title" class="field-input" placeholder="请输入开票抬头或姓名" />
          </view>
          <view class="field">
            <text class="field-label">联系电话</text>
            <input v-model="profile.phone" class="field-input" placeholder="请输入联系电话" />
          </view>
          <view class="field">
            <text class="field-label">邮箱</text>
            <input v-model="profile.email" class="field-input" placeholder="请输入接收邮箱" />
          </view>
          <view class="field">
            <text class="field-label">身份证号 / 统一社会信用代码</text>
            <input v-model="profile.identity_no" class="field-input" placeholder="请输入证件号码" />
          </view>
          <view class="field">
            <text class="field-label">资料备注</text>
            <textarea v-model="profile.remark" class="field-textarea" placeholder="可补充常用说明" />
          </view>
          <view
            class="button-secondary"
            :class="{ 'button-disabled': savingProfile }"
            @click="saveProfile"
          >
            {{ savingProfile ? '保存中...' : '保存默认资料' }}
          </view>
        </view>

        <view class="card">
          <view class="section-header">
            <view>
              <view class="section-title">提交开票申请</view>
              <view class="section-subtitle">提交时会同步当前资料，并生成后台可处理的开票申请。</view>
            </view>
          </view>

          <view class="field">
            <text class="field-label">捐赠金额</text>
            <input
              v-model="requestForm.amount"
              class="field-input"
              type="digit"
              placeholder="请输入捐赠金额"
            />
          </view>
          <view class="field">
            <text class="field-label">捐赠日期</text>
            <picker
              mode="date"
              :value="requestForm.donation_date || today"
              :end="today"
              @change="onDonationDateChange"
            >
              <view class="field-input date-picker">
                <text :class="{ 'date-placeholder': !requestForm.donation_date }">
                  {{ requestForm.donation_date || '请选择捐赠日期' }}
                </text>
                <view class="date-picker-arrow"></view>
              </view>
            </picker>
          </view>
          <view class="field">
            <text class="field-label">申请备注</text>
            <textarea
              v-model="requestForm.remark"
              class="field-textarea"
              placeholder="可补充本次开票需求"
            />
          </view>
          <view
            class="button-primary"
            :class="{ 'button-disabled': submitting }"
            @click="submitRequest"
          >
            {{ submitting ? '提交中...' : '提交申请' }}
          </view>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import {
  createMemberInvoiceRequest,
  getMemberInvoiceProfile,
  updateMemberInvoiceProfile,
} from '../../api/member'
import {
  getBindingDescription,
  getMember,
  getMemberAccessState,
  goLogin,
  isLoggedIn,
} from '../../utils/auth'

const profile = reactive({
  title: '',
  phone: '',
  email: '',
  identity_no: '',
  remark: '',
})

const requestForm = reactive({
  amount: '',
  donation_date: '',
  remark: '',
})

const savingProfile = ref(false)
const submitting = ref(false)
const loggedIn = ref(isLoggedIn())
const member = ref(getMember())
const memberState = computed(() => getMemberAccessState(member.value))
const bindingDescription = computed(() => getBindingDescription(member.value))

function formatLocalDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const today = formatLocalDate(new Date())

function onDonationDateChange(event) {
  requestForm.donation_date = event.detail.value
}

function normalizeAmount(value) {
  return String(value || '')
    .trim()
    .replace(/,/g, '')
    .replace(/，/g, '')
}

function validateRequestForm() {
  const amount = normalizeAmount(requestForm.amount)
  if (!amount) {
    uni.showToast({ title: '请输入捐赠金额', icon: 'none' })
    return null
  }
  if (!/^\d+(\.\d{1,2})?$/.test(amount) || Number(amount) <= 0) {
    uni.showToast({ title: '请输入正确的金额格式', icon: 'none' })
    return null
  }

  const donationDate = String(requestForm.donation_date || '').trim()
  if (!donationDate) {
    uni.showToast({ title: '请选择捐赠日期', icon: 'none' })
    return null
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(donationDate)) {
    uni.showToast({ title: '日期请按 YYYY-MM-DD 填写', icon: 'none' })
    return null
  }

  return {
    amount,
    donation_date: donationDate,
  }
}

async function loadData() {
  loggedIn.value = isLoggedIn()
  member.value = getMember()
  if (!loggedIn.value) return
  const res = await getMemberInvoiceProfile()
  Object.assign(profile, res)
}

async function saveProfile() {
  if (savingProfile.value) return
  savingProfile.value = true
  try {
    await updateMemberInvoiceProfile(profile)
    uni.showToast({ title: '默认资料已保存', icon: 'none' })
  } finally {
    savingProfile.value = false
  }
}

async function submitRequest() {
  if (submitting.value) return
  const normalized = validateRequestForm()
  if (!normalized) return
  submitting.value = true
  try {
    await updateMemberInvoiceProfile(profile)
    await createMemberInvoiceRequest({
      donor_name: profile.title,
      amount: normalized.amount,
      donation_date: normalized.donation_date,
      email: profile.email,
      phone: profile.phone,
      identity_no: profile.identity_no,
      remark: requestForm.remark || profile.remark,
    })
    uni.showToast({ title: '申请已提交', icon: 'none' })
    requestForm.amount = ''
    requestForm.donation_date = ''
    requestForm.remark = ''
  } finally {
    submitting.value = false
  }
}

onShow(() => {
  loadData().catch(() => {})
})
</script>

<style scoped>
.state-action {
  margin-top: 24rpx;
}

.date-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.date-placeholder {
  color: #9aa4b2;
}

.date-picker-arrow {
  width: 14rpx;
  height: 14rpx;
  margin-right: 4rpx;
  border-right: 3rpx solid #7b8798;
  border-bottom: 3rpx solid #7b8798;
  transform: rotate(45deg) translateY(-3rpx);
}
</style>
