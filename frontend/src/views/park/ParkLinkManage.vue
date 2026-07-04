<template>
  <PageCard title="产业园链接管理">
    <div class="toolbar">
      <el-input v-model="query.title" placeholder="标题关键词" clearable style="width: 240px" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
        <el-option label="已发布" value="published" />
        <el-option label="草稿" value="draft" />
        <el-option label="下线" value="offline" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      <el-button type="primary" :icon="Plus" @click="openDialog()">新增链接</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="image_url" label="图片 URL" min-width="240" show-overflow-tooltip />
      <el-table-column prop="target_url" label="跳转链接" min-width="240" show-overflow-tooltip />
      <el-table-column prop="published_at" label="发布时间" width="140" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_featured" label="首页展示" width="100">
        <template #default="{ row }">{{ row.is_featured ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openTarget(row)">预览链接</el-button>
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="removeLink(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑产业园链接' : '新增产业园链接'" width="760px">
      <el-form :model="form" label-width="96px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="图片">
          <ImageUploadField v-model="form.image_url" folder="park-links" placeholder="可手填图片 URL，或直接上传图片" />
        </el-form-item>
        <el-form-item label="跳转链接" required>
          <el-input v-model="form.target_url" placeholder="点击图片后跳转的 URL" />
        </el-form-item>
        <el-form-item label="录入提示">
          <div class="field-hint">若需在小程序中打开，请优先填写关联公众号文章链接（mp.weixin.qq.com）。</div>
        </el-form-item>
        <el-form-item label="发布时间">
          <el-date-picker v-model="form.published_at" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="published">已发布</el-radio>
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="offline">下线</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="首页展示">
          <el-switch v-model="form.is_featured" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLink">保存</el-button>
      </template>
    </el-dialog>
  </PageCard>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import PageCard from '@/components/PageCard.vue'
import ImageUploadField from '@/components/ImageUploadField.vue'
import {
  createParkLinkApi,
  deleteParkLinkApi,
  getParkLinkListApi,
  updateParkLinkApi,
} from '@/api/parkLink'

const loading = ref(false)
const dialogVisible = ref(false)
const items = ref([])
const total = ref(0)
const query = reactive({ title: '', status: '', page: 1, page_size: 20 })
const form = reactive({
  id: null,
  title: '',
  summary: '',
  image_url: '',
  target_url: '',
  published_at: '',
  status: 'published',
  is_featured: true,
  sort_order: 0,
})

function statusText(status) {
  return { published: '已发布', draft: '草稿', offline: '下线' }[status] || status
}

function statusType(status) {
  return { published: 'success', draft: 'info', offline: 'warning' }[status] || 'info'
}

async function loadData() {
  loading.value = true
  try {
    const res = await getParkLinkListApi(query)
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

function resetForm() {
  Object.assign(form, {
    id: null,
    title: '',
    summary: '',
    image_url: '',
    target_url: '',
    published_at: '',
    status: 'published',
    is_featured: true,
    sort_order: 0,
  })
}

function openDialog(row) {
  resetForm()
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

function openTarget(row) {
  window.open(row.target_url, '_blank', 'noopener,noreferrer')
}

async function saveLink() {
  if (!form.title.trim() || !form.image_url.trim() || !form.target_url.trim()) {
    ElMessage.warning('请填写标题、图片和跳转链接')
    return
  }
  const payload = { ...form }
  delete payload.id
  if (form.id) {
    await updateParkLinkApi(form.id, payload)
  } else {
    await createParkLinkApi(payload)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

async function removeLink(row) {
  await ElMessageBox.confirm(`确认删除“${row.title}”吗？`, '提示', { type: 'warning' })
  await deleteParkLinkApi(row.id)
  ElMessage.success('删除成功')
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

.field-hint {
  color: #7f8ba3;
  font-size: 12px;
  line-height: 1.6;
}
</style>
