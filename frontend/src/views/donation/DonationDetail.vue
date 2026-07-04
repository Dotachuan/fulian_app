<template>
  <div v-loading="loading">
    <div class="detail-header">
      <el-button :icon="ArrowLeft" @click="$router.back()">返回</el-button>
      <span class="detail-title">捐款详情</span>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="never" header="基本信息">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="捐款编号">{{ detail.donation_no }}</el-descriptions-item>
            <el-descriptions-item label="捐款日期">{{ detail.donation_date }}</el-descriptions-item>
            <el-descriptions-item label="捐款金额">
              <span class="amount-text">¥ {{ Number(detail.amount || 0).toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="支付方式">{{ detail.payment_method }}</el-descriptions-item>
            <el-descriptions-item label="捐款目标">{{ detail.target_name }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusTagMap[detail.status]?.type" size="small">
                {{ statusTagMap[detail.status]?.label }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="是否开票">{{ detail.receipt_flag ? '是' : '否' }}</el-descriptions-item>
            <el-descriptions-item label="票据编号">{{ detail.receipt_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ detail.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" header="捐款人信息" style="margin-top: 16px">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名/单位">{{ detail.donor?.name }}</el-descriptions-item>
            <el-descriptions-item label="类型">
              {{ detail.donor?.type === 'person' ? '个人' : '企业' }}
            </el-descriptions-item>
            <el-descriptions-item label="联系方式">{{ detail.donor?.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ detail.donor?.address || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never" header="操作日志">
          <el-timeline>
            <el-timeline-item
              v-for="log in detail.logs"
              :key="log.id"
              :timestamp="log.created_at"
              placement="top"
            >
              <span class="log-text">{{ log.username }} {{ actionMap[log.action] || log.action }}</span>
            </el-timeline-item>
            <el-timeline-item v-if="!detail.logs?.length" timestamp="">
              暂无日志
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import { getDonationDetailApi } from '@/api/donation'

const route = useRoute()
const loading = ref(false)
const detail = ref({})

const statusTagMap = {
  normal: { label: '正常', type: 'success' },
  pending: { label: '待审核', type: 'warning' },
  void: { label: '作废', type: 'danger' },
}

const actionMap = {
  create: '创建了此记录',
  update: '修改了此记录',
  delete: '删除了此记录',
  void: '作废了此记录',
}

onMounted(async () => {
  loading.value = true
  try {
    detail.value = await getDonationDetailApi(route.params.id)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
}

.amount-text {
  color: #f56c6c;
  font-weight: 700;
  font-size: 16px;
}

.log-text {
  font-size: 13px;
  color: #595959;
}
</style>
