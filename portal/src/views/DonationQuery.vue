<template>
  <section class="page">
    <h1 class="page-title">捐赠查询</h1>
    <p class="page-desc">输入捐赠人名称，并可结合日期范围或年份查询公开捐赠记录。</p>

    <div class="toolbar">
      <el-form :model="query" label-position="top" class="query-form">
        <el-form-item label="捐赠人">
          <el-input v-model="query.donor_name" placeholder="请输入捐赠人姓名或企业名称" clearable />
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
        <el-form-item label="年份">
          <el-input-number v-model="query.year" :min="2000" :max="2100" controls-position="right" />
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" :icon="Search" :loading="loading" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div v-if="summary" class="summary-grid">
      <div class="summary-item">
        <span>累计捐赠笔数</span>
        <strong>{{ summary.total_count }}</strong>
      </div>
      <div class="summary-item">
        <span>累计捐赠金额</span>
        <strong>¥{{ formatMoney(summary.total_amount) }}</strong>
      </div>
    </div>

    <div class="content-band">
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column prop="donation_no" label="捐赠编号" min-width="150" />
        <el-table-column prop="donor_name" label="捐赠人" min-width="140" />
        <el-table-column prop="donation_date" label="捐赠日期" width="130" />
        <el-table-column prop="amount" label="金额" width="140" align="right">
          <template #default="{ row }">
            <span class="money">¥{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="target_name" label="捐赠项目" min-width="160" />
      </el-table>

      <el-empty v-if="!loading && searched && items.length === 0" description="暂无匹配记录" />

      <el-pagination
        v-if="total > 0"
        layout="prev, pager, next, total"
        :total="total"
        :page-size="query.page_size"
        :current-page="query.page"
        @current-change="handlePageChange"
      />
    </div>

    <section v-if="gratitudeSummary && gratitudeSummary.total_count > 0" class="gratitude-panel">
      <p class="gratitude-line">
        尊敬的 <strong class="director-name">{{ directorName }}</strong> 理事：
      </p>
      <p>
        感谢您的捐赠，截至目前，您已累计捐赠
        <strong class="gratitude-amount">{{ formatMoney(gratitudeSummary.total_amount) }}</strong>
        元，期待您的下次捐赠！
      </p>
      <p>您的福业，福莲的未来。您的每一分捐赠，都将用于连城教育事业的发展！</p>
      <p>
        这是您加入福莲的第
        <strong class="gratitude-years">{{ displaySupportYears }}</strong>
        年，期待未来继续与福莲同行！
      </p>
      <p>花开福莲，香逸四海！</p>
      <p class="gratitude-sign">福莲教育促进会</p>
    </section>
  </section>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { getDonationSummaryApi, queryDonationsApi } from '@/api/public'

const loading = ref(false)
const searched = ref(false)
const dateRange = ref([])
const items = ref([])
const total = ref(0)
const summary = ref(null)
const gratitudeSummary = ref(null)

const query = reactive({
  donor_name: '',
  year: null,
  page: 1,
  page_size: 10,
})

function formatMoney(value) {
  return Number(value || 0).toFixed(2)
}

const directorName = computed(() => gratitudeSummary.value?.donor_name || query.donor_name.trim())
const displaySupportYears = computed(() => {
  const supportYears = Number(gratitudeSummary.value?.support_years || 0)
  return supportYears > 0 ? supportYears : '待更新'
})

function buildParams() {
  return {
    ...query,
    date_from: dateRange.value?.[0],
    date_to: dateRange.value?.[1],
  }
}

async function fetchData() {
  if (!query.donor_name.trim()) {
    ElMessage.warning('请输入捐赠人名称')
    return
  }
  loading.value = true
  searched.value = true
  try {
    const params = buildParams()
    const [listRes, summaryRes, gratitudeRes] = await Promise.all([
      queryDonationsApi(params),
      getDonationSummaryApi({ donor_name: query.donor_name, year: query.year }),
      getDonationSummaryApi({ donor_name: query.donor_name }),
    ])
    items.value = listRes.items || []
    total.value = listRes.total || 0
    summary.value = summaryRes
    gratitudeSummary.value = gratitudeRes
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchData()
}

function handleReset() {
  query.donor_name = ''
  query.year = null
  query.page = 1
  dateRange.value = []
  items.value = []
  total.value = 0
  summary.value = null
  gratitudeSummary.value = null
  searched.value = false
}

function handlePageChange(page) {
  query.page = page
  fetchData()
}
</script>

<style scoped>
.query-form {
  display: grid;
  grid-template-columns: minmax(220px, 1.2fr) minmax(280px, 1.4fr) 160px auto;
  gap: 14px;
  align-items: end;
}

.query-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.form-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.summary-item {
  padding: 20px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.summary-item span {
  display: block;
  color: #6b7280;
}

.summary-item strong {
  display: block;
  margin-top: 8px;
  font-size: 28px;
  color: #0f766e;
}

.el-pagination {
  justify-content: flex-end;
  margin-top: 18px;
}

.gratitude-panel {
  margin-top: 24px;
  padding: 26px 28px;
  color: #1f2937;
  background: linear-gradient(135deg, #ffffff 0%, #f0fdfa 100%);
  border: 1px solid #bfe9df;
  border-radius: 8px;
  box-shadow: 0 14px 32px rgba(15, 118, 110, 0.08);
  line-height: 2;
}

.gratitude-panel p {
  margin: 0;
  font-size: 17px;
}

.gratitude-line {
  margin-bottom: 4px;
}

.director-name {
  padding: 0 4px;
  color: #0f766e;
  font-size: 24px;
  font-weight: 800;
}

.gratitude-amount,
.gratitude-years {
  color: #b45309;
  font-size: 22px;
  font-weight: 800;
}

.gratitude-sign {
  margin-top: 10px !important;
  color: #0f766e;
  font-weight: 700;
  text-align: right;
}

@media (max-width: 920px) {
  .query-form,
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .gratitude-panel {
    padding: 20px;
  }

  .gratitude-panel p {
    font-size: 16px;
  }

  .director-name {
    font-size: 22px;
  }
}
</style>
