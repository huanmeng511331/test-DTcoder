<template>
  <el-card v-loading="loading" shadow="never">
    <template #header>{{ isEdit ? '编辑生产数据' : '录入生产数据' }}</template>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="170px" style="max-width: 680px">
      <el-form-item label="生产日期" prop="production_date">
        <el-date-picker
          v-model="form.production_date"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择日期"
          style="width: 220px"
        />
      </el-form-item>
      <el-form-item label="原油产量（吨）" prop="crude_oil_output">
        <el-input-number v-model="form.crude_oil_output" :min="0" :precision="1" :step="10" :controls="false" style="width: 220px" />
      </el-form-item>
      <el-form-item label="天然气产量（万m³）" prop="natural_gas_output">
        <el-input-number v-model="form.natural_gas_output" :min="0" :precision="1" :step="1" :controls="false" style="width: 220px" />
      </el-form-item>
      <el-form-item label="注水量（m³）" prop="water_injection">
        <el-input-number v-model="form.water_injection" :min="0" :precision="0" :step="10" :controls="false" style="width: 220px" />
      </el-form-item>
      <el-form-item label="能耗（万kWh）" prop="energy_consumption">
        <el-input-number v-model="form.energy_consumption" :min="0" :precision="1" :step="1" :controls="false" style="width: 220px" />
      </el-form-item>
      <el-form-item label="停井数量（口）" prop="shutdown_well_count">
        <el-input-number v-model="form.shutdown_well_count" :min="0" :precision="0" style="width: 220px" />
      </el-form-item>
      <el-form-item label="异常说明" prop="abnormal_description">
        <el-input v-model="form.abnormal_description" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="无异常可留空" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
        <el-button @click="$router.push('/records')">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createRecord, getRecord, updateRecord } from '../api/production'

const route = useRoute()
const router = useRouter()
const recordId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => recordId.value !== null)

const formRef = ref()
const loading = ref(false)
const submitting = ref(false)

const form = reactive({
  production_date: route.query.date || '',
  crude_oil_output: null,
  natural_gas_output: null,
  water_injection: null,
  energy_consumption: null,
  shutdown_well_count: 0,
  abnormal_description: '',
})

const nonNegative = (label) => (rule, value, callback) => {
  if (value === null || value === undefined || value === '') {
    return callback(new Error(`请输入${label}`))
  }
  if (Number(value) < 0) {
    return callback(new Error(`${label}不能为负数`))
  }
  callback()
}

const rules = {
  production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
  crude_oil_output: [{ required: true, validator: nonNegative('原油产量'), trigger: 'blur' }],
  natural_gas_output: [{ required: true, validator: nonNegative('天然气产量'), trigger: 'blur' }],
  water_injection: [{ required: true, validator: nonNegative('注水量'), trigger: 'blur' }],
  energy_consumption: [{ required: true, validator: nonNegative('能耗'), trigger: 'blur' }],
  shutdown_well_count: [{ required: true, validator: nonNegative('停井数量'), trigger: 'blur' }],
}

async function loadRecord() {
  if (!isEdit.value) {
    return
  }
  loading.value = true
  try {
    const record = await getRecord(recordId.value)
    Object.assign(form, record)
  } catch (error) {
    ElMessage.error(error.message)
    router.push('/records')
  } finally {
    loading.value = false
  }
}

async function onSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateRecord(recordId.value, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createRecord({ ...form })
      ElMessage.success('录入成功')
    }
    router.push('/records')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    submitting.value = false
  }
}

onMounted(loadRecord)
</script>
