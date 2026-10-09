"""
Warning List Page

Page for viewing and managing crisis warnings and notifications.
"""

import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, AlertTriangle, CheckCircle, XCircle, Eye, Trash2, Search, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import DataTable from '../../components/Common/DataTable';
import {
  Badge,
  ActionButtons,
  EmptyState,
  LoadingState,
  ConfirmationDialog,
  StatsCard,
  PriorityBadge,
  NotificationTypeBadge,
} from '../../components/Common/TableComponents';
import { warningService } from '../../services/warningService';
import { Warning } from '../../types';

const WARNING_TYPES = ['EMAIL', 'SMS', 'PUSH', 'WEBHOOK', 'IN_APP'];
const WARNING_PRIORITIES = ['URGENT', 'HIGH', 'MEDIUM', 'LOW'];
const WARNING_STATUSES = ['PENDING', 'SENT', 'DELIVERED', 'FAILED', 'READ', 'ARCHIVED'];

const STATUS_COLORS: Record<string, string> = {
  PENDING: 'bg-warning-100 text-warning-800',
  SENT: 'bg-primary-100 text-primary-800',
  DELIVERED: 'bg-success-100 text-success-800',
  FAILED: 'bg-danger-100 text-danger-800',
  READ: 'bg-gray-100 text-gray-800',
  ARCHIVED: 'bg-gray-200 text-gray-600',
};

export const WarningListPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedWarning, setSelectedWarning] = useState<Warning | null>(null);

  // Fetch warnings
  const {
    data: warnings = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['warnings'],
    queryFn: warningService.getWarnings,
  });

  // Delete warning mutation
  const deleteMutation = useMutation({
    mutationFn: warningService.deleteWarning,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warnings'] });
      setIsDeleteModalOpen(false);
      setSelectedWarning(null);
    },
    onError: (err) => {
      console.error('Delete failed:', err);
    },
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: warningService.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warnings'] });
    },
    onError: (err) => {
      console.error('Mark as read failed:', err);
    },
  });

  // Calculate stats
  const stats = {
    total: warnings.length,
    unread: warnings.filter((w) => !w.isRead).length,
    urgent: warnings.filter((w) => w.priority === 'URGENT').length,
    high: warnings.filter((w) => w.priority === 'HIGH').length,
    delivered: warnings.filter((w) => w.status === 'DELIVERED').length,
    failed: warnings.filter((w) => w.status === 'FAILED').length,
  };

  const handleDelete = useCallback(() => {
    if (selectedWarning) {
      deleteMutation.mutate(selectedWarning.id);
    }
  }, [selectedWarning, deleteMutation]);

  const handleView = useCallback(
    (warning: Warning) => {
      navigate(`/warnings/${warning.id}`);
    },
    [navigate]
  );

  const handleMarkAsRead = useCallback((warning: Warning) => {
    markAsReadMutation.mutate(warning.id);
  }, [markAsReadMutation]);

  const handleDeleteClick = useCallback((warning: Warning) => {
    setSelectedWarning(warning);
    setIsDeleteModalOpen(true);
  }, []);

  const handleEdit = useCallback((warning: Warning) => {
    // TODO: Implement edit
    console.log('Edit warning:', warning);
  }, []);

  const columns = [
    {
      key: 'subject',
      header: 'Subject',
      sortable: true,
      render: (warning: Warning) => (
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-primary-600" />
          <span className="font-medium truncate max-w-xs">{warning.subject || 'No Subject'}</span>
        </div>
      ),
      width: '250px',
    },
    {
      key: 'warningType',
      header: 'Channel',
      sortable: true,
      render: (warning: Warning) => (
        <NotificationTypeBadge value={warning.warningType || 'IN_APP'} />
      ),
    },
    {
      key: 'priority',
      header: 'Priority',
      sortable: true,
      render: (warning: Warning) => (
        <PriorityBadge value={warning.priority || 'MEDIUM'} />
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (warning: Warning) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            STATUS_COLORS[warning.status || 'PENDING']
          }`}
        >
          {warning.status || 'PENDING'}
        </span>
      ),
    },
    {
      key: 'recipient',
      header: 'Recipient',
      sortable: true,
      render: (warning: Warning) => (
        <span className="text-sm">{warning.recipient || 'N/A'}</span>
      ),
    },
    {
      key: 'isRead',
      header: 'Read',
      sortable: true,
      render: (warning: Warning) => (
        <span className="text-sm">
          {warning.isRead ? (
            <CheckCircle className="w-4 h-4 text-success-600 mx-auto" />
          ) : (
            <XCircle className="w-4 h-4 text-gray-400 mx-auto" />
          )}
        </span>
      ),
      className: 'text-center',
    },
    {
      key: 'createdAt',
      header: 'Sent At',
      sortable: true,
      render: (warning: Warning) => (
        <span className="text-sm text-gray-500">
          {warning.createdAt ? new Date(warning.createdAt).toLocaleString() : 'N/A'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (warning: Warning) => (
        <ActionButtons
          onView={() => handleView(warning)}
          onEdit={() => handleEdit(warning)}
          onDelete={() => handleDeleteClick(warning)}
          showDelete={!warning.isRead}
        />
      ),
      className: 'w-24',
    },
  ];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <LoadingState message="Loading warnings..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Error Loading Warnings</h2>
          <p className="text-danger-600">{error?.message || 'Failed to load warnings'}</p>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['warnings'] })}
            className="btn btn-primary mt-4"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Warnings</h1>
            <p className="text-gray-600 mt-1">
              View and manage crisis warnings and notifications
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ['warnings'] })}
              className="btn btn-secondary btn-with-icon"
            >
              <Clock className="w-5 h-5" />
              Refresh
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard
            title="Total Warnings"
            value={stats.total}
            icon={<Bell className="w-6 h-6 text-primary-600" />}
          />
          <StatsCard
            title="Unread"
            value={stats.unread}
            icon={<AlertTriangle className="w-6 h-6 text-warning-600" />}
            change={stats.unread > 0 ? 'New' : 'All Read'}
            trend={stats.unread > 0 ? 'up' : 'neutral'}
          />
          <StatsCard
            title="Urgent"
            value={stats.urgent}
            icon={<XCircle className="w-6 h-6 text-danger-600" />}
            change="High Priority"
            trend="up"
          />
          <StatsCard
            title="Delivered"
            value={stats.delivered}
            icon={<CheckCircle className="w-6 h-6 text-success-600" />}
            change={`${Math.round((stats.delivered / stats.total) * 100 || 0)}%`}
            trend="up"
          />
        </div>
      </div>

      {/* Data Table */}
      <div className="card">
        {warnings.length === 0 ? (
          <EmptyState
            icon={<Bell className="w-16 h-16 text-gray-400" />}
            title="No Warnings Found"
            description="Warnings will appear here when crises are detected and notifications are sent"
          />
        ) : (
          <DataTable
            data={warnings}
            columns={columns}
            keyExtractor={(warning) => warning.id.toString()}
            searchKeys={['subject', 'warningType', 'recipient', 'message']}
            searchPlaceholder="Search warnings..."
            emptyMessage="No warnings found matching your search"
            onRowClick={(warning) => {
              if (!warning.isRead) {
                markAsReadMutation.mutate(warning.id);
              }
              navigate(`/warnings/${warning.id}`);
            }}
          />
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setSelectedWarning(null);
        }}
        onConfirm={handleDelete}
        title="Delete Warning"
        message={`Are you sure you want to delete this warning? This action cannot be undone.`}
        confirmText="Delete Warning"
        cancelText="Cancel"
        variant="danger"
      />
    </div>
  );
};

export default WarningListPage;
