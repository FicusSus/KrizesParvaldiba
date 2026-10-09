// Authentication types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: UserRole;
  status: UserStatus;
  is_verified: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
  is_admin: boolean;
  is_active: boolean;
  preferences?: Record<string, unknown>;
}

export enum UserRole {
  ADMIN = 'admin',
  ANALYST = 'analyst',
  USER = 'user',
}

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  role?: UserRole;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ErrorResponse {
  message: string;
  code?: string;
  details?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// Data Source types
export enum DataSourceType {
  CSV = 'csv',
  JSON = 'json',
  API = 'api',
  DATABASE = 'database',
  EXCEL = 'excel',
  PARQUET = 'parquet',
}

export interface DataSource {
  id: number;
  name: string;
  source_type: DataSourceType;
  connection_string: string;
  description: string | null;
  config: Record<string, unknown>;
  is_active: boolean;
  last_sync: string | null;
  created_at: string;
  updated_at: string;
  is_available: boolean;
}

// Dataset types
export enum DatasetType {
  RAW = 'raw',
  PROCESSED = 'processed',
  AGGREGATED = 'aggregated',
  FEATURES = 'features',
}

export enum DatasetStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  ARCHIVED = 'archived',
}

export interface Dataset {
  id: number;
  data_source_id: number | null;
  name: string;
  file_path: string;
  dataset_type: DatasetType;
  status: DatasetStatus;
  row_count: number | null;
  column_count: number | null;
  file_size: number | null;
  metadata: Record<string, unknown>;
  processing_time: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  is_processed: boolean;
  is_processing: boolean;
}

// Crisis types
export enum CrisisType {
  FINANCIAL = 'financial',
  ECONOMIC = 'economic',
  POLITICAL = 'political',
  SOCIAL = 'social',
  ENVIRONMENTAL = 'environmental',
  HEALTH = 'health',
  SECURITY = 'security',
  OTHER = 'other',
}

export enum CrisisSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum CrisisStatus {
  PREDICATED = 'predicted',
  CONFIRMED = 'confirmed',
  ONGOING = 'ongoing',
  RESOLVED = 'resolved',
  FALSE_ALARM = 'false_alarm',
}

export interface Crisis {
  id: number;
  dataset_id: number | null;
  crisis_type: CrisisType;
  severity: CrisisSeverity;
  status: CrisisStatus;
  title: string;
  description: string | null;
  location: string | null;
  start_date: string | null;
  end_date: string | null;
  confidence_score: number | null;
  impact_score: number | null;
  parameters: Record<string, unknown>;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  is_high_priority: boolean;
  risk_level: string;
}

// Warning types
export enum WarningType {
  EMAIL = 'email',
  SMS = 'sms',
  PUSH = 'push',
  WEBHOOK = 'webhook',
  IN_APP = 'in_app',
}

export enum WarningPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum WarningStatus {
  PENDING = 'pending',
  SENT = 'sent',
  DELIVERED = 'delivered',
  FAILED = 'failed',
  READ = 'read',
}

export interface Warning {
  id: number;
  user_id: number | null;
  crisis_id: number | null;
  warning_type: WarningType;
  priority: WarningPriority;
  status: WarningStatus;
  subject: string;
  message: string;
  recipient: string | null;
  is_read: boolean;
  send_attempts: number;
  last_attempt: string | null;
  error_message: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  is_sent: boolean;
  is_delivered: boolean;
  should_retry: boolean;
}

// Prediction types
export enum PredictionType {
  CLASSIFICATION = 'classification',
  REGRESSION = 'regression',
  TIME_SERIES = 'time_series',
  CLUSTERING = 'clustering',
  ANOMALY_DETECTION = 'anomaly_detection',
}

export enum PredictionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum ModelType {
  CRISIS_DETECTION = 'crisis_detection',
  SEVERITY_PREDICTION = 'severity_prediction',
  TIMELINE_PREDICTION = 'timeline_prediction',
  IMPACT_ASSESSMENT = 'impact_assessment',
}

export interface Prediction {
  id: number;
  dataset_id: number | null;
  model_type: ModelType;
  prediction_type: PredictionType;
  status: PredictionStatus;
  model_version: string;
  model_parameters: Record<string, unknown>;
  feature_columns: string[];
  target_column: string | null;
  predictions: Record<string, unknown>;
  metrics: Record<string, unknown>;
  training_time: number | null;
  prediction_time: number | null;
  error_message: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  is_successful: boolean;
  is_running: boolean;
  accuracy: number | null;
  f1_score: number | null;
}

