<template>
  <section class="page">
    <h1 class="page-title">开票申请</h1>
    <p class="page-desc">请填写捐赠信息和接收方式，提交后由后台工作人员统一处理。</p>

    <div class="content-band">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="invoice-form">
        <el-form-item label="捐赠人姓名或企业全称" prop="donor_name">
          <el-input v-model="form.donor_name" placeholder="请输入姓名或企业全称" />
        </el-form-item>
        <el-form-item label="捐赠金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" :step="100" controls-position="right" />
        </el-form-item>
        <el-form-item label="捐赠日期" prop="donation_date">
          <el-date-picker v-model="form.donation_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择日期" />
        </el-form-item>
        <el-form-item label="电子邮箱" prop="email">
          <el-input v-model="form.email" placeholder="用于接收电子票" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="用于接收开票通知短信" />
        </el-form-item>
        <el-form-item label="身份证号或统一社会信用代码" prop="identity_no">
          <el-input v-model="form.identity_no" placeholder="个人填身份证号，企业填统一社会信用代码" />
        </el-form-item>
        <el-form-item label="备注" prop="remark" class="full-row">
          <el-input v-model="form.remark" type="textarea" :rows="4" placeholder="需要特别说明的内容" />
        </el-form-item>
        <el-form-item class="full-row form-actions">
          <el-button type="primary" :icon="Check" :loading="submitting" @click="handleSubmit">提交申请</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-alert
      v-if="successNo"
      class="success-alert"
      type="success"
      show-icon
      :closable="false"
      :title="`提交成功，申请编号：${successNo}`"
    />
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Refresh } from '@element-plus/icons-vue'
import { createInvoiceRequestApi } from '@/api/public'

const formRef = ref()
const submitting = ref(false)
const successNo = ref('')

const form = reactive({
  donor_name: '',
  amount: null,
  donation_date: '',
  email: '',
  phone: '',
  identity_no: '',
  remark: '',
})

const mobilePhonePattern = /^1[3-9]\d{9}$/
const landlinePhonePattern = /^0\d{2,3}-?\d{7,8}$/
const creditCodePattern = /^[0-9A-HJ-NPQRTUWXY]{18}$/
const idCardWeightFactors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
const idCardCheckCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

function normalizeText(value) {
  return String(value || '').trim().toUpperCase()
}

function isValidPhone(value) {
  const phone = String(value || '').trim().replace(/\s+/g, '')
  return mobilePhonePattern.test(phone) || landlinePhonePattern.test(phone)
}

function isValidIdCard(value) {
  const idNo = normalizeText(value)
  if (!/^\d{17}[\dX]$/.test(idNo)) return false

  const year = Number(idNo.slice(6, 10))
  const month = Number(idNo.slice(10, 12))
  const day = Number(idNo.slice(12, 14))
  const birthday = new Date(year, month - 1, day)
  const isRealDate =
    birthday.getFullYear() === year &&
    birthday.getMonth() === month - 1 &&
    birthday.getDate() === day
  if (!isRealDate) return false

  const sum = idCardWeightFactors.reduce((total, factor, index) => total + Number(idNo[index]) * factor, 0)
  return idCardCheckCodes[sum % 11] === idNo[17]
}

function isValidIdentityNo(value) {
  const identityNo = normalizeText(value)
  return isValidIdCard(identityNo) || creditCodePattern.test(identityNo)
}

function validatePhone(_rule, value, callback) {
  if (!String(value || '').trim()) {
    callback(new Error('请输入联系电话'))
    return
  }
  if (!isValidPhone(value)) {
    callback(new Error('请输入正确的手机号或座机号'))
    return
  }
  callback()
}

function validateIdentityNo(_rule, value, callback) {
  if (!String(value || '').trim()) {
    callback(new Error('请输入身份证号或统一社会信用代码'))
    return
  }
  if (!isValidIdentityNo(value)) {
    callback(new Error('请输入正确的身份证号或统一社会信用代码'))
    return
  }
  callback()
}

const rules = {
  donor_name: [{ required: true, message: '请输入捐赠人姓名或企业全称', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入捐赠金额', trigger: 'change' }],
  donation_date: [{ required: true, message: '请选择捐赠日期', trigger: 'change' }],
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  identity_no: [{ validator: validateIdentityNo, trigger: 'blur' }],
}

function resetFormValues() {
  form.donor_name = ''
  form.amount = null
  form.donation_date = ''
  form.email = ''
  form.phone = ''
  form.identity_no = ''
  form.remark = ''
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const res = await createInvoiceRequestApi(form)
    successNo.value = res.request_no
    ElMessage.success('开票申请已提交')
    formRef.value.resetFields()
    resetFormValues()
  } finally {
    submitting.value = false
  }
}

function handleReset() {
  formRef.value.resetFields()
  resetFormValues()
  successNo.value = ''
}
</script>

<style scoped>
.invoice-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.invoice-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.full-row {
  grid-column: 1 / -1;
}

.form-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
}

.success-alert {
  margin-top: 18px;
}

@media (max-width: 760px) {
  .invoice-form {
    grid-template-columns: 1fr;
  }
}
</style>
