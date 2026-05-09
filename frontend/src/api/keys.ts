import request from './request'

export function searchKeys(data: any) {
  return request.post('/admin/keys/search', data)
}

export function generateKeys(data: any) {
  return request.post('/admin/keys/generate', data)
}

export function disableKey(id: number) {
  return request.put(`/admin/keys/${id}/disable`)
}
