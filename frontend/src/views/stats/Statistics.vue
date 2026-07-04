<template>
  <div>
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form inline :model="query">
        <el-form-item label="统计周期">
          <el-radio-group v-model="query.period" @change="loadAll">
            <el-radio-button value="day">按日</el-radio-button>
            <el-radio-button value="month">按月</el-radio-button>
            <el-radio-button value="year">按年</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            value-format="YYYY-MM-DD"
            @change="onDateChange"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="never" header="捐款趋势">
          <div ref="trendEl" style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-top: 20px">
        <el-card shadow="never" header="按捐款目标统计">
          <div ref="targetEl" style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-top: 20px">
        <el-card shadow="never" header="按支付方式统计">
          <div ref="methodEl" style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { getStatsByMethodApi, getStatsByTargetApi, getStatsTrendApi } from '@/api/stats'

const query = reactive({ period: 'month', date_from: '', date_to: '' })
const dateRange = ref([])

const trendEl = ref()
const targetEl = ref()
const methodEl = ref()
let trendChart
let targetChart
let methodChart

function onDateChange(val) {
  query.date_from = val?.[0] || ''
  query.date_to = val?.[1] || ''
  loadAll()
}

async function loadAll() {
  await Promise.all([loadTrend(), loadTarget(), loadMethod()])
}

async function loadTrend() {
  const data = await getStatsTrendApi(query)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map((d) => d.period) },
    yAxis: [
      { type: 'value', name: '金额（元）' },
      { type: 'value', name: '笔数' },
    ],
    series: [
      { name: '捐款金额', type: 'bar', data: data.map((d) => d.amount) },
      { name: '捐款笔数', type: 'line', yAxisIndex: 1, data: data.map((d) => d.count) },
    ],
  })
}

async function loadTarget() {
  const data = await getStatsByTargetApi(query)
  targetChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['40%', '68%'],
        data: data.map((d) => ({ name: d.target_name, value: d.amount })),
      },
    ],
  })
}

async function loadMethod() {
  const data = await getStatsByMethodApi(query)
  methodChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map((d) => d.method) },
    yAxis: { type: 'value', name: '金额（元）' },
    series: [{ name: '金额', type: 'bar', data: data.map((d) => d.amount) }],
  })
}

function onResize() {
  trendChart?.resize()
  targetChart?.resize()
  methodChart?.resize()
}

onMounted(() => {
  trendChart = echarts.init(trendEl.value)
  targetChart = echarts.init(targetEl.value)
  methodChart = echarts.init(methodEl.value)
  loadAll()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  trendChart?.dispose()
  targetChart?.dispose()
  methodChart?.dispose()
  window.removeEventListener('resize', onResize)
})
</script>
