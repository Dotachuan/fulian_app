import { clearAuth, getToken, goLogin } from './auth'
import { getBaseUrl } from '../config/env'

function normalizeErrorDetail(detail) {
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((item) => item?.msg || item?.message || '')
      .filter(Boolean)
      .join('；')
  }
  return '请求失败'
}

export function request({ url, method = 'GET', data, auth = false, silentAuthRedirect = false }) {
  return new Promise((resolve, reject) => {
    const headers = {}
    if (auth && getToken()) {
      headers.Authorization = `Bearer ${getToken()}`
    }

    uni.request({
      url: `${getBaseUrl()}${url}`,
      method,
      data,
      header: headers,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
          return
        }

        const detail = normalizeErrorDetail(res.data?.detail)
        const error = {
          statusCode: res.statusCode,
          detail,
          data: res.data,
          raw: res,
        }

        if (res.statusCode === 401 && auth) {
          clearAuth()
          if (!silentAuthRedirect) {
            uni.showToast({ title: '登录状态已失效，请重新登录', icon: 'none' })
            goLogin()
          }
          reject(error)
          return
        }

        uni.showToast({
          title: detail,
          icon: 'none',
        })
        reject(error)
      },
      fail: (err) => {
        uni.showToast({
          title: '网络请求失败',
          icon: 'none',
        })
        reject({
          statusCode: 0,
          detail: '网络请求失败',
          raw: err,
        })
      },
    })
  })
}
