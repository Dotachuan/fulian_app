<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>捐赠人管理</span>
        <div class="header-actions">
          <el-button :icon="Download" @click="handleExportCodes">导出绑定码 Excel</el-button>
          <el-button type="success" :icon="Key" @click="handleBatchGenerate">批量生成绑定码</el-button>
          <el-button type="primary" :icon="Plus" @click="openDialog()">新增捐赠人</el-button>
        </div>
      </div>
    </template>

    <el-form inline :model="query">
      <el-form-item>
        <el-input
          v-model="query.name"
          placeholder="姓名 / 单位名称"
          clearable
          :prefix-icon="Search"
          @keyup.enter="loadList(1)"
        />
      </el-form-item>
      <el-form-item>
        <el-select v-model="query.type" placeholder="类型" clearable style="width: 110px">
          <el-option label="个人" value="person" />
          <el-option label="企业" value="company" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadList(1)">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="name" label="姓名 / 单位" min-width="180" />
      <el-table-column prop="type" label="类型" width="80">
        <template #default="{ row }">
          {{ row.type === 'person' ? '个人' : '企业' }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="联系方式" width="140" />
      <el-table-column prop="binding_code" label="绑定码" width="130">
        <template #default="{ row }">
          <span v-if="row.binding_code" class="binding-code">{{ row.binding_code }}</span>
          <span v-else class="muted-text">未生成</span>
        </template>
      </el-table-column>
      <el-table-column prop="binding_code_status" label="绑定码状态" width="120">
        <template #default="{ row }">
          <el-tag :type="bindingStatusType(row.binding_code_status)">{{ bindingStatusText(row.binding_code_status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="binding_bound_member_name" label="已绑定会员" min-width="120">
        <template #default="{ row }">
          {{ row.binding_bound_member_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="address" label="地址" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @change="loadList"
    />

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑捐赠人' : '新增捐赠人'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio value="person">个人</el-radio>
            <el-radio value="company">企业</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="姓名/单位" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import dayjs from 'dayjs'
import { onMounted, reactive, ref } from 'vue'
import { Download, Key, Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  batchGenerateDonorBindingCodesApi,
  createDonorApi,
  deleteDonorApi,
  exportDonorBindingCodesApi,
  getDonorListApi,
  updateDonorApi,
} from '@/api/donor'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editing = ref(null)
const formRef = ref()

const query = reactive({ name: '', type: '', page: 1, page_size: 20 })
const form = reactive({ type: 'person', name: '', phone: '', address: '', remark: '' })

const rules = {
  name: [{ required: true, message: '请输入姓名或单位名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

function bindingStatusText(status) {
  return {
    active: '可绑定',
    bound: '已绑定',
    disabled: '已停用',
    null: '未生成',
    undefined: '未生成',
  }[String(status)] || '未生成'
}

function bindingStatusType(status) {
  return {
    active: 'success',
    bound: 'info',
    disabled: 'danger',
  }[status] || 'warning'
}

async function loadList(page) {
  if (page) query.page = page
  loading.value = true
  try {
    const res = await getDonorListApi(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function openDialog(row = null) {
  editing.value = row
  if (row) {
    Object.assign(form, {
      type: row.type,
      name: row.name,
      phone: row.phone || '',
      address: row.address || '',
      remark: row.remark || '',
    })
  } else {
    Object.assign(form, { type: 'person', name: '', phone: '', address: '', remark: '' })
  }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editing.value) {
      await updateDonorApi(editing.value.id, form)
      ElMessage.success('更新成功')
    } else {
      await createDonorApi(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除 ${row.name} 吗？`, '提示', { type: 'warning' })
  await deleteDonorApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

async function handleBatchGenerate() {
  const res = await batchGenerateDonorBindingCodesApi({ only_missing: true })
  ElMessage.success(`已生成 ${res.generated_count} 个绑定码，复用 ${res.reused_count} 个`)
  loadList()
}

async function handleExportCodes() {
  const blob = await exportDonorBindingCodesApi({ name: query.name, type: query.type })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `donor_binding_codes_${dayjs().format('YYYYMMDD')}.xlsx`
  link.click()
  window.URL.revokeObjectURL(url)
}

onMounted(() => loadList())
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.binding-code {
  font-family: Consolas, Monaco, monospace;
  font-weight: 700;
  letter-spacing: 1px;
  color: #1f2d3d;
}

.muted-text {
  color: #909399;
}
</style>
