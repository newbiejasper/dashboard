// ===== Types =====

export interface User {
  id: number
  username: string
  email?: string
  display_name?: string
  avatar?: string
  is_active: boolean
  created_at?: string
}

export interface DataSource {
  id: number
  name: string
  description?: string
  source_type: string
  connection_mode: string
  config?: any
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface DataSourceType {
  key: string
  name: string
  category: string
  icon: string
}

export interface Dataset {
  id: number
  name: string
  description?: string
  dataset_type: string
  datasource_id?: number
  source_table?: string
  sql_query?: string
  fields_config?: FieldConfig[]
  dimensions_config?: DimensionConfig[]
  measures_config?: MeasureConfig[]
  drill_down_config?: DrillDownConfig[]
  filter_fields?: FilterFieldConfig[]
  transformations?: any
  sync_config?: any
  data_sample?: any[]
  row_count: number
  is_synced: boolean
  last_sync_at?: string
  created_at?: string
  updated_at?: string
}

export interface FieldConfig {
  name: string
  type: 'string' | 'number' | 'date' | 'boolean'
  alias?: string
  original_type?: string
}

export interface DimensionConfig {
  name: string
  type: string
  alias?: string
  sub_dimensions?: SubDimensionConfig[]
}

export interface SubDimensionConfig {
  name: string
  alias?: string
}

export interface MeasureConfig {
  name: string
  type: string
  alias?: string
  aggregation: 'SUM' | 'AVG' | 'COUNT' | 'MAX' | 'MIN' | 'COUNT_DISTINCT'
}

export interface DrillDownConfig {
  name: string
  alias?: string
  levels: string[]
}

export interface FilterFieldConfig {
  name: string
  type: 'dropdown' | 'date_picker' | 'text_input' | 'slider' | 'date_range'
  alias?: string
  field: string
  options?: any[]
}

export interface Chart {
  id: number
  name?: string
  chart_type: string
  dataset_id: number
  dimensions: string[]
  measures: string[]
  config?: any
  color_schema?: string[]
  sort_config?: any
  filter_config?: FilterConfig[]
  drill_down?: any
  created_at?: string
  updated_at?: string
}

export interface FilterConfig {
  field: string
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'between'
  value: any
  value2?: any
}

export interface Dashboard {
  id: number
  name: string
  description?: string
  dashboard_type: 'dashboard' | 'screen'
  layout?: any
  background_config?: BackgroundConfig
  style_config?: any
  filter_config?: DashboardFilter[]
  width: number
  height: number
  is_published: boolean
  thumbnail?: string
  share_token?: string
  embed_token?: string
  visit_count: number
  created_at?: string
  updated_at?: string
}

export interface BackgroundConfig {
  color?: string
  image?: string
  opacity?: number
  border?: string
}

export interface DashboardFilter {
  id?: number
  dashboard_id?: number
  filter_type: 'dropdown' | 'date_picker' | 'text_input' | 'slider'
  field_name: string
  title: string
  position?: { x: number; y: number; w: number; h: number }
  config?: any
  linked_views?: number[]
}

export interface DashboardView {
  id: number
  dashboard_id: number
  title?: string
  chart_id?: number
  position: ViewPosition
  style?: any
  interactions?: ViewInteractions
  chart?: Chart
}

export interface ViewPosition {
  x: number
  y: number
  w: number
  h: number
}

export interface ViewInteractions {
  linkage?: boolean
  drill_down_hierarchy?: string[]
  jump_to?: { dashboard_id: number; params_field: string }
}

export interface StatsResponse {
  dashboard_count: number
  screen_count: number
  datasource_count: number
  dataset_count: number
}

// Chart types enum
export type ChartType =
  | 'bar' | 'line' | 'pie' | 'doughnut' | 'horizontal_bar' | 'radar'
  | 'scatter' | 'area' | 'gauge' | 'progress'
  | 'funnel' | 'sankey' | 'heatmap' | 'tree' | 'sunburst'
  | 'liquid' | 'wordcloud' | 'map_china' | 'map_world' | 'map_province'

export interface ChartTypeOption {
  key: ChartType
  name: string
  icon: string
  category: 'basic' | 'advanced'
}

// Navigation
export interface MenuItem {
  key: string
  label: string
  icon: string
  route?: string
  children?: MenuItem[]
}
