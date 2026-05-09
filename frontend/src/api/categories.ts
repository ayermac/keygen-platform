import request from './request'

export function getCategories() {
  return request.get('/admin/categories')
}

export function createCategory(data: any) {
  return request.post('/admin/categories', data)
}

export function updateCategory(id: number, data: any) {
  return request.put(`/admin/categories/${id}`, data)
}

export function deleteCategory(id: number) {
  return request.delete(`/admin/categories/${id}`)
}
