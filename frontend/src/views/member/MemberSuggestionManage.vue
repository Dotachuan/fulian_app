<template>
  <PageCard title="意见建议管理">
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索姓名、手机号、联系方式或内容" clearable style="width: 300px" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
        <el-option label="待处理" value="pending" />
        <el-option label="已处理" value="processed" />
        <el-option label="已驳回" value="rejected" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      <el-button :icon="Download" @click="handleExport">导出 Excel</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="member_name" label="会员姓名" min-width="120" />
      <el-table-column prop="member_phone" label="会员手机号" min-width="140" />
      <el-table-column prop="contact" label="联系方式" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">{{ row.contact || '-' }}</template>
      </el-table-column>
      <el-table-column prop="content" label="建议内容" min-width="380" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" min-width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
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

    <el-dialog v-model="dialogVisible" title="处理意见建议" width="620px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="会员姓名">{{ current?.member_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="会员手机号">{{ current?.member_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系方式">{{ current?.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ formatDateTime(current?.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="建议内容">{{ current?.content || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-form :model="form" label-width="80px" class="process-form">
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="processed" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStatus">保存</el-button>
      </template>
    </el-dialog>
  </PageCard>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import PageCard from '@/components/PageCard.vue'
import { exportMemberSuggestionApi, getMemberSuggestionListApi, updateMemberSuggestionApi } from '@/api/member'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const current = ref(null)
const query = reactive({ keyword: '', status: '', page: 1, page_size: 20 })
const form = reactive({ status: 'pending' })

function statusText(status) {
  return { pending: '待处理', processed: '已处理', rejected: '已驳回' }[status] || status
}

function statusType(status) {
  return { pending: 'warning', processed: 'success', rejected: 'danger' }[status] || 'info'
}

function formatDateTime(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 19)
}

async function loadData() {
  loading.value = true
  try {
    const res = await getMemberSuggestionListApi(query)
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
  dialogVisible.value = true
}

async function saveStatus() {
  if (!current.value) return
  await updateMemberSuggestionApi(current.value.id, { status: form.status })
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

async function handleExport() {
  const blob = await exportMemberSuggestionApi({
    keyword: query.keyword,
    status: query.status,
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'member_suggestions.xlsx'
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
</style>
