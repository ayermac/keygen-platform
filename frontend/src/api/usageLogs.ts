import request from './request'

export function searchUsageLogs(data: any) {
  return request.post('/admin/usage-logs/search', data)
}
