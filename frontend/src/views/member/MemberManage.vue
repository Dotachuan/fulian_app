<template>
  <PageCard title="会员管理">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="会员列表" name="members">
        <div class="toolbar">
          <el-input v-model="query.keyword" placeholder="手机号 / 姓名" clearable style="width: 220px" />
          <el-select v-model="query.status" placeholder="账号状态" clearable style="width: 140px">
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
          <el-select v-model="query.binding_status" placeholder="绑定状态" clearable style="width: 160px">
            <el-option label="已绑定" value="bound" />
            <el-option label="待绑定" value="unbound" />
            <el-option label="需人工确认" value="ambiguous" />
          </el-select>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        </div>

        <el-table :data="items" v-loading="loading" stripe>
          <el-table-column prop="phone" label="手机号" min-width="140" />
          <el-table-column prop="name" label="姓名" min-width="120" />
          <el-table-column prop="work_unit" label="工作单位" min-width="220" show-overflow-tooltip />
          <el-table-column prop="donor_name" label="绑定捐赠人" min-width="140" />
          <el-table-column label="绑定状态" width="120">
            <template #default="{ row }">
              <el-tag :type="bindingType(row.binding_status)">{{ bindingText(row.binding_status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="绑定来源" width="110">
            <template #default="{ row }">
              <el-tag type="info">{{ bindingSourceText(row.binding_source) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="member_level_label" label="会员身份" width="100" />
          <el-table-column label="账号状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                {{ row.status === 'active' ? '启用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
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
      </el-tab-pane>

      <el-tab-pane label="绑定申请" name="requests">
        <div class="toolbar">
          <el-input v-model="requestQuery.keyword" placeholder="申请姓名 / 申请手机号 / 会员信息" clearable style="width: 280px" />
          <el-select v-model="requestQuery.status" placeholder="申请状态" clearable style="width: 140px">
            <el-option label="待处理" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
          <el-button type="primary" :icon="Search" @click="handleRequestSearch">查询</el-button>
        </div>

        <el-table :data="requestItems" v-loading="requestLoading" stripe>
          <el-table-column prop="name" label="申请姓名" min-width="120" />
          <el-table-column prop="phone" label="申请手机号" min-width="140" />
          <el-table-column prop="member_name" label="会员账号姓名" min-width="130" />
          <el-table-column prop="member_phone" label="会员账号手机号" min-width="150" />
          <el-table-column prop="donor_name" label="已绑定捐赠人" min-width="150" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="requestStatusType(row.status)">{{ requestStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="admin_note" label="处理备注" min-width="180" show-overflow-tooltip />
          <el-table-column prop="created_at" label="提交时间" width="160">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.status === 'pending'" link type="primary" @click="openRequestDialog(row)">处理</el-button>
              <span v-else class="muted">已处理</span>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          layout="prev, pager, next, total"
          :total="requestTotal"
          :page-size="requestQuery.page_size"
          :current-page="requestQuery.page"
          @current-change="changeRequestPage"
        />
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" title="编辑会员" width="680px">
      <el-form :model="form" label-width="92px">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="工作单位">
          <el-input v-model="form.work_unit" />
        </el-form-item>
        <el-form-item label="绑定捐赠人">
          <el-select
            v-model="form.donor_id"
            filterable
            remote
            clearable
            reserve-keyword
            placeholder="输入姓名或手机号搜索"
            :remote-method="searchDonors"
            :loading="donorLoading"
            style="width: 100%"
          >
            <el-option
              v-for="item in donorOptions"
              :key="item.id"
              :label="`${item.name}${item.phone ? `（${item.phone}）` : ''}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="账号状态">
          <el-radio-group v-model="form.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="同步手机号">
          <el-switch v-model="form.sync_donor_phone" />
          <span class="hint">如已绑定捐赠人，可将当前手机号同步写回捐赠人资料</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMember">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="requestDialogVisible" title="处理绑定申请" width="680px">
      <div v-if="currentRequest" class="request-summary">
        <div>申请姓名：<strong>{{ currentRequest.name }}</strong></div>
        <div>申请手机号：<strong>{{ currentRequest.phone }}</strong></div>
        <div>会员账号：{{ currentRequest.member_name || '-' }} / {{ currentRequest.member_phone || '-' }}</div>
      </div>
      <el-form :model="requestForm" label-width="92px">
        <el-form-item label="绑定捐赠人">
          <el-select
            v-model="requestForm.donor_id"
            filterable
            remote
            clearable
            reserve-keyword
            placeholder="输入捐赠人姓名或手机号搜索后选择"
            :remote-method="searchRequestDonors"
            :loading="donorLoading"
            style="width: 100%"
          >
            <el-option
              v-for="item in requestDonorOptions"
              :key="item.id"
              :label="`${item.name}${item.phone ? `（${item.phone}）` : ''}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model="requestForm.admin_note" type="textarea" :rows="3" placeholder="可填写比对说明或驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="requestDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="rejectRequest">驳回</el-button>
        <el-button type="primary" @click="approveRequest">通过并绑定</el-button>
      </template>
    </el-dialog>
  </PageCard>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import PageCard from '@/components/PageCard.vue'
import {
  approveMemberBindingRequestApi,
  getMemberBindingRequestListApi,
  getMemberDonorOptionsApi,
  getMemberListApi,
  rejectMemberBindingRequestApi,
  updateMemberApi,
} from '@/api/member'

const activeTab = ref('members')
const loading = ref(false)
const requestLoading = ref(false)
const dialogVisible = ref(false)
const requestDialogVisible = ref(false)
const donorLoading = ref(false)
const items = ref([])
const total = ref(0)
const requestItems = ref([])
const requestTotal = ref(0)
const donorOptions = ref([])
const requestDonorOptions = ref([])
const currentId = ref(null)
const currentRequest = ref(null)

const query = reactive({ keyword: '', status: '', binding_status: '', page: 1, page_size: 20 })
const requestQuery = reactive({ keyword: '', status: 'pending', page: 1, page_size: 20 })
const form = reactive({
  phone: '',
  name: '',
  work_unit: '',
  donor_id: null,
  status: 'active',
  note: '',
  sync_donor_phone: false,
})
const requestForm = reactive({
  donor_id: null,
  admin_note: '',
})

function bindingText(status) {
  return { bound: '已绑定', unbound: '待绑定', ambiguous: '需人工确认' }[status] || status
}

function bindingType(status) {
  return { bound: 'success', unbound: 'warning', ambiguous: 'danger' }[status] || 'info'
}

function bindingSourceText(source) {
  return { auto: '自动', manual: '手动', code: '绑定码', request: '申请绑定' }[source] || source || '-'
}

function requestStatusText(status) {
  return { pending: '待处理', approved: '已通过', rejected: '已驳回' }[status] || status
}

function requestStatusType(status) {
  return { pending: 'warning', approved: 'success', rejected: 'info' }[status] || 'info'
}

function formatDateTime(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 16)
}

async function loadData() {
  loading.value = true
  try {
    const res = await getMemberListApi(query)
    items.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

async function loadRequests() {
  requestLoading.value = true
  try {
    const res = await getMemberBindingRequestListApi(requestQuery)
    requestItems.value = res.items || []
    requestTotal.value = res.total || 0
  } finally {
    requestLoading.value = false
  }
}

function handleTabChange(tab) {
  if (tab === 'requests') loadRequests()
}

function handleSearch() {
  query.page = 1
  loadData()
}

function handleRequestSearch() {
  requestQuery.page = 1
  loadRequests()
}

function changePage(page) {
  query.page = page
  loadData()
}

function changeRequestPage(page) {
  requestQuery.page = page
  loadRequests()
}

function openDialog(row) {
  currentId.value = row.id
  Object.assign(form, {
    phone: row.phone || '',
    name: row.name || '',
    work_unit: row.work_unit || '',
    donor_id: row.donor_id || null,
    status: row.status || 'active',
    note: row.note || '',
    sync_donor_phone: false,
  })
  donorOptions.value = row.donor_id ? [{ id: row.donor_id, name: row.donor_name, phone: row.phone }] : []
  dialogVisible.value = true
}

async function searchDonors(keyword) {
  donorLoading.value = true
  try {
    donorOptions.value = await getMemberDonorOptionsApi({ keyword, page_size: 20 })
  } finally {
    donorLoading.value = false
  }
}

async function searchRequestDonors(keyword) {
  donorLoading.value = true
  try {
    requestDonorOptions.value = await getMemberDonorOptionsApi({ keyword, page_size: 20 })
  } finally {
    donorLoading.value = false
  }
}

async function saveMember() {
  await updateMemberApi(currentId.value, form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

async function openRequestDialog(row) {
  currentRequest.value = row
  requestForm.donor_id = row.donor_id || null
  requestForm.admin_note = row.admin_note || ''
  requestDonorOptions.value = []
  requestDialogVisible.value = true
  await searchRequestDonors(row.name || row.phone || '')
}

async function approveRequest() {
  if (!currentRequest.value || !requestForm.donor_id) {
    ElMessage.warning('请先选择要绑定的捐赠人')
    return
  }
  await approveMemberBindingRequestApi(currentRequest.value.id, { ...requestForm })
  ElMessage.success('已通过并完成绑定')
  requestDialogVisible.value = false
  loadRequests()
  loadData()
}

async function rejectRequest() {
  if (!currentRequest.value) return
  await rejectMemberBindingRequestApi(currentRequest.value.id, {
    admin_note: requestForm.admin_note,
  })
  ElMessage.success('已驳回申请')
  requestDialogVisible.value = false
  loadRequests()
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

.hint {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}

.muted {
  color: #909399;
}

.request-summary {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
  padding: 14px 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafbfc;
  color: #303133;
  line-height: 1.6;
}
</style>
