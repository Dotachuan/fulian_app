import request from '@/utils/request'

export const getSiteContentListApi = () =>
  request.get('/site-contents')

export const updateSiteContentApi = (key, data) =>
  request.put(`/site-contents/${key}`, data)
