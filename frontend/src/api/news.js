import request from '@/utils/request'

export const getNewsListApi = (params) =>
  request.get('/news', { params })

export const createNewsApi = (data) =>
  request.post('/news', data)

export const updateNewsApi = (id, data) =>
  request.put(`/news/${id}`, data)

export const deleteNewsApi = (id) =>
  request.delete(`/news/${id}`)

