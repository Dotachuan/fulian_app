const LOCAL_API_ORIGIN = 'http://127.0.0.1:8000'
const REMOTE_API_ORIGIN = 'https://api.fulian520.com'
const API_PREFIX = '/api/v1'

const H5_API_BASE_URL = import.meta.env.VITE_H5_API_BASE_URL || `${LOCAL_API_ORIGIN}${API_PREFIX}`
const MP_WEIXIN_API_BASE_URL =
  import.meta.env.VITE_MP_WEIXIN_API_BASE_URL || `${REMOTE_API_ORIGIN}${API_PREFIX}`

export function getBaseUrl() {
  // #ifdef MP-WEIXIN
  return MP_WEIXIN_API_BASE_URL
  // #endif

  // #ifdef H5
  return H5_API_BASE_URL
  // #endif

  return H5_API_BASE_URL
}
