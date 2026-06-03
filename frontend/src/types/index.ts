/** Shared TypeScript types for GeneralDataPlatform frontend */

export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface DataSource {
  id: string;
  name: string;
  description?: string;
  group?: string;
  request_method: string;
  request_url: string;
  auth_type: string;
  headers_config?: Record<string, string>;
  query_config?: Record<string, string>;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface DataSourceFormValues {
  name: string;
  description?: string;
  group?: string;
  request_method: string;
  request_url: string;
  auth_type: string;
  auth_config?: {
    token?: string;
    key_name?: string;
    key_value?: string;
    key_location?: string;
  };
  headers_config?: Record<string, string>;
  query_config?: Record<string, string>;
  body_config?: string;
  timeout_seconds?: number;
  retry_count?: number;
}

export interface SyncJob {
  id: string;
  data_source_id: string;
  name: string;
  schedule_type: string;
  schedule_config: Record<string, any>;
  sync_mode: string;
  write_mode: string;
  is_enabled: boolean;
  last_run_at?: string;
  next_run_at?: string;
}

export interface SyncJobRun {
  id: string;
  sync_job_id: string;
  status: string;
  started_at: string;
  finished_at?: string;
  fetched_count: number;
  inserted_count: number;
  failed_count: number;
  error_message?: string;
}

export interface Dashboard {
  id: string;
  name: string;
  description?: string;
  status: string;
  visibility: string;
  created_at?: string;
  updated_at?: string;
}

export interface DashboardWidget {
  id: string;
  dashboard_id: string;
  widget_type: string;
  title: string;
  component_source: string;
  component_key?: string;
  component_version?: string;
  query_config?: Record<string, any>;
  props_config?: Record<string, any>;
  position_config?: Record<string, any>;
}

export interface QueryRequest {
  table: string;
  dimensions?: string[];
  metrics?: Array<{
    field: string;
    aggregation: string;
    alias?: string;
  }>;
  filters?: Array<{
    field: string;
    operator: string;
    value: any;
  }>;
  sort?: Array<{
    field: string;
    direction: string;
  }>;
  limit?: number;
  offset?: number;
}

export interface QueryResult {
  columns: string[];
  rows: any[][];
  total: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