// Notification types
export enum NotificationType {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  SUCCESS = 'success',
}

export enum NotificationChannel {
  EMAIL = 'email',
  SMS = 'sms',
  PUSH = 'push',
  WEBHOOK = 'webhook',
  IN_APP = 'in_app',
}

export interface Notification {
  id: number;
  user_id: number | null;
  notification_type: NotificationType;
  channel: NotificationChannel;
  title: string;
  message: string;
  is_read: boolean;
  is_archived: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  is_unread: boolean;
}

// Health check types
export interface HealthCheck {
  status: string;
  version: string;
  timestamp: string;
  checks?: Record<string, string>;
}

// Dashboard stats types
export interface DashboardStats {
  total_datasets: number;
  processed_datasets: number;
  pending_datasets: number;
  total_crises: number;
  active_crises: number;
  high_priority_crises: number;
  total_warnings: number;
  delivered_warnings: number;
  pending_warnings: number;
  model_accuracy: number | null;
  system_health: string;
}

// Filter and sort types
export interface QueryParams {
  page?: number;
  size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface FilterParams {
  dataset_type?: DatasetType;
  status?: DatasetStatus;
  crisis_type?: CrisisType;
  severity?: CrisisSeverity;
  priority?: WarningPriority;
  warning_type?: WarningType;
  warning_status?: WarningStatus;
  is_active?: boolean;
  is_read?: boolean;
  data_source_id?: number;
  user_id?: number;
  crisis_id?: number;
}

export interface TableColumn<T> {
  key: string;
  header: string;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

// UI State types
export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

export interface ModalState {
  isOpen: boolean;
  title: string;
  content: React.ReactNode;
  onConfirm?: () => void;
  onCancel?: () => void;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Form types
export interface SelectOption {
  value: string | number;
  label: string;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea' | 'date' | 'checkbox' | 'file';
  placeholder?: string;
  required?: boolean;
  options?: SelectOption[];
  defaultValue?: unknown;
  validation?: Record<string, unknown>;
  helpText?: string;
}

// Chart types
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
}

export interface CrisisTrendData {
  date: string;
  total: number;
  byType: Record<CrisisType, number>;
  bySeverity: Record<CrisisSeverity, number>;
}

export interface DataProcessingStats {
  total_size: number;
  processed_size: number;
  row_count: number;
  column_count: number;
  processing_time: number;
  memory_usage: number;
}

// User preferences types
export interface UserPreferences {
  theme?: 'light' | 'dark' | 'system';
  language?: string;
  timezone?: string;
  receive_notifications?: boolean;
  notification_channels?: WarningType[];
  crisis_types?: Record<CrisisType, boolean>;
  severity_levels?: Record<CrisisSeverity, boolean>;
  dashboard_layout?: string;
  date_format?: string;
  number_format?: string;
  currency?: string;
  phone_number?: string;
  push_token?: string;
  webhook_url?: string;
}

// Application state types
export interface AppState {
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export interface CrisisFilterState {
  crisis_type: CrisisType | '';
  severity: CrisisSeverity | '';
  status: CrisisStatus | '';
  dateRange: [Date | null, Date | null];
  search: string;
}

export interface DataFilterState {
  dataset_type: DatasetType | '';
  status: DatasetStatus | '';
  data_source_id: number | '';
  dateRange: [Date | null, Date | null];
  search: string;
}

export interface WarningFilterState {
  warning_type: WarningType | '';
  priority: WarningPriority | '';
  status: WarningStatus | '';
  is_read: boolean | '';
  dateRange: [Date | null, Date | null];
  search: string;
}

// Export all types
export type {
  SelectOption as SelectOption,
  FormField as FormField,
  ChartData as ChartData,
  ChartDataset as ChartDataset,
  ToastMessage as ToastMessage,
  ModalState as ModalState,
  QueryParams as QueryParams,
  FilterParams as FilterParams,
  TableColumn as TableColumn,
  UserPreferences as UserPreferences,
  CrisisTrendData as CrisisTrendData,
  DataProcessingStats as DataProcessingStats,
  AppState as AppState,
  CrisisFilterState as CrisisFilterState,
  DataFilterState as DataFilterState,
  WarningFilterState as WarningFilterState,
}