import axios from 'axios'
import { ElMessage } from 'element-plus'

function cleanParams(params) {
  if (!params || typeof params !== 'object' || Array.isArray(params)) {
    return params
  }
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== '' && value !== null && value !== undefined)
  )
}

function getErrorMessage(error) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string' && detail) {
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0]?.msg || '请求失败，请稍后再试'
  }
  return '请求失败，请稍后再试'
}

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  if (config.params) {
    config.params = cleanParams(config.params)
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    ElMessage.error(getErrorMessage(error))
    return Promise.reject(error)
  }
)

export default request

