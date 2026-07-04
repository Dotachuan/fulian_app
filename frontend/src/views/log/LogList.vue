<template>
  <el-card shadow="never">
    <template #header>操作日志</template>

    <el-form inline :model="query">
      <el-form-item label="操作类型">
        <el-select v-model="query.action" placeholder="全部" clearable style="width: 120px">
          <el-option label="新增" value="create" />
          <el-option label="修改" value="update" />
          <el-option label="删除" value="delete" />
        </el-select>
      </el-form-item>
      <el-form-item label="时间范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          value-format="YYYY-MM-DD"
          @change="onDateChange"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadList(1)">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="list" v-loading="loading" stripe border style="margin-top: 12px">
      <el-table-column prop="username" label="操作人" width="120" />
      <el-table-column prop="action" label="操作类型" width="100">
        <template #default="{ row }">
          <el-tag :type="actionTagMap[row.action]?.type" size="small">
            {{ actionTagMap[row.action]?.label || row.action }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module" label="模块" width="120" />
      <el-table-column prop="detail" label="操作内容" show-overflow-tooltip />
      <el-table-column prop="created_at" label="操作时间" width="180" />
    </el-table>

    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @change="loadList"
    />
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getLogListApi } from '@/api/stats'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const dateRange = ref([])
const query = reactive({ action: '', date_from: '', date_to: '', page: 1, page_size: 20 })

const actionTagMap = {
  create: { label: '新增', type: 'success' },
  update: { label: '修改', type: 'warning' },
  delete: { label: '删除', type: 'danger' },
}

function onDateChange(val) {
  query.date_from = val?.[0] || ''
  query.date_to = val?.[1] || ''
}

async function loadList(page) {
  if (page) query.page = page
  loading.value = true
  try {
    const res = await getLogListApi(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

onMounted(() => loadList())
</script>
