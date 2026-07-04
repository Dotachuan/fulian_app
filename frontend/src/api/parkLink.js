import request from '@/utils/request'

export const getParkLinkListApi = (params) => request.get('/park-links', { params })

export const createParkLinkApi = (data) => request.post('/park-links', data)

export const updateParkLinkApi = (id, data) => request.put(`/park-links/${id}`, data)

export const deleteParkLinkApi = (id) => request.delete(`/park-links/${id}`)
