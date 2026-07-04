import request from '@/utils/request'

export const getDonationListApi = (params) =>
  request.get('/donations', { params })

export const getDonationDetailApi = (id) =>
  request.get(`/donations/${id}`)

export const createDonationApi = (data) =>
  request.post('/donations', data)

export const updateDonationApi = (id, data) =>
  request.put(`/donations/${id}`, data)

export const deleteDonationApi = (id) =>
  request.delete(`/donations/${id}`)

export const exportDonationApi = (params) =>
  request.get('/donations/export', {
    params,
    responseType: 'blob',
  })
