/**
 * Table Components
 * Additional table-related components: StatusBadge, SeverityBadge, ActionButtons, etc.
 */

import React from 'react';
import { Eye, Edit, Trash2, AlertTriangle, CheckCircle, XCircle, Info, Clock } from 'lucide-react';

// Severity levels for crisis
const SEVERITY_COLORS: Record<string, { bg: string; text: string }> = {
  low: { bg: 'bg-success-100', text: 'text-success-800' },
  medium: { bg: 'bg-warning-100', text: 'text-warning-800' },
  high: { bg: 'bg-danger-100', text: 'text-danger-800' },
  critical: { bg: 'bg-danger-200', text: 'text-danger-900' },
  LOW: { bg: 'bg-success-100', text: 'text-success-800' },
  MEDIUM: { bg: 'bg-warning-100', text: 'text-warning-800' },
  HIGH: { bg: 'bg-danger-100', text: 'text-danger-800' },
  CRITICAL: { bg: 'bg-danger-200', text: 'text-danger-900' },
};

// Status types
const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  active: { bg: 'bg-success-100', text: 'text-success-800' },
  pending: { bg: 'bg-warning-100', text: 'text-warning-800' },
  completed: { bg: 'bg-primary-100', text: 'text-primary-800' },
  failed: { bg: 'bg-danger-100', text: 'text-danger-800' },
  resolved: { bg: 'bg-success-100', text: 'text-success-800' },
  ongoing: { bg: 'bg-warning-100', text: 'text-warning-800' },
  ACTIVE: { bg: 'bg-success-100', text: 'text-success-800' },
  PENDING: { bg: 'bg-warning-100', text: 'text-warning-800' },
  COMPLETED: { bg: 'bg-primary-100', text: 'text-primary-800' },
  FAILED: { bg: 'bg-danger-100', text: 'text-danger-800' },
  RESOLVED: { bg: 'bg-success-100', text: 'text-success-800' },
  ONGOING: { bg: 'bg-warning-100', text: 'text-warning-800' },
};

// Warning priority
const PRIORITY_COLORS: Record<string, { bg: string; text: string }> = {
  low: { bg: 'bg-gray-100', text: 'text-gray-800' },
  medium: { bg: 'bg-warning-100', text: 'text-warning-800' },
  high: { bg: 'bg-danger-100', text: 'text-danger-800' },
  urgent: { bg: 'bg-danger-200', text: 'text-danger-900' },
  LOW: { bg: 'bg-gray-100', text: 'text-gray-800' },
  MEDIUM: { bg: 'bg-warning-100', text: 'text-warning-800' },
  HIGH: { bg: 'bg-danger-100', text: 'text-danger-800' },
  URGENT: { bg: 'bg-danger-200', text: 'text-danger-900' },
};

// Crisis type icons
const CRISIS_ICONS: Record<string, React.ReactNode> = {
  financial: <span className="text-green-600">💰</span>,
  economic: <span className="text-blue-600">📈</span>,
  political: <span className="text-red-600">🏛️</span>,
  social: <span className="text-orange-600">👥</span>,
  environmental: <span className="text-green-600">🌍</span>,
  health: <span className="text-purple-600">🏥</span>,
  security: <span className="text-yellow-600">🔒</span>,
  FINANCIAL: <span className="text-green-600">💰</span>,
  ECONOMIC: <span className="text-blue-600">📈</span>,
  POLITICAL: <span className="text-red-600">🏛️</span>,
  SOCIAL: <span className="text-orange-600">👥</span>,
  ENVIRONMENTAL: <span className="text-green-600">🌍</span>,
  HEALTH: <span className="text-purple-600">🏥</span>,
  SECURITY: <span className="text-yellow-600">🔒</span>,
  other: <span className="text-gray-600">⚠️</span>,
  OTHER: <span className="text-gray-600">⚠️</span>,
};

// Notification type icons
const NOTIFICATION_ICONS: Record<string, React.ReactNode> = {
  email: <span className="text-blue-600">📧</span>,
  sms: <span className="text-green-600">📱</span>,
  push: <span className="text-purple-600">🔔</span>,
  webhook: <span className="text-orange-600">🔗</span>,
  in_app: <span className="text-indigo-600">📬</span>,
  EMAIL: <span className="text-blue-600">📧</span>,
  SMS: <span className="text-green-600">📱</span>,
  PUSH: <span className="text-purple-600">🔔</span>,
  WEBHOOK: <span className="text-orange-600">🔗</span>,
  IN_APP: <span className="text-indigo-600">📬</span>,
};

