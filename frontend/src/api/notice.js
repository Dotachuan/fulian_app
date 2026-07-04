import request from '@/utils/request'

export const getNoticeListApi = (params) =>
  request.get('/notices', { params })

export const createNoticeApi = (data) =>
  request.post('/notices', data)

export const updateNoticeApi = (id, data) =>
  request.put(`/notices/${id}`, data)

export const deleteNoticeApi = (id) =>
  request.delete(`/notices/${id}`)
