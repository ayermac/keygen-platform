import request from './request'

export function getProducts() {
  return request.get('/admin/products')
}

export function createProduct(data: any) {
  return request.post('/admin/products', data)
}

export function updateProduct(id: number, data: any) {
  return request.put(`/admin/products/${id}`, data)
}

export function deleteProduct(id: number) {
  return request.delete(`/admin/products/${id}`)
}
