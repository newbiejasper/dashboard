import api from './index'
import type {
  User, DataSource, DataSourceType, Dataset, Chart, Dashboard,
  DashboardView, DashboardFilter, StatsResponse, ChartTypeOption
} from '@/types'

// ===== Auth =====
export const authAPI = {
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  register: (data: { username: string; password: string; email?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get<User>('/auth/me'),
}

// ===== DataSources =====
export const datasourceAPI = {
  list: (sourceType?: string) =>
    api.get<DataSource[]>('/datasources/', { params: { source_type: sourceType } }),
  types: () => api.get<{ types: DataSourceType[]; connection_modes: any[] }>('/datasources/types'),
  create: (data: Partial<DataSource>) =>
    api.post<DataSource>('/datasources/', data),
  get: (id: number) => api.get<DataSource>(`/datasources/${id}`),
  update: (id: number, data: Partial<DataSource>) =>
    api.put<DataSource>(`/datasources/${id}`, data),
  delete: (id: number) => api.delete(`/datasources/${id}`),
  test: (id: number) => api.post(`/datasources/${id}/test`),
}

// ===== Datasets =====
export const datasetAPI = {
  list: (params?: { dataset_type?: string; datasource_id?: number }) =>
    api.get<Dataset[]>('/datasets/', { params }),
  create: (data: Partial<Dataset>) =>
    api.post<Dataset>('/datasets/', data),
  upload: (file: File, name?: string) => {
    const form = new FormData()
    form.append('file', file)
    if (name) form.append('name', name)
    return api.post<Dataset>('/datasets/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  get: (id: number) => api.get<Dataset>(`/datasets/${id}`),
  update: (id: number, data: Partial<Dataset>) =>
    api.put<Dataset>(`/datasets/${id}`, data),
  delete: (id: number) => api.delete(`/datasets/${id}`),
  query: (id: number, params: any) =>
    api.post(`/datasets/${id}/query`, params),
}

// ===== Dashboards =====
export const dashboardAPI = {
  list: (dashboardType?: string) =>
    api.get<Dashboard[]>('/dashboards/', { params: { dashboard_type: dashboardType } }),
  recent: (limit = 10) =>
    api.get<Dashboard[]>('/dashboards/recent', { params: { limit } }),
  stats: () => api.get<StatsResponse>('/dashboards/stats'),
  create: (data: Partial<Dashboard>) =>
    api.post<Dashboard>('/dashboards/', data),
  get: (id: number) => api.get<Dashboard>(`/dashboards/${id}`),
  update: (id: number, data: Partial<Dashboard>) =>
    api.put<Dashboard>(`/dashboards/${id}`, data),
  delete: (id: number) => api.delete(`/dashboards/${id}`),
  // Views
  views: (dashboardId: number) =>
    api.get<DashboardView[]>(`/dashboards/${dashboardId}/views`),
  addView: (dashboardId: number, data: Partial<DashboardView>) =>
    api.post<DashboardView>(`/dashboards/${dashboardId}/views`, data),
  updateView: (dashboardId: number, viewId: number, data: Partial<DashboardView>) =>
    api.put<DashboardView>(`/dashboards/${dashboardId}/views/${viewId}`, data),
  removeView: (dashboardId: number, viewId: number) =>
    api.delete(`/dashboards/${dashboardId}/views/${viewId}`),
  // Share
  share: (dashboardId: number, password?: string) =>
    api.post(`/dashboards/${dashboardId}/share`, { password }),
  // Charts
  createChart: (data: Partial<Chart>) =>
    api.post<Chart>('/dashboards/charts', data),
  getChart: (id: number) => api.get<Chart>(`/dashboards/charts/${id}`),
  updateChart: (id: number, data: Partial<Chart>) =>
    api.put<Chart>(`/dashboards/charts/${id}`, data),
  deleteChart: (id: number) => api.delete(`/dashboards/charts/${id}`),
  // Templates
  templates: (category?: string) =>
    api.get<Dashboard[]>('/dashboards/templates', { params: { category } }),
  useTemplate: (templateId: number) =>
    api.post<Dashboard>(`/dashboards/templates/${templateId}/use`),
}

export default api
