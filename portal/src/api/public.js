import request from '@/utils/request'

export const queryDonationsApi = (params) =>
  request.get('/public/donations/query', { params })

export const getDonationSummaryApi = (params) =>
  request.get('/public/donations/summary', { params })

export const getPublicFundsApi = () =>
  request.get('/public/funds')

export const getPublicFundUsageApi = (fundId, params) =>
  request.get(`/public/funds/${fundId}/usage`, { params })

export const createInvoiceRequestApi = (data) =>
  request.post('/public/invoice-requests', data)

export const getPublicNewsApi = (params) =>
  request.get('/public/news', { params })
