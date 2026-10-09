"""
Crisis List Page

Page for viewing and managing crisis predictions and detections.
"""

import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, AlertTriangle, Clock, CheckCircle, XCircle, Eye, Edit, Trash2, Search, Filter } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import DataTable from '../../components/Common/DataTable';
import {
  Badge,
  ActionButtons,
  EmptyState,
  LoadingState,
  Modal,
  ConfirmationDialog,
  StatsCard,
  SeverityBadge,
  StatusBadge,
} from '../../components/Common/TableComponents';
import { crisisService } from '../../services/crisisService';
import { useCrisisStore } from '../../stores/crisisStore';
import { Crisis } from '../../types';

const CRISIS_TYPES = [
  'FINANCIAL',
  'ECONOMIC',
  'POLITICAL',
  'SOCIAL',
  'ENVIRONMENTAL',
  'HEALTH',
  'SECURITY',
  'OTHER',
];

const SEVERITY_LEVELS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

const STATUS_OPTIONS = ['DETECTED', 'ANALYZING', 'ONGOING', 'RESOLVED', 'FALSE_ALARM'];

export const CrisisListPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState<string[]>([]);
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCrisis, setSelectedCrisis] = useState<Crisis | null>(null);

  // Fetch crises
  const {
    data: crises = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['crises'],
    queryFn: crisisService.getCrises,
  });

  // Delete crisis mutation
  const deleteMutation = useMutation({
    mutationFn: crisisService.deleteCrisis,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['crises'] });
      setIsDeleteModalOpen(false);
      setSelectedCrisis(null);
    },
    onError: (err) => {
      console.error('Delete failed:', err);
    },
  });

  // Filter crises based on filters
  const filteredCrises = crises.filter((crisis) => {
    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch =
        crisis.title?.toLowerCase().includes(searchLower) ||
        crisis.description?.toLowerCase().includes(searchLower) ||
        crisis.crisisType?.toLowerCase().includes(searchLower) ||
        crisis.location?.toLowerCase().includes(searchLower);
      if (!matchesSearch) return false;
    }

    // Severity filter
    if (severityFilter.length > 0 && crisis.severity) {
      if (!severityFilter.includes(crisis.severity)) return false;
    }

    // Type filter
    if (typeFilter.length > 0 && crisis.crisisType) {
      if (!typeFilter.includes(crisis.crisisType)) return false;
    }

    // Status filter
    if (statusFilter.length > 0 && crisis.status) {
      if (!statusFilter.includes(crisis.status)) return false;
    }

    return true;
  });

  // Calculate stats
  const stats = {
    total: crises.length,
    active: crises.filter((c) => c.status === 'ONGOING' || c.status === 'DETECTED' || c.status === 'ANALYZING').length,
    resolved: crises.filter((c) => c.status === 'RESOLVED').length,
    critical: crises.filter((c) => c.severity === 'CRITICAL').length,
    high: crises.filter((c) => c.severity === 'HIGH').length,
  };

  const handleDelete = useCallback(() => {
    if (selectedCrisis) {
      deleteMutation.mutate(selectedCrisis.id);
    }
  }, [selectedCrisis, deleteMutation]);

  const handleView = useCallback(
    (crisis: Crisis) => {
      navigate(`/crisis/${crisis.id}`);
    },
    [navigate]
  );

  const handleEdit = useCallback((crisis: Crisis) => {
    // TODO: Implement edit
    console.log('Edit crisis:', crisis);
  }, []);

  const handleDeleteClick = useCallback((crisis: Crisis) => {
    setSelectedCrisis(crisis);
    setIsDeleteModalOpen(true);
  }, []);

  const toggleSeverityFilter = useCallback((severity: string) => {
    setSeverityFilter((prev) =>
      prev.includes(severity) ? prev.filter((s) => s !== severity) : [...prev, severity]
    );
  }, []);

  const toggleTypeFilter = useCallback((type: string) => {
    setTypeFilter((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  }, []);

  const toggleStatusFilter = useCallback((status: string) => {
    setStatusFilter((prev) =>
      prev.includes(status) ? prev.filter((s) => s !== status) : [...prev, status]
    );
  }, []);

  const clearFilters = useCallback(() => {
    setSeverityFilter([]);
    setTypeFilter([]);
    setStatusFilter([]);
  }, []);

  const columns = [
    {
      key: 'title',
      header: 'Title',
      sortable: true,
      render: (crisis: Crisis) => (
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-warning-600" />
          <span className="font-medium">{crisis.title || 'Untitled Crisis'}</span>
        </div>
      ),
      width: '200px',
    },
    {
      key: 'crisisType',
      header: 'Type',
      sortable: true,
      render: (crisis: Crisis) => (
        <Badge value={crisis.crisisType || 'UNKNOWN'} type="crisis" className="text-xs" />
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      sortable: true,
      render: (crisis: Crisis) => (
        <SeverityBadge value={crisis.severity || 'MEDIUM'} />
      ),
    },
    {
      key: 'confidenceScore',
      header: 'Confidence',
      sortable: true,
      render: (crisis: Crisis) => (
        <span className="text-sm">
          {crisis.confidenceScore ? `${(crisis.confidenceScore * 100).toFixed(1)}%` : 'N/A'}
        </span>
      ),
    },
    {
      key: 'impactScore',
      header: 'Impact',
      sortable: true,
      render: (crisis: Crisis) => (
        <span className="text-sm">{crisis.impactScore ? crisis.impactScore.toFixed(1) : 'N/A'}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (crisis: Crisis) => (
        <StatusBadge value={crisis.status || 'DETECTED'} />
      ),
    },
    {
      key: 'location',
      header: 'Location',
      sortable: true,
      render: (crisis: Crisis) => (
        <span className="text-sm">{crisis.location || 'N/A'}</span>
      ),
    },
    {
      key: 'startDate',
      header: 'Started',
      sortable: true,
      render: (crisis: Crisis) => (
        <span className="text-sm text-gray-500">
          {crisis.startDate ? new Date(crisis.startDate).toLocaleDateString() : 'N/A'}
        </span>
      ),
    },
    {
      key: 'endDate',
      header: 'Ended',
      sortable: true,
      render: (crisis: Crisis) => (
        <span className="text-sm text-gray-500">
          {crisis.endDate ? new Date(crisis.endDate).toLocaleDateString() : 'N/A'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (crisis: Crisis) => (
        <ActionButtons
          onView={() => handleView(crisis)}
          onEdit={() => handleEdit(crisis)}
          onDelete={() => handleDeleteClick(crisis)}
        />
      ),
      className: 'w-24',
    },
  ];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <LoadingState message="Loading crisis data..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Error Loading Crises</h2>
          <p className="text-danger-600">{error?.message || 'Failed to load crisis data'}</p>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['crises'] })}
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
            <h1 className="text-3xl font-bold text-gray-900">Crisis Detection</h1>
            <p className="text-gray-600 mt-1">
              Monitor and manage detected crisis events
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsFilterOpen(true)}
              className="btn btn-secondary btn-with-icon"
            >
              <Filter className="w-5 h-5" />
              Filters
              {(severityFilter.length > 0 || typeFilter.length > 0 || statusFilter.length > 0) && (
                <span className="ml-1 px-2 py-0.5 bg-primary-600 text-white text-xs rounded-full">
                  {severityFilter.length + typeFilter.length + statusFilter.length}
                </span>
              )}
            </button>
            <button
              onClick={() => navigate('/crisis/predict')}
              className="btn btn-primary btn-with-icon"
            >
              <Plus className="w-5 h-5" />
              New Prediction
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard
            title="Total Crises"
            value={stats.total}
            icon={<AlertTriangle className="w-6 h-6 text-warning-600" />}
          />
          <StatsCard
            title="Active"
            value={stats.active}
            icon={<Clock className="w-6 h-6 text-primary-600" />}
            change={stats.active > 0 ? 'Active' : 'None'}
            trend={stats.active > 0 ? 'up' : 'neutral'}
          />
          <StatsCard
            title="Critical"
            value={stats.critical}
            icon={<XCircle className="w-6 h-6 text-danger-600" />}
            change="High Priority"
            trend="up"
          />
          <StatsCard
            title="Resolved"
            value={stats.resolved}
            icon={<CheckCircle className="w-6 h-6 text-success-600" />}
            change="100%"
            trend="up"
          />
        </div>
      </div>

      {/* Data Table */}
      <div className="card">
        {filteredCrises.length === 0 ? (
          <EmptyState
            icon={<AlertTriangle className="w-16 h-16 text-gray-400" />}
            title="No Crises Found"
            description={`${
              searchTerm || severityFilter.length > 0 || typeFilter.length > 0 || statusFilter.length > 0
                ? 'No crises match your filters'
                : 'No crises detected yet. Run a prediction to get started'
            }`}
            action={
              <button
                onClick={() => navigate('/crisis/predict')}
                className="btn btn-primary btn-with-icon"
              >
                <Plus className="w-5 h-5" />
                Run Prediction
              </button>
            }
          />
        ) : (
          <DataTable
            data={filteredCrises}
            columns={columns}
            keyExtractor={(crisis) => crisis.id.toString()}
            searchKeys={['title', 'crisisType', 'severity', 'location', 'description']}
            searchPlaceholder="Search crises..."
            emptyMessage="No crises found matching your search"
          />
        )}
      </div>

      {/* Filter Modal */}
      <Modal
        isOpen={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        title="Filter Crises"
        size="md"
      >
        <div className="space-y-6">
          <div className="form-group">
            <h3 className="font-semibold text-gray-900 mb-3">Severity</h3>
            <div className="flex flex-wrap gap-2">
              {SEVERITY_LEVELS.map((level) => (
                <button
                  key={level}
                  onClick={() => toggleSeverityFilter(level)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    severityFilter.includes(level)
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <SeverityBadge value={level} />
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <h3 className="font-semibold text-gray-900 mb-3">Crisis Type</h3>
            <div className="flex flex-wrap gap-2">
              {CRISIS_TYPES.map((type) => (
                <button
                  key={type}
                  onClick={() => toggleTypeFilter(type)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    typeFilter.includes(type)
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Badge value={type} type="crisis" className="text-xs" />
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <h3 className="font-semibold text-gray-900 mb-3">Status</h3>
            <div className="flex flex-wrap gap-2">
              {STATUS_OPTIONS.map((status) => (
                <button
                  key={status}
                  onClick={() => toggleStatusFilter(status)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    statusFilter.includes(status)
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <StatusBadge value={status} />
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button onClick={clearFilters} className="btn btn-secondary">
              Clear All
            </button>
            <button
              onClick={() => setIsFilterOpen(false)}
              className="btn btn-primary"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setSelectedCrisis(null);
        }}
        onConfirm={handleDelete}
        title="Delete Crisis"
        message={`Are you sure you want to delete this crisis? All associated data and warnings will be removed.`}
        confirmText="Delete Crisis"
        cancelText="Cancel"
        variant="danger"
      />
    </div>
  );
};

export default CrisisListPage;
