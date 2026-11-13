import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail = error.response?.data?.detail
    let message = error.message || '请求失败'
    if (Array.isArray(detail)) {
      message = detail.map((item) => `${(item.loc || []).slice(1).join('.') || '字段'}: ${item.msg}`).join('；')
    } else if (typeof detail === 'string') {
      message = detail
    }
    const normalized = new Error(message)
    normalized.status = error.response?.status
    return Promise.reject(normalized)
  },
)

export function listRecords(params) {
  return request.get('/production-records', { params })
}

export function getRecord(id) {
  return request.get(`/production-records/${id}`)
}

export function createRecord(data) {
  return request.post('/production-records', data)
}

export function updateRecord(id, data) {
  return request.put(`/production-records/${id}`, data)
}

export function getDailyReport(date) {
  return request.get(`/daily-reports/${date}`)
}

export function getTrends(params) {
  return request.get('/production-trends', { params })
}
