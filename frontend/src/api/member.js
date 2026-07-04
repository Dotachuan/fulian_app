import request from '@/utils/request'

export const getMemberListApi = (params) =>
  request.get('/members', { params })

export const updateMemberApi = (id, data) =>
  request.put(`/members/${id}`, data)

export const getMemberDonorOptionsApi = (params) =>
  request.get('/members/donor-options', { params })

export const getMemberBindingCodeApi = (id) =>
  request.get(`/members/${id}/binding-code`)

export const createMemberBindingCodeApi = (id, data) =>
  request.post(`/members/${id}/binding-code`, data)

export const getMemberSuggestionListApi = (params) =>
  request.get('/members/suggestions', { params })

export const updateMemberSuggestionApi = (id, data) =>
  request.put(`/members/suggestions/${id}`, data)

export const exportMemberSuggestionApi = (params) =>
  request.get('/members/suggestions/export', {
    params,
    responseType: 'blob',
  })
