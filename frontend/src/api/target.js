import request from '@/utils/request'

export const getTargetListApi = (params) =>
  request.get('/targets', { params })

export const createTargetApi = (data) =>
  request.post('/targets', data)

export const updateTargetApi = (id, data) =>
  request.put(`/targets/${id}`, data)

export const deleteTargetApi = (id) =>
  request.delete(`/targets/${id}`)
