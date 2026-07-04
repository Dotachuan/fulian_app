<template>
  <div>
    <el-card shadow="never">
      <el-form :model="query" inline class="search-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="onDateChange"
          />
        </el-form-item>
        <el-form-item label="捐款人">
          <el-input v-model="query.donor_name" placeholder="姓名/单位" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="捐款目标">
          <el-select v-model="query.target_id" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="t in targetOptions" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="正常" value="normal" />
            <el-option label="待审核" value="pending" />
            <el-option label="作废" value="void" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadList(1)">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="table-actions">
        <el-button
          v-permission="['admin', 'operator']"
          type="primary"
          :icon="Plus"
          @click="$router.push('/donation/create')"
        >
          新增捐款
        </el-button>
        <el-button :icon="Download" @click="handleExport">导出 Excel</el-button>
        <div class="quick-filter">
          <el-button size="small" @click="setQuick('today')">今日</el-button>
          <el-button size="small" @click="setQuick('month')">本月</el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading" stripe border style="margin-top: 12px">
        <el-table-column prop="donation_no" label="捐款编号" width="160" />
        <el-table-column prop="donation_date" label="捐款日期" width="110" sortable />
        <el-table-column prop="donor_name" label="捐款人" width="140" />
        <el-table-column prop="amount" label="金额（元）" width="120" sortable>
          <template #default="{ row }">
            {{ Number(row.amount).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="target_name" label="捐款目标" />
        <el-table-column prop="payment_method" label="支付方式" width="100" />
        <el-table-column prop="receipt_flag" label="票据" width="80">
          <template #default="{ row }">
            <el-tag :type="row.receipt_flag ? 'success' : 'info'" size="small">
              {{ row.receipt_flag ? '已开票' : '未开票' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagMap[row.status]?.type" size="small">
              {{ statusTagMap[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="录入时间" width="180" />
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/donation/${row.id}`)">查看</el-button>
            <el-button
              v-permission="['admin', 'operator']"
              link
              type="warning"
              @click="$router.push(`/donation/edit/${row.id}`)"
            >
              编辑
            </el-button>
            <el-button v-permission="'admin'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
        @change="loadList"
      />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { Download, Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteDonationApi, exportDonationApi, getDonationListApi } from '@/api/donation'
import { getTargetListApi } from '@/api/target'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const dateRange = ref([])
const targetOptions = ref([])

const query = reactive({
  page: 1,
  page_size: 20,
  donor_name: '',
  target_id: '',
  status: '',
  date_from: '',
  date_to: '',
})

const statusTagMap = {
  normal: { label: '正常', type: 'success' },
  pending: { label: '待审核', type: 'warning' },
  void: { label: '作废', type: 'danger' },
}

function onDateChange(val) {
  query.date_from = val?.[0] || ''
  query.date_to = val?.[1] || ''
}

function setQuick(type) {
  const now = dayjs()
  if (type === 'today') {
    const today = now.format('YYYY-MM-DD')
    dateRange.value = [today, today]
    query.date_from = today
    query.date_to = today
  } else {
    query.date_from = now.startOf('month').format('YYYY-MM-DD')
    query.date_to = now.endOf('month').format('YYYY-MM-DD')
    dateRange.value = [query.date_from, query.date_to]
  }
  loadList(1)
}

function resetQuery() {
  Object.assign(query, {
    page: 1,
    page_size: 20,
    donor_name: '',
    target_id: '',
    status: '',
    date_from: '',
    date_to: '',
  })
  dateRange.value = []
  loadList()
}

async function loadList(page) {
  if (page) query.page = page
  loading.value = true
  try {
    const res = await getDonationListApi(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除捐款编号 ${row.donation_no} 吗？`, '提示', { type: 'warning' })
  await deleteDonationApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

async function handleExport() {
  const blob = await exportDonationApi(query)
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `捐款记录_${dayjs().format('YYYYMMDD')}.xlsx`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadList()
  getTargetListApi({ status: 'active' }).then((res) => {
    targetOptions.value = res.items
  })
})
</script>

<style scoped>
.search-form {
  flex-wrap: wrap;
  gap: 4px;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-filter {
  margin-left: auto;
}
</style>
