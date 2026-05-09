import request from './request'

export function getStatsOverview() {
  return request.get('/admin/stats')
}

export function getProductStats(productId: number) {
  return request.get(`/admin/stats/product/${productId}`)
}
