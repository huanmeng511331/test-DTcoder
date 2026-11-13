<template>
  <div>
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <span class="toolbar-label">日报日期：</span>
        <el-date-picker
          v-model="reportDate"
          type="date"
          value-format="YYYY-MM-DD"
          :disabled-date="disableFuture"
          placeholder="选择日期"
          style="width: 200px"
        />
        <el-button type="primary" :loading="loading" @click="loadReport">生成日报</el-button>
        <el-button @click="gotoCreate">补录当日数据</el-button>
      </div>
    </el-card>

    <template v-if="report">
      <el-alert
        v-for="(alert, index) in report.alerts"
        :key="index"
        class="alert-item"
        :title="alert.message"
        type="warning"
        show-icon
        :closable="false"
      />

      <el-row :gutter="16" class="stat-row">
        <el-col :span="6" v-for="metric in report.comparisons" :key="metric.metric">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">{{ metric.label }}（{{ metric.unit }}）</div>
            <div class="stat-value">{{ formatNumber(metric.current) }}</div>
            <div class="stat-delta" :class="deltaClass(metric)">
              <template v-if="metric.previous === null">无前一日数据</template>
              <template v-else-if="metric.direction === 'flat'">与前一日持平</template>
              <template v-else>
                {{ metric.direction === 'up' ? '▲' : '▼' }} {{ Math.abs(metric.change_ratio) }}%
                （{{ metric.delta > 0 ? '+' : '' }}{{ metric.delta }}）
              </template>
            </div>
            <el-tag v-if="metric.alert" type="danger" size="small" class="alert-tag">超阈值</el-tag>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="14">
          <el-card shadow="never">
            <template #header>自动生成摘要</template>
            <ul class="summary-list">
              <li v-for="(item, index) in report.summary" :key="index">{{ item }}</li>
            </ul>
          </el-card>
        </el-col>
        <el-col :span="10">
          <el-card shadow="never">
            <template #header>当日明细</template>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="生产日期">{{ report.record.production_date }}</el-descriptions-item>
              <el-descriptions-item label="原油产量（吨）">{{ formatNumber(report.record.crude_oil_output) }}</el-descriptions-item>
              <el-descriptions-item label="天然气产量（万m³）">{{ formatNumber(report.record.natural_gas_output) }}</el-descriptions-item>
              <el-descriptions-item label="注水量（m³）">{{ formatNumber(report.record.water_injection, 0) }}</el-descriptions-item>
              <el-descriptions-item label="能耗（万kWh）">{{ formatNumber(report.record.energy_consumption) }}</el-descriptions-item>
              <el-descriptions-item label="停井数量（口）">{{ report.record.shutdown_well_count }}</el-descriptions-item>
              <el-descriptions-item label="异常说明">{{ report.record.abnormal_description || '无' }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ report.record.updated_at }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <el-empty v-else-if="notFound" :description="`${reportDate} 暂无生产数据，请先录入`">
      <el-button type="primary" @click="gotoCreate">去录入</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDailyReport } from '../api/production'
import { formatNumber } from '../utils/format'

const FAVORABLE_DIRECTION = {
  crude_oil_output: 'up',
  natural_gas_output: 'up',
  water_injection: 'up',
  energy_consumption: 'down',
}

const route = useRoute()
const router = useRouter()
const reportDate = ref(route.query.date || new Date().toISOString().slice(0, 10))
const report = ref(null)
const notFound = ref(false)
const loading = ref(false)

function disableFuture(date) {
  return date.getTime() > Date.now()
}

function gotoCreate() {
  router.push(`/records/new?date=${reportDate.value || ''}`)
}

function deltaClass(metric) {
  if (metric.previous === null || metric.direction === 'flat') {
    return 'delta-flat'
  }
  return metric.direction === FAVORABLE_DIRECTION[metric.metric] ? 'delta-good' : 'delta-bad'
}

async function loadReport() {
  if (!reportDate.value) {
    ElMessage.warning('请先选择日期')
    return
  }
  loading.value = true
  notFound.value = false
  report.value = null
  try {
    report.value = await getDailyReport(reportDate.value)
  } catch (error) {
    if (error.status === 404) {
      notFound.value = true
    } else {
      ElMessage.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

watch(
  () => route.query.date,
  (value) => {
    if (value) {
      reportDate.value = value
      loadReport()
    }
  },
)

onMounted(loadReport)
</script>

<style scoped>
.toolbar-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-label {
  color: #606266;
}

.alert-item {
  margin-bottom: 12px;
}

.stat-row {
  margin-bottom: 16px;
}

.stat-card {
  text-align: center;
}

.stat-label {
  color: #909399;
  font-size: 13px;
}

.stat-value {
  font-size: 26px;
  font-weight: 600;
  color: #303133;
  margin: 8px 0;
}

.stat-delta {
  font-size: 13px;
}

.delta-good {
  color: #67c23a;
}

.delta-bad {
  color: #f56c6c;
}

.delta-flat {
  color: #909399;
}

.alert-tag {
  margin-top: 6px;
}

.summary-list {
  margin: 0;
  padding-left: 20px;
  line-height: 2;
  color: #303133;
}
</style>
