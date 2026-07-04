<template>
  <PageCard title="会员管理">
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="手机号 / 姓名" clearable style="width: 220px" />
      <el-select v-model="query.status" placeholder="账号状态" clearable style="width: 140px">
        <el-option label="启用" value="active" />
        <el-option label="停用" value="inactive" />
      </el-select>
      <el-select v-model="query.binding_status" placeholder="绑定状态" clearable style="width: 160px">
        <el-option label="已绑定" value="bound" />
        <el-option label="待绑定" value="unbound" />
        <el-option label="手机号重复" value="ambiguous" />
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
          <span class="hint">如已绑定捐赠人，可将当前手机号同步写回 donor</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <div class="binding-code-panel">
        <div class="binding-code-head">
          <div>
            <div class="binding-code-title">绑定码</div>
            <div class="binding-code-subtitle">自动手机号绑定失败时，可生成一次性绑定码给会员在小程序中输入完成绑定。</div>
          </div>
          <el-button type="primary" :disabled="!form.donor_id || !currentId" @click="generateBindingCode">
            生成绑定码
          </el-button>
        </div>

        <div v-if="bindingCode" class="binding-code-result">
          <div class="binding-code-value">{{ bindingCode.code }}</div>
          <div class="binding-code-meta">
            绑定对象：{{ bindingCode.donor_name || '-' }} ｜ 有效期至：{{ formatDateTime(bindingCode.expires_at) }}
          </div>
        </div>
        <div v-else class="binding-code-empty">当前还没有可用绑定码，选择捐赠人后即可生成。</div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMember">保存</el-button>
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
  createMemberBindingCodeApi,
  getMemberBindingCodeApi,
  getMemberDonorOptionsApi,
  getMemberListApi,
  updateMemberApi,
} from '@/api/member'

const loading = ref(false)
const dialogVisible = ref(false)
const donorLoading = ref(false)
const items = ref([])
const total = ref(0)
const donorOptions = ref([])
const currentId = ref(null)
const bindingCode = ref(null)

const query = reactive({ keyword: '', status: '', binding_status: '', page: 1, page_size: 20 })
const form = reactive({
  phone: '',
  name: '',
  work_unit: '',
  donor_id: null,
  status: 'active',
  note: '',
  sync_donor_phone: false,
})

function bindingText(status) {
  return { bound: '已绑定', unbound: '待绑定', ambiguous: '手机号重复' }[status] || status
}

function bindingType(status) {
  return { bound: 'success', unbound: 'warning', ambiguous: 'danger' }[status] || 'info'
}

function bindingSourceText(source) {
  return { auto: '自动', manual: '手动', code: '绑定码' }[source] || '自动'
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

function handleSearch() {
  query.page = 1
  loadData()
}

function changePage(page) {
  query.page = page
  loadData()
}

async function loadBindingCode() {
  if (!currentId.value) return
  try {
    bindingCode.value = await getMemberBindingCodeApi(currentId.value)
  } catch {
    bindingCode.value = null
  }
}

async function openDialog(row) {
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
  bindingCode.value = null
  dialogVisible.value = true
  await loadBindingCode()
}

async function searchDonors(keyword) {
  donorLoading.value = true
  try {
    donorOptions.value = await getMemberDonorOptionsApi({ keyword, page_size: 20 })
  } finally {
    donorLoading.value = false
  }
}

async function generateBindingCode() {
  if (!currentId.value || !form.donor_id) {
    ElMessage.warning('请先选择绑定捐赠人')
    return
  }
  bindingCode.value = await createMemberBindingCodeApi(currentId.value, {
    donor_id: form.donor_id,
    expires_in_days: 7,
  })
  ElMessage.success('绑定码已生成')
}

async function saveMember() {
  await updateMemberApi(currentId.value, form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
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

.binding-code-panel {
  margin-top: 12px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  background: #fafbfc;
}

.binding-code-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.binding-code-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.binding-code-subtitle {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: #909399;
}

.binding-code-result {
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px dashed #d0d7e2;
}

.binding-code-value {
  font-size: 24px;
  line-height: 1;
  letter-spacing: 3px;
  font-weight: 700;
  color: #1f2d3d;
}

.binding-code-meta,
.binding-code-empty {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}
</style>
