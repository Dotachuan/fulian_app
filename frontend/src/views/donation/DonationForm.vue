<template>
  <el-card shadow="never" :header="isEdit ? '编辑捐款' : '新增捐款'">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" style="max-width: 700px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="捐款日期" prop="donation_date">
            <el-date-picker v-model="form.donation_date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="捐款人" prop="donor_id">
            <el-select
              v-model="form.donor_id"
              filterable
              remote
              :remote-method="searchDonor"
              placeholder="输入姓名搜索"
              style="width: 100%"
            >
              <el-option v-for="d in donorOptions" :key="d.id" :label="d.name" :value="d.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="捐款金额" prop="amount">
            <el-input-number
              v-model="form.amount"
              :precision="2"
              :min="0.01"
              :controls="false"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="捐款目标" prop="target_id">
            <el-select v-model="form.target_id" placeholder="请选择" style="width: 100%">
              <el-option v-for="t in targetOptions" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="支付方式" prop="payment_method">
            <el-select v-model="form.payment_method" style="width: 100%">
              <el-option label="现金" value="cash" />
              <el-option label="银行转账" value="bank" />
              <el-option label="支付宝" value="alipay" />
              <el-option label="微信支付" value="wechat" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="是否开票">
            <el-switch v-model="form.receipt_flag" />
          </el-form-item>
        </el-col>
        <el-col v-if="form.receipt_flag" :span="12">
          <el-form-item label="票据编号" prop="receipt_no">
            <el-input v-model="form.receipt_no" />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="3" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item>
        <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { createDonationApi, getDonationDetailApi, updateDonationApi } from '@/api/donation'
import { getDonorListApi } from '@/api/donor'
import { getTargetListApi } from '@/api/target'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const formRef = ref()
const saving = ref(false)
const donorOptions = ref([])
const targetOptions = ref([])

const form = reactive({
  donation_date: '',
  donor_id: '',
  amount: null,
  target_id: '',
  payment_method: 'bank',
  receipt_flag: false,
  receipt_no: '',
  remark: '',
})

const rules = {
  donation_date: [{ required: true, message: '请选择捐款日期', trigger: 'change' }],
  donor_id: [{ required: true, message: '请选择捐款人', trigger: 'change' }],
  amount: [{ required: true, message: '请输入捐款金额', trigger: 'blur' }],
  target_id: [{ required: true, message: '请选择捐款目标', trigger: 'change' }],
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }],
}

async function searchDonor(keyword) {
  if (!keyword) return
  const res = await getDonorListApi({ name: keyword, page_size: 20 })
  donorOptions.value = res.items
}

async function handleSubmit() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await updateDonationApi(route.params.id, form)
      ElMessage.success('更新成功')
    } else {
      await createDonationApi(form)
      ElMessage.success('新增成功')
    }
    router.push('/donation')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const res = await getTargetListApi({ status: 'active', page_size: 100 })
  targetOptions.value = res.items

  if (isEdit.value) {
    const data = await getDonationDetailApi(route.params.id)
    Object.assign(form, {
      donation_date: data.donation_date,
      donor_id: data.donor_id,
      amount: Number(data.amount),
      target_id: data.target_id,
      payment_method: data.payment_method,
      receipt_flag: data.receipt_flag,
      receipt_no: data.receipt_no,
      remark: data.remark,
    })
    donorOptions.value = [{ id: data.donor_id, name: data.donor_name }]
  }
})
</script>
