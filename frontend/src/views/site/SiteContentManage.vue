<template>
  <PageCard title="站点内容配置">
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="key" label="键值" width="120" />
      <el-table-column prop="title" label="标题" width="140" />
      <el-table-column prop="summary" label="摘要" min-width="220" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="编辑站点内容" width="720px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="正文">
          <el-input v-model="form.content" type="textarea" :rows="10" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="published">发布</el-radio>
            <el-radio label="draft">草稿</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveContent">保存</el-button>
      </template>
    </el-dialog>
  </PageCard>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageCard from '@/components/PageCard.vue'
import { getSiteContentListApi, updateSiteContentApi } from '@/api/siteContent'

const loading = ref(false)
const dialogVisible = ref(false)
const items = ref([])
const currentKey = ref('')
const form = reactive({ title: '', summary: '', content: '', status: 'published' })

async function loadData() {
  loading.value = true
  try {
    items.value = await getSiteContentListApi()
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  currentKey.value = row.key
  Object.assign(form, {
    title: row.title || '',
    summary: row.summary || '',
    content: row.content || '',
    status: row.status || 'published',
  })
  dialogVisible.value = true
}

async function saveContent() {
  await updateSiteContentApi(currentKey.value, form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>
