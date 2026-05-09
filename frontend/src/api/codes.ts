import request from './request'

export function searchCodes(data: any) {
  return request.post('/admin/codes/search', data)
}

export function generateCodes(data: any) {
  return request.post('/admin/codes/generate', data)
}

export function disableCode(id: number) {
  return request.put(`/admin/codes/${id}/disable`)
}
