<template>
  <PageCard title="开票申请管理">
    <div class="toolbar">
      <el-input v-model="query.donor_name" placeholder="捐赠人/企业名称" clearable style="width: 220px" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
        <el-option label="待处理" value="pending" />
        <el-option label="已处理" value="processed" />
        <el-option label="已驳回" value="rejected" />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        clearable
      />
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      <el-button type="success" :disabled="selectedRows.length === 0" @click="openBatchDialog">批量处理</el-button>
      <el-button :icon="Download" @click="handleExport">导出待处理</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="48" />
      <el-table-column prop="request_no" label="申请编号" min-width="160" />
      <el-table-column prop="donor_name" label="捐赠人/企业" min-width="160" />
      <el-table-column prop="amount" label="金额" width="130" align="right">
        <template #default="{ row }">{{ money(row.amount) }}</template>
      </el-table-column>
      <el-table-column prop="donation_date" label="捐赠日期" width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column prop="phone" label="电话" min-width="130" />
      <el-table-column prop="identity_no" label="证件号/信用代码" min-width="190" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">处理</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      layout="prev, pager, next, total"
      :total="total"
      :page-size="query.page_size"
      :current-page="query.page"
      @current-change="changePage"
    />

    <el-dialog v-model="dialogVisible" title="处理开票申请" width="520px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="申请编号">{{ current?.request_no }}</el-descriptions-item>
        <el-descriptions-item label="捐赠人">{{ current?.donor_name }}</el-descriptions-item>
        <el-descriptions-item label="金额">{{ money(current?.amount) }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ current?.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-form :model="form" label-width="80px" class="process-form">
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="processed" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStatus">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialogVisible" title="批量处理开票申请" width="520px">
      <el-alert
        :title="`已选择 ${selectedRows.length} 条开票申请`"
        type="info"
        show-icon
        :closable="false"
        class="batch-alert"
      />
      <el-form :model="batchForm" label-width="80px" class="process-form">
        <el-form-item label="状态">
          <el-select v-model="batchForm.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="processed" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="batchForm.remark" type="textarea" :rows="3" placeholder="批量写入备注，可留空" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchSaving" @click="saveBatchStatus">确认处理</el-button>
      </template>
    </el-dialog>
  </PageCard>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import PageCard from '@/components/PageCard.vue'
import {
  batchUpdateInvoiceRequestApi,
  exportInvoiceRequestApi,
  getInvoiceRequestListApi,
  updateInvoiceRequestApi,
} from '@/api/invoiceRequest'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const dateRange = ref([])
const dialogVisible = ref(false)
const batchDialogVisible = ref(false)
const batchSaving = ref(false)
const current = ref(null)
const selectedRows = ref([])
const query = reactive({ donor_name: '', status: '', page: 1, page_size: 20 })
const form = reactive({ status: 'pending', remark: '' })
const batchForm = reactive({ status: 'processed', remark: '' })

function money(value) {
  return Number(value || 0).toFixed(2)
}

function statusText(status) {
  return { pending: '待处理', processed: '已处理', rejected: '已驳回' }[status] || status
}

function statusType(status) {
  return { pending: 'warning', processed: 'success', rejected: 'danger' }[status] || 'info'
}

function params() {
  return {
    ...query,
    date_from: dateRange.value?.[0],
    date_to: dateRange.value?.[1],
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await getInvoiceRequestListApi(params())
    items.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  loadData()
}

function changePage(page) {
  query.page = page
  loadData()
}

function openDialog(row) {
  current.value = row
  form.status = row.status
  form.remark = row.remark || ''
  dialogVisible.value = true
}

function handleSelectionChange(rows) {
  selectedRows.value = rows
}

function openBatchDialog() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择开票申请')
    return
  }
  batchForm.status = 'processed'
  batchForm.remark = ''
  batchDialogVisible.value = true
}

async function saveStatus() {
  await updateInvoiceRequestApi(current.value.id, form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

async function saveBatchStatus() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择开票申请')
    return
  }
  batchSaving.value = true
  try {
    await batchUpdateInvoiceRequestApi({
      ids: selectedRows.value.map((row) => row.id),
      status: batchForm.status,
      remark: batchForm.remark,
    })
    ElMessage.success(`已批量处理 ${selectedRows.value.length} 条申请`)
    batchDialogVisible.value = false
    selectedRows.value = []
    loadData()
  } finally {
    batchSaving.value = false
  }
}

async function handleExport() {
  const { status, page, page_size, ...exportParams } = params()
  const blob = await exportInvoiceRequestApi(exportParams)
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'pending_invoice_requests.xlsx'
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(loadData)
</script>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.el-pagination {
  justify-content: flex-end;
  margin-top: 16px;
}

.process-form {
  margin-top: 18px;
}

.batch-alert {
  margin-bottom: 16px;
}
</style>
