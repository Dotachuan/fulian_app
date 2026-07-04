import request from '@/utils/request'

export const getProjectLinkListApi = (params) => request.get('/project-links', { params })

export const createProjectLinkApi = (data) => request.post('/project-links', data)

export const updateProjectLinkApi = (id, data) => request.put(`/project-links/${id}`, data)

export const deleteProjectLinkApi = (id) => request.delete(`/project-links/${id}`)
