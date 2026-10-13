import { request } from '../utils/request'
import { getBaseUrl } from '../config/env'
import { getToken } from '../utils/auth'

export const sendMemberCode = (data) =>
  request({ url: '/member-auth/send-code', method: 'POST', data })

export const loginMember = (data) =>
  request({ url: '/member-auth/login', method: 'POST', data })

export const loginMemberByWechatPhone = (data) =>
  request({ url: '/member-auth/wechat-phone-login', method: 'POST', data })

export const getMemberMe = () =>
  request({ url: '/member-auth/me', auth: true })

export const getMemberProfile = () =>
  request({ url: '/member/profile', auth: true })

export const updateMemberProfile = (data) =>
  request({ url: '/member/profile', method: 'PUT', data, auth: true })

export const uploadMemberAvatar = (filePath) =>
  new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${getBaseUrl()}/member/profile/avatar`,
      filePath,
      name: 'file',
      header: {
        Authorization: `Bearer ${getToken()}`,
      },
      success: (res) => {
        const data = JSON.parse(res.data || '{}')
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data)
          return
        }
        const detail = data?.detail || '头像上传失败'
        uni.showToast({ title: detail, icon: 'none' })
        reject({ statusCode: res.statusCode, detail, data })
      },
      fail: (err) => {
        uni.showToast({ title: '头像上传失败', icon: 'none' })
        reject(err)
      },
    })
  })

export const syncMemberAvatarFromUrl = (data) =>
  request({ url: '/member/profile/avatar-from-url', method: 'POST', data, auth: true })

export const redeemMemberBindingCode = (data) =>
  request({ url: '/member/binding-code/redeem', method: 'POST', data, auth: true })

export const getLatestMemberBindingRequest = () =>
  request({ url: '/member/binding-request/latest', auth: true })

export const createMemberBindingRequest = (data) =>
  request({ url: '/member/binding-request', method: 'POST', data, auth: true })

export const autoBindMember = (data) =>
  request({ url: '/member/auto-binding', method: 'POST', data, auth: true })

export const createMemberBindingCorrection = (data) =>
  request({ url: '/member/binding-correction', method: 'POST', data, auth: true })

export const getMemberDonations = (data) =>
  request({ url: '/member/donations', data, auth: true })

export const getMemberDonationSummary = () =>
  request({ url: '/member/donations/summary', auth: true })

export const getMemberCertificate = () =>
  request({ url: '/member/donations/certificate', auth: true })

export const getMemberInvoiceProfile = () =>
  request({ url: '/member/invoice-profile', auth: true })

export const updateMemberInvoiceProfile = (data) =>
  request({ url: '/member/invoice-profile', method: 'PUT', data, auth: true })

export const createMemberInvoiceRequest = (data) =>
  request({ url: '/member/invoice-requests', method: 'POST', data, auth: true })

export const getMemberDirectory = (data) =>
  request({ url: '/member/directory', data, auth: true })

export const getMemberFunds = () =>
  request({ url: '/member/funds', auth: true })

export const getMemberFundUsage = (fundId, data) =>
  request({ url: `/member/funds/${fundId}/usage`, data, auth: true })
