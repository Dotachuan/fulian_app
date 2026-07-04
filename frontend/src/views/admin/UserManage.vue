<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>用户管理</span>
        <el-button type="primary" :icon="Plus" @click="openDialog()">新增用户</el-button>
      </div>
    </template>

    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="roleTagMap[row.role]?.type" size="small">
            {{ roleTagMap[row.role]?.label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link @click="resetPwd(row)">重置密码</el-button>
          <el-button
            link
            :type="row.status === 'active' ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 'active' ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑用户' : '新增用户'" width="440px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="!!editing" />
        </el-form-item>
        <el-form-item v-if="!editing" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="录入人员" value="operator" />
            <el-option label="审核人员" value="reviewer" />
            <el-option label="查询用户" value="viewer" />
          </el-select>
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
import { onMounted, reactive, ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createUserApi, getUserListApi, updateUserApi } from '@/api/auth'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editing = ref(null)
const formRef = ref()
const form = reactive({ username: '', password: '', role: 'operator' })

const roleTagMap = {
  admin: { label: '管理员', type: 'danger' },
  operator: { label: '录入人员', type: 'primary' },
  reviewer: { label: '审核人员', type: 'warning' },
  viewer: { label: '查询用户', type: 'info' },
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

async function loadList() {
  loading.value = true
  try {
    const res = await getUserListApi()
    list.value = res.items
  } finally {
    loading.value = false
  }
}

function openDialog(row = null) {
  editing.value = row
  if (row) {
    Object.assign(form, { username: row.username, role: row.role, password: '' })
  } else {
    Object.assign(form, { username: '', password: '', role: 'operator' })
  }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editing.value) {
      await updateUserApi(editing.value.id, { role: form.role })
    } else {
      await createUserApi(form)
    }
    ElMessage.success('操作成功')
    dialogVisible.value = false
    loadList()
  } finally {
    saving.value = false
  }
}

async function toggleStatus(row) {
  const newStatus = row.status === 'active' ? 'inactive' : 'active'
  await updateUserApi(row.id, { status: newStatus })
  ElMessage.success('操作成功')
  loadList()
}

async function resetPwd(row) {
  await ElMessageBox.prompt('请输入新密码', '重置密码', {
    inputType: 'password',
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  })
    .then(async ({ value }) => {
      await updateUserApi(row.id, { password: value })
      ElMessage.success('密码重置成功')
    })
    .catch(() => {})
}

onMounted(() => loadList())
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
