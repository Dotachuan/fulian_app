import request from '@/utils/request'

export const uploadImageApi = (folder, file) => {
  const formData = new FormData()
  formData.append('folder', folder)
  formData.append('file', file)
  return request.post('/uploads/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
