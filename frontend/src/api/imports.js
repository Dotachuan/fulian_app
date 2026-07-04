import request from '@/utils/request'

export const previewDonationImportApi = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/imports/donations/preview', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const commitDonationImportApi = (data) =>
  request.post('/imports/donations/commit', data)