// Notification type labels
const NOTIFICATION_LABELS: Record<string, string> = {
  info: 'Info',
  warning: 'Warning',
  error: 'Error',
  success: 'Success',
  INFO: 'Info',
  WARNING: 'Warning',
  ERROR: 'Error',
  SUCCESS: 'Success',
};

// Status icons
const STATUS_ICONS: Record<string, React.ReactNode> = {
  active: <CheckCircle className="w-4 h-4 text-success-600" />,
  pending: <Clock className="w-4 h-4 text-warning-600" />,
  completed: <CheckCircle className="w-4 h-4 text-primary-600" />,
  failed: <XCircle className="w-4 h-4 text-danger-600" />,
  resolved: <CheckCircle className="w-4 h-4 text-success-600" />,
  ongoing: <AlertTriangle className="w-4 h-4 text-warning-600" />,
  ACTIVE: <CheckCircle className="w-4 h-4 text-success-600" />,
  PENDING: <Clock className="w-4 h-4 text-warning-600" />,
  COMPLETED: <CheckCircle className="w-4 h-4 text-primary-600" />,
  FAILED: <XCircle className="w-4 h-4 text-danger-600" />,
  RESOLVED: <CheckCircle className="w-4 h-4 text-success-600" />,
  ONGOING: <AlertTriangle className="w-4 h-4 text-warning-600" />,
};

interface BadgeProps {
  value: string;
  type?: 'severity' | 'status' | 'priority' | 'crisis' | 'notification';
  className?: string;
}

export function Badge({ value, type = 'status', className = '' }: BadgeProps) {
  const getColors = () => {
    if (type === 'severity') return SEVERITY_COLORS[value] || SEVERITY_COLORS.low;
    if (type === 'status') return STATUS_COLORS[value] || STATUS_COLORS.active;
    if (type === 'priority') return PRIORITY_COLORS[value] || PRIORITY_COLORS.medium;
    if (type === 'crisis') return SEVERITY_COLORS[value] || SEVERITY_COLORS.medium;
    return STATUS_COLORS[value] || STATUS_COLORS.active;
  };

  const colors = getColors();
  const label = type === 'notification' ? NOTIFICATION_LABELS[value] || value : value;

  return (
    <span
      className={`badge ${colors.bg} ${colors.text} ${className}`}
      title={label}
    >
      {type === 'crisis' && CRISIS_ICONS[value]}
      {type === 'notification' && NOTIFICATION_ICONS[value]}
      {' '}
      {label}
    </span>
  );
}

export function SeverityBadge({ value }: { value: string }) {
  const colors = SEVERITY_COLORS[value] || SEVERITY_COLORS.low;
  const label = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();

  return (
    <span className={`badge ${colors.bg} ${colors.text}`}>
      {CRISIS_ICONS[value]}
      {' '}
      {label}
    </span>
  );
}

export function StatusBadge({ value }: { value: string }) {
  const colors = STATUS_COLORS[value] || STATUS_COLORS.active;
  const label = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();

  return (
    <span className={`badge ${colors.bg} ${colors.text}`}>
      {STATUS_ICONS[value]}
      {' '}
      {label}
    </span>
  );
}

export function PriorityBadge({ value }: { value: string }) {
  const colors = PRIORITY_COLORS[value] || PRIORITY_COLORS.medium;
  const label = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();

  return (
    <span className={`badge ${colors.bg} ${colors.text}`}>
      {label}
    </span>
  );
}

export function CrisisTypeBadge({ value }: { value: string }) {
  const colors = SEVERITY_COLORS[value] || SEVERITY_COLORS.medium;

  return (
    <span className={`badge ${colors.bg} ${colors.text}`}>
      {CRISIS_ICONS[value]}
      {' '}
      {value}
    </span>
  );
}

export function NotificationTypeBadge({ value }: { value: string }) {
  const label = NOTIFICATION_LABELS[value] || value;

  return (
    <span className="badge bg-primary-100 text-primary-800">
      {NOTIFICATION_ICONS[value]}
      {' '}
      {label}
    </span>
  );
}

export function ProgressBar({ value, max = 100 }: { value: number; max?: number }) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className="progress-bar">
      <div
        className="progress-bar-fill"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}

