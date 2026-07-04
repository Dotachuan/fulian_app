<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>捐款目标管理</span>
        <el-button type="primary" :icon="Plus" @click="openDialog()">新增目标</el-button>
      </div>
    </template>

    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="code" label="目标编号" width="130" />
      <el-table-column prop="name" label="目标名称" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button
            link
            :type="row.status === 'active' ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 'active' ? '停用' : '启用' }}
          </el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑目标' : '新增目标'" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="目标名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
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
import { createTargetApi, deleteTargetApi, getTargetListApi, updateTargetApi } from '@/api/target'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editing = ref(null)
const formRef = ref()
const form = reactive({ name: '', description: '' })

const rules = {
  name: [{ required: true, message: '请输入目标名称', trigger: 'blur' }],
}

async function loadList() {
  loading.value = true
  try {
    const res = await getTargetListApi({ page_size: 100 })
    list.value = res.items
  } finally {
    loading.value = false
  }
}

function openDialog(row = null) {
  editing.value = row
  if (row) {
    Object.assign(form, {
      name: row.name,
      description: row.description || '',
    })
  } else {
    Object.assign(form, { name: '', description: '' })
  }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editing.value) {
      await updateTargetApi(editing.value.id, form)
      ElMessage.success('更新成功')
    } else {
      await createTargetApi(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    saving.value = false
  }
}

async function toggleStatus(row) {
  const newStatus = row.status === 'active' ? 'inactive' : 'active'
  await updateTargetApi(row.id, { status: newStatus })
  ElMessage.success('操作成功')
  loadList()
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除目标 ${row.name} 吗？`, '提示', { type: 'warning' })
  await deleteTargetApi(row.id)
  ElMessage.success('删除成功')
  loadList()
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
