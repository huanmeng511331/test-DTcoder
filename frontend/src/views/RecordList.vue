<template>
  <el-card shadow="never">
    <div class="toolbar">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        style="width: 280px"
      />
      <el-button type="primary" :loading="loading" @click="onSearch">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="success" @click="$router.push('/records/new')">录入生产数据</el-button>
    </div>

    <el-table v-loading="loading" :data="records" stripe empty-text="暂无生产数据，点击右上角「录入生产数据」开始">
      <el-table-column prop="production_date" label="生产日期" width="120" />
      <el-table-column label="原油产量（吨）" align="right">
        <template #default="{ row }">{{ formatNumber(row.crude_oil_output) }}</template>
      </el-table-column>
      <el-table-column label="天然气产量（万m³）" align="right">
        <template #default="{ row }">{{ formatNumber(row.natural_gas_output) }}</template>
      </el-table-column>
      <el-table-column label="注水量（m³）" align="right">
        <template #default="{ row }">{{ formatNumber(row.water_injection, 0) }}</template>
      </el-table-column>
      <el-table-column label="能耗（万kWh）" align="right">
        <template #default="{ row }">{{ formatNumber(row.energy_consumption) }}</template>
      </el-table-column>
      <el-table-column prop="shutdown_well_count" label="停井数（口）" width="110" align="right" />
      <el-table-column label="状态" width="130">
        <template #default="{ row }">
          <el-tag v-if="row.abnormal_description" type="danger">异常</el-tag>
          <el-tag v-else-if="row.shutdown_well_count > 0" type="warning">停井 {{ row.shutdown_well_count }} 口</el-tag>
          <el-tag v-else type="success">正常</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/records/${row.id}/edit`)">编辑</el-button>
          <el-button link type="primary" @click="$router.push(`/reports?date=${row.production_date}`)">日报</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      class="pagination"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      @current-change="fetchRecords"
      @size-change="onSizeChange"
    />
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listRecords } from '../api/production'
import { formatNumber } from '../utils/format'

const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const dateRange = ref(null)
const loading = ref(false)

async function fetchRecords() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const data = await listRecords(params)
    records.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchRecords()
}

function onReset() {
  dateRange.value = null
  page.value = 1
  fetchRecords()
}

function onSizeChange() {
  page.value = 1
  fetchRecords()
}

onMounted(fetchRecords)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
