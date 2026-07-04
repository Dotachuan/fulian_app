import request from '@/utils/request'

export const loginApi = (data) =>
  request.post('/auth/login', data)

export const logoutApi = () =>
  request.post('/auth/logout')

export const getUserListApi = (params) =>
  request.get('/users', { params })

export const createUserApi = (data) =>
  request.post('/users', data)

export const updateUserApi = (id, data) =>
  request.put(`/users/${id}`, data)

export const deleteUserApi = (id) =>
  request.delete(`/users/${id}`)
