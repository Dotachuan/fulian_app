<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col v-for="card in statCards" :key="card.label" :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-inner">
            <div>
              <div class="stat-label">{{ card.label }}</div>
              <div class="stat-value">{{ card.value }}</div>
            </div>
            <el-icon :style="{ color: card.color, fontSize: '42px' }">
              <component :is="card.icon" />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="never" header="近 12 个月捐款趋势">
          <div ref="trendChartEl" style="height: 280px" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" header="捐款目标占比">
          <div ref="pieChartEl" style="height: 280px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getStatsByTargetApi, getStatsOverviewApi, getStatsTrendApi } from '@/api/stats'

const statCards = ref([
  { label: '总捐款金额（元）', value: '--', icon: 'Money', color: '#409eff' },
  { label: '总捐款笔数', value: '--', icon: 'Document', color: '#67c23a' },
  { label: '本月捐款金额', value: '--', icon: 'TrendCharts', color: '#e6a23c' },
  { label: '捐款人总数', value: '--', icon: 'User', color: '#f56c6c' },
])

const trendChartEl = ref()
const pieChartEl = ref()
let trendChart
let pieChart

async function loadOverview() {
  try {
    const data = await getStatsOverviewApi()
    statCards.value[0].value = Number(data.total_amount).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
    statCards.value[1].value = data.total_count
    statCards.value[2].value = Number(data.month_amount).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
    statCards.value[3].value = data.donor_count
  } catch {}
}

async function initTrendChart() {
  trendChart = echarts.init(trendChartEl.value)
  try {
    const data = await getStatsTrendApi({ period: 'month', limit: 12 })
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.map((d) => d.period) },
      yAxis: { type: 'value', name: '金额（元）' },
      series: [
        {
          name: '捐款金额',
          type: 'line',
          smooth: true,
          data: data.map((d) => d.amount),
          areaStyle: {},
        },
      ],
    })
  } catch {}
}

async function initPieChart() {
  pieChart = echarts.init(pieChartEl.value)
  try {
    const data = await getStatsByTargetApi()
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          data: data.map((d) => ({ name: d.target_name, value: d.amount })),
        },
      ],
    })
  } catch {}
}

function onResize() {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  loadOverview()
  initTrendChart()
  initPieChart()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  trendChart?.dispose()
  pieChart?.dispose()
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.stat-card {
  border-radius: 10px;
}

.stat-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #262626;
}
</style>
