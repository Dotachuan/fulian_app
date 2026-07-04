<template>
  <section class="page">
    <h1 class="page-title">基金使用查询</h1>
    <p class="page-desc">查看主体基金及子基金的收入、支出、结余和项目明细。</p>

    <div class="toolbar">
      <el-form label-position="top" class="fund-toolbar">
        <el-form-item label="基金">
          <el-select v-model="selectedFundId" placeholder="请选择基金" @change="loadUsage">
            <el-option
              v-for="fund in funds"
              :key="fund.id"
              :label="fund.name"
              :value="fund.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            clearable
          />
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" :icon="Search" :loading="loading" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div v-if="summary" class="fund-summary">
      <div>
        <span>总收入</span>
        <strong>¥{{ formatMoney(summary.total_income) }}</strong>
      </div>
      <div>
        <span>总支出</span>
        <strong>¥{{ formatMoney(summary.total_expense) }}</strong>
      </div>
      <div>
        <span>基金结余</span>
        <strong>¥{{ formatMoney(summary.balance) }}</strong>
      </div>
    </div>

    <div v-if="summary?.description" class="content-band fund-desc">
      {{ summary.description }}
    </div>

    <div class="content-band">
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column prop="record_date" label="日期" width="130" />
        <el-table-column prop="project_desc" label="项目说明" min-width="220" />
        <el-table-column prop="income_amount" label="收入金额" width="150" align="right">
          <template #default="{ row }">
            <span class="money income">¥{{ formatMoney(row.income_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="expense_amount" label="支出金额" width="150" align="right">
          <template #default="{ row }">
            <span class="money expense">¥{{ formatMoney(row.expense_amount) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && items.length === 0" description="暂无基金使用记录" />

      <el-pagination
        v-if="total > 0"
        layout="prev, pager, next, total"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="handlePageChange"
      />
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'
import { getPublicFundsApi, getPublicFundUsageApi } from '@/api/public'

const funds = ref([])
const selectedFundId = ref(null)
const dateRange = ref([])
const loading = ref(false)
const summary = ref(null)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

function formatMoney(value) {
  return Number(value || 0).toFixed(2)
}

async function loadFunds() {
  const res = await getPublicFundsApi()
  funds.value = res.items || []
  if (funds.value.length > 0 && !selectedFundId.value) {
    selectedFundId.value = funds.value[0].id
    await loadUsage()
  }
}

async function loadUsage() {
  if (!selectedFundId.value) return
  loading.value = true
  try {
    const res = await getPublicFundUsageApi(selectedFundId.value, {
      page: page.value,
      page_size: pageSize,
      date_from: dateRange.value?.[0],
      date_to: dateRange.value?.[1],
    })
    summary.value = res.summary
    items.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadUsage()
}

function handleReset() {
  dateRange.value = []
  page.value = 1
  loadUsage()
}

function handlePageChange(value) {
  page.value = value
  loadUsage()
}

onMounted(loadFunds)
</script>

<style scoped>
.fund-toolbar {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(280px, 1.2fr) auto;
  gap: 14px;
  align-items: end;
}

.fund-toolbar :deep(.el-form-item) {
  margin-bottom: 0;
}

.form-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
}

.fund-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.fund-summary div {
  padding: 20px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.fund-summary span {
  display: block;
  color: #6b7280;
}

.fund-summary strong {
  display: block;
  margin-top: 8px;
  font-size: 26px;
  color: #0f766e;
}

.fund-desc {
  color: #4b5563;
  line-height: 1.8;
}

.income {
  color: #0f766e;
}

.expense {
  color: #dc2626;
}

.el-pagination {
  justify-content: flex-end;
  margin-top: 18px;
}

@media (max-width: 920px) {
  .fund-toolbar,
  .fund-summary {
    grid-template-columns: 1fr;
  }
}
</style>

