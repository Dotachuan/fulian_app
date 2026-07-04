<template>
  <div class="fund-page">
    <PageCard title="基金使用管理">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基金管理" name="funds">
          <div class="toolbar">
            <el-select v-model="fundQuery.status" placeholder="状态" clearable style="width: 140px" @change="loadFunds">
              <el-option label="启用" value="active" />
              <el-option label="停用" value="inactive" />
            </el-select>
            <el-button type="primary" :icon="Plus" @click="openFundDialog()">新增基金</el-button>
          </div>

          <el-table :data="funds" v-loading="fundLoading" stripe>
            <el-table-column prop="name" label="基金名称" min-width="180" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">{{ row.type === 'main' ? '主体' : '子基金' }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sort_order" label="排序" width="90" />
            <el-table-column prop="description" label="说明" min-width="220" show-overflow-tooltip />
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openFundDialog(row)">编辑</el-button>
                <el-button link type="danger" @click="removeFund(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="收支明细" name="records">
          <div class="toolbar">
            <el-select v-model="usageQuery.fund_id" placeholder="基金" clearable style="width: 220px" @change="loadUsage">
              <el-option v-for="fund in funds" :key="fund.id" :label="fund.name" :value="fund.id" />
            </el-select>
            <el-date-picker
              v-model="usageDateRange"
              type="daterange"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              clearable
              @change="loadUsage"
            />
            <el-button type="primary" :icon="Plus" @click="openUsageDialog()">新增明细</el-button>
          </div>

          <el-table :data="records" v-loading="usageLoading" stripe>
            <el-table-column prop="record_date" label="日期" width="120" />
            <el-table-column prop="fund_id" label="基金" min-width="160">
              <template #default="{ row }">{{ fundName(row.fund_id) }}</template>
            </el-table-column>
            <el-table-column prop="project_desc" label="项目说明" min-width="220" />
            <el-table-column prop="income_amount" label="收入" width="130" align="right">
              <template #default="{ row }">{{ money(row.income_amount) }}</template>
            </el-table-column>
            <el-table-column prop="expense_amount" label="支出" width="130" align="right">
              <template #default="{ row }">{{ money(row.expense_amount) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openUsageDialog(row)">编辑</el-button>
                <el-button link type="danger" @click="removeUsage(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            layout="prev, pager, next, total"
            :total="usageTotal"
            :page-size="usageQuery.page_size"
            :current-page="usageQuery.page"
            @current-change="changeUsagePage"
          />
        </el-tab-pane>
      </el-tabs>
    </PageCard>

    <el-dialog v-model="fundDialogVisible" :title="fundForm.id ? '编辑基金' : '新增基金'" width="520px">
      <el-form :model="fundForm" label-width="90px">
        <el-form-item label="基金名称" required>
          <el-input v-model="fundForm.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="fundForm.type">
            <el-radio label="main">主体</el-radio>
            <el-radio label="sub">子基金</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="fundForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="fundForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="fundForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFund">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="usageDialogVisible" :title="usageForm.id ? '编辑明细' : '新增明细'" width="560px">
      <el-form :model="usageForm" label-width="90px">
        <el-form-item label="基金" required>
          <el-select v-model="usageForm.fund_id" placeholder="请选择基金" style="width: 100%">
            <el-option v-for="fund in funds" :key="fund.id" :label="fund.name" :value="fund.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker v-model="usageForm.record_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="项目说明" required>
          <el-input v-model="usageForm.project_desc" />
        </el-form-item>
        <el-form-item label="收入金额">
          <el-input-number v-model="usageForm.income_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="支出金额">
          <el-input-number v-model="usageForm.expense_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="usageForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="usageDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUsage">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PageCard from '@/components/PageCard.vue'
import {
  createFundApi,
  createFundUsageApi,
  deleteFundApi,
  deleteFundUsageApi,
  getFundListApi,
  getFundUsageListApi,
  updateFundApi,
  updateFundUsageApi,
} from '@/api/fund'

const activeTab = ref('funds')
const funds = ref([])
const records = ref([])
const fundLoading = ref(false)
const usageLoading = ref(false)
const fundDialogVisible = ref(false)
const usageDialogVisible = ref(false)
const usageDateRange = ref([])
const usageTotal = ref(0)

const fundQuery = reactive({ status: '' })
const usageQuery = reactive({ fund_id: null, page: 1, page_size: 20 })
const fundForm = reactive({ id: null, name: '', type: 'sub', status: 'active', sort_order: 0, description: '' })
const usageForm = reactive({
  id: null,
  fund_id: null,
  record_date: '',
  project_desc: '',
  income_amount: 0,
  expense_amount: 0,
  remark: '',
})

function money(value) {
  return Number(value || 0).toFixed(2)
}

function fundName(id) {
  return funds.value.find((item) => item.id === id)?.name || '-'
}

async function loadFunds() {
  fundLoading.value = true
  try {
    const res = await getFundListApi({ ...fundQuery, page: 1, page_size: 1000 })
    funds.value = res.items || []
  } finally {
    fundLoading.value = false
  }
}

async function loadUsage() {
  usageLoading.value = true
  try {
    const res = await getFundUsageListApi({
      ...usageQuery,
      date_from: usageDateRange.value?.[0],
      date_to: usageDateRange.value?.[1],
    })
    records.value = res.items || []
    usageTotal.value = res.total || 0
  } finally {
    usageLoading.value = false
  }
}

function openFundDialog(row) {
  Object.assign(fundForm, row || { id: null, name: '', type: 'sub', status: 'active', sort_order: 0, description: '' })
  fundDialogVisible.value = true
}

async function saveFund() {
  if (!fundForm.name.trim()) {
    ElMessage.warning('请输入基金名称')
    return
  }
  const payload = { ...fundForm }
  delete payload.id
  if (fundForm.id) {
    await updateFundApi(fundForm.id, payload)
  } else {
    await createFundApi(payload)
  }
  ElMessage.success('保存成功')
  fundDialogVisible.value = false
  await loadFunds()
}

async function removeFund(row) {
  await ElMessageBox.confirm(`确认删除基金“${row.name}”？`, '提示', { type: 'warning' })
  await deleteFundApi(row.id)
  ElMessage.success('删除成功')
  await loadFunds()
}

function openUsageDialog(row) {
  Object.assign(
    usageForm,
    row || {
      id: null,
      fund_id: usageQuery.fund_id,
      record_date: '',
      project_desc: '',
      income_amount: 0,
      expense_amount: 0,
      remark: '',
    }
  )
  usageDialogVisible.value = true
}

async function saveUsage() {
  if (!usageForm.fund_id || !usageForm.record_date || !usageForm.project_desc.trim()) {
    ElMessage.warning('请填写基金、日期和项目说明')
    return
  }
  const payload = { ...usageForm }
  delete payload.id
  if (usageForm.id) {
    await updateFundUsageApi(usageForm.id, payload)
  } else {
    await createFundUsageApi(payload)
  }
  ElMessage.success('保存成功')
  usageDialogVisible.value = false
  await loadUsage()
}

async function removeUsage(row) {
  await ElMessageBox.confirm('确认删除该收支明细？', '提示', { type: 'warning' })
  await deleteFundUsageApi(row.id)
  ElMessage.success('删除成功')
  await loadUsage()
}

function changeUsagePage(page) {
  usageQuery.page = page
  loadUsage()
}

onMounted(async () => {
  await loadFunds()
  await loadUsage()
})
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
</style>

