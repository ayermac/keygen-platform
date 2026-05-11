import request from './request'

export function searchBatches(data: any) {
  return request.post('/admin/batches/search', data)
}

export function getBatchDetail(batchId: string) {
  return request.get(`/admin/batches/${batchId}`)
}

export function disableBatch(batchId: string) {
  return request.put(`/admin/batches/${batchId}/disable`)
}
