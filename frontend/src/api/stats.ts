import request from './request'

export function getStatsOverview() {
  return request.get('/admin/stats')
}

export function getCategoryStats(categoryId: number) {
  return request.get(`/admin/stats/category/${categoryId}`)
}
