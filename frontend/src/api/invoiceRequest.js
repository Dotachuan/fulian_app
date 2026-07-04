import request from '@/utils/request'

export const getInvoiceRequestListApi = (params) =>
  request.get('/invoice-requests', { params })

export const updateInvoiceRequestApi = (id, data) =>
  request.put(`/invoice-requests/${id}`, data)

export const batchUpdateInvoiceRequestApi = (data) =>
  request.post('/invoice-requests/batch', data)

export const exportInvoiceRequestApi = (params) =>
  request.get('/invoice-requests/export', {
    params,
    responseType: 'blob',
  })
