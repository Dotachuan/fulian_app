import request from '@/utils/request'

export const getFundListApi = (params) =>
  request.get('/funds', { params })

export const createFundApi = (data) =>
  request.post('/funds', data)

export const updateFundApi = (id, data) =>
  request.put(`/funds/${id}`, data)

export const deleteFundApi = (id) =>
  request.delete(`/funds/${id}`)

export const getFundUsageListApi = (params) =>
  request.get('/fund-usage-records', { params })

export const createFundUsageApi = (data) =>
  request.post('/fund-usage-records', data)

export const updateFundUsageApi = (id, data) =>
  request.put(`/fund-usage-records/${id}`, data)

export const deleteFundUsageApi = (id) =>
  request.delete(`/fund-usage-records/${id}`)

