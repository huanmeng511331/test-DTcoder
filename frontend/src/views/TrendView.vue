<template>
  <el-card shadow="never">
    <div class="toolbar">
      <el-radio-group v-model="metric" @change="renderChart">
        <el-radio-button value="crude_oil_output">原油产量（吨）</el-radio-button>
        <el-radio-button value="natural_gas_output">天然气产量（万m³）</el-radio-button>
        <el-radio-button value="water_injection">注水量（m³）</el-radio-button>
        <el-radio-button value="energy_consumption">能耗（万kWh）</el-radio-button>
      </el-radio-group>
      <el-select v-model="days" style="width: 130px" @change="fetchTrend">
        <el-option :value="7" label="近 7 天" />
        <el-option :value="14" label="近 14 天" />
      </el-select>
    </div>

    <div v-show="points.length > 0" ref="chartEl" class="chart" v-loading="loading" />
    <el-empty v-if="!loading && points.length === 0" description="暂无趋势数据，请先录入生产数据" />
  </el-card>
</template>

<script setup>
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getTrends } from '../api/production'

const METRIC_LABELS = {
  crude_oil_output: '原油产量（吨）',
  natural_gas_output: '天然气产量（万m³）',
  water_injection: '注水量（m³）',
  energy_consumption: '能耗（万kWh）',
}

const metric = ref('crude_oil_output')
const days = ref(7)
const points = ref([])
const loading = ref(false)
const chartEl = ref(null)
let chart = null

async function fetchTrend() {
  loading.value = true
  try {
    points.value = await getTrends({ days: days.value })
    renderChart()
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chart || points.value.length === 0) {
    return
  }
  chart.setOption(
    {
      tooltip: { trigger: 'axis' },
      grid: { left: 70, right: 30, top: 50, bottom: 40 },
      xAxis: { type: 'category', data: points.value.map((point) => point.production_date.slice(5)) },
      yAxis: { type: 'value', name: METRIC_LABELS[metric.value] },
      series: [
        {
          name: METRIC_LABELS[metric.value],
          type: 'line',
          smooth: true,
          data: points.value.map((point) => point[metric.value]),
          areaStyle: { opacity: 0.15 },
          itemStyle: { color: '#409EFF' },
        },
      ],
    },
    true,
  )
}

function handleResize() {
  if (chart) {
    chart.resize()
  }
}

onMounted(async () => {
  chart = echarts.init(chartEl.value)
  window.addEventListener('resize', handleResize)
  await fetchTrend()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.chart {
  width: 100%;
  height: 420px;
}
</style>
