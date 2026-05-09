import request from './request'

export function getAuditLogs(params: any) {
  return request.get('/admin/audit-logs', { params })
}