export function ActionButtons({
  onView,
  onEdit,
  onDelete,
  showView = true,
  showEdit = true,
  showDelete = true,
}: {
  onView?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  showView?: boolean;
  showEdit?: boolean;
  showDelete?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      {showView && onView && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onView();
          }}
          className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
          title="View"
        >
          <Eye className="w-5 h-5" />
        </button>
      )}
      {showEdit && onEdit && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onEdit();
          }}
          className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
          title="Edit"
        >
          <Edit className="w-5 h-5" />
        </button>
      )}
      {showDelete && onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="p-2 text-danger-600 hover:bg-danger-50 rounded-lg transition-colors"
          title="Delete"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon || <Info className="w-16 h-16" />}</div>
      <h3 className="empty-state-title">{title}</h3>
      {description && <p className="empty-state-text">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

export function LoadingState({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="loading-state">
      <div className="loading-spinner" />
      <p className="loading-text">{message}</p>
    </div>
  );
}

export function ErrorState({
  title = 'Error',
  message,
  onRetry,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="error-state">
      <div className="error-state-icon">
        <XCircle className="w-16 h-16" />
      </div>
      <h3 className="error-state-title">{title}</h3>
      {message && <p className="error-state-text">{message}</p>}
      {onRetry && (
        <div className="error-state-actions">
          <button onClick={onRetry} className="btn btn-primary">
            Retry
          </button>
        </div>
      )}
    </div>
  );
}

export function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm',
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  message: React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'primary' | 'warning';
}) {
  if (!isOpen) return null;

  const getButtonClass = () => {
    if (variant === 'danger') return 'btn btn-danger';
    if (variant === 'warning') return 'btn btn-warning';
    return 'btn btn-primary';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
        <h3 className="text-xl font-semibold mb-4">{title}</h3>
        <div className="mb-6">{message}</div>
        <div className="flex justify-end gap-3">
          <button onClick={onClose} className="btn btn-secondary">
            {cancelText}
          </button>
          <button onClick={onConfirm} className={getButtonClass()}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

export function Tooltip({ children, content }: { children: React.ReactNode; content: string }) {
  return (
    <div className="relative group">
      {children}
      <div className="absolute z-10 invisible group-hover:visible bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap">
        {content}
      </div>
    </div>
  );
}

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}: {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}) {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className={`bg-white rounded-xl shadow-xl w-full ${sizeClasses[size]} max-h-[90vh] overflow-y-auto`}
        onClick={(e) => e.stopPropagation()}
      >
        {title && (
          <div className="p-6 pb-0 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-xl font-semibold">{title}</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        )}
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}

export function Alert({
  type = 'info',
  message,
  onClose,
  title,
}: {
  type?: 'info' | 'success' | 'warning' | 'danger';
  message: React.ReactNode;
  onClose?: () => void;
  title?: string;
}) {
  const typeClasses = {
    info: 'alert-info',
    success: 'alert-success',
    warning: 'alert-warning',
    danger: 'alert-danger',
  };

  const iconClasses = {
    info: 'text-primary-600',
    success: 'text-success-600',
    warning: 'text-warning-600',
    danger: 'text-danger-600',
  };

  const icons = {
    info: <Info className="w-5 h-5" />,
    success: <CheckCircle className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
    danger: <XCircle className="w-5 h-5" />,
  };

  return (
    <div className={`alert ${typeClasses[type]} p-4 rounded-lg flex items-center gap-3`}>
      <div className={iconClasses[type]}>{icons[type]}</div>
      <div className="flex-1">
        {title && <h4 className="font-semibold mb-1">{title}</h4>}
        <div>{message}</div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-black hover:bg-opacity-10"
        >
          <XCircle className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

export function StatsCard({
  title,
  value,
  icon,
  change,
  trend = 'up',
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  change?: string | number;
  trend?: 'up' | 'down' | 'neutral';
}) {
  const trendColor = {
    up: 'text-success-600',
    down: 'text-danger-600',
    neutral: 'text-gray-600',
  };

  const trendIcon = {
    up: '↑',
    down: '↓',
    neutral: '→',
  };

  return (
    <div className="card">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`text-sm ${trendColor[trend]} flex items-center gap-1`}>
              {trendIcon[trend]}
              {change}
            </p>
          )}
        </div>
        <div className="p-2 bg-primary-50 rounded-lg">{icon}</div>
      </div>
    </div>
  );
}
