export function formatDateTime(iso: string | null): string {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('zh-CN')
}

export function statusLabel(status: string): string {
  const map: Record<string, string> = {
    unused: '未兑换',
    activated: '已兑换',
    expired: '已过期',
    disabled: '已禁用',
  }
  return map[status] || status
}

export function statusType(status: string): string {
  const map: Record<string, string> = {
    unused: 'info',
    activated: 'success',
    expired: 'warning',
    disabled: 'danger',
  }
  return map[status] || 'info'
}
