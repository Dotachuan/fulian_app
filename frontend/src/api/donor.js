import request from '@/utils/request'

export const getDonorListApi = (params) =>
  request.get('/donors', { params })

export const getDonorDetailApi = (id) =>
  request.get(`/donors/${id}`)

export const createDonorApi = (data) =>
  request.post('/donors', data)

export const updateDonorApi = (id, data) =>
  request.put(`/donors/${id}`, data)

export const deleteDonorApi = (id) =>
  request.delete(`/donors/${id}`)

export const batchGenerateDonorBindingCodesApi = (data) =>
  request.post('/donors/binding-codes/batch-generate', data)

export const exportDonorBindingCodesApi = (params) =>
  request.get('/donors/binding-codes/export', {
    params,
    responseType: 'blob',
  })
