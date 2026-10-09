/**
 * Recent Activity Component
 * Displays recent items (crises, warnings, etc.)
 */

import React from 'react';
import { Clock, AlertTriangle, Bell } from 'lucide-react';
import { Badge, EmptyState, LoadingState } from './TableComponents';

interface RecentActivityProps {
  title: string;
  data: any[];
  type: 'crisis' | 'warning' | 'data';
  isLoading?: boolean;
}

function RecentActivity({ title, data = [], type = 'crisis', isLoading = false }: RecentActivityProps) {
  const getIcon = () => {
    switch (type) {
      case 'warning':
        return <Bell className="w-4 h-4" />;
      case 'data':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <AlertTriangle className="w-4 h-4" />;
    }
  };

  const getTime = (item: any) => {
    if (item.created_at) return new Date(item.created_at).toLocaleString();
    if (item.start_date) return new Date(item.start_date).toLocaleDateString();
    return 'N/A';
  };

  const getTitle = (item: any) => {
    if (type === 'warning') return item.subject || 'No subject';
    return item.title || item.name || 'Untitled';
  };

  const getSeverity = (item: any) => {
    if (type === 'crisis') return item.severity || 'MEDIUM';
    if (type === 'warning') return item.priority || 'MEDIUM';
    return null;
  };

  if (isLoading) {
    return <LoadingState message="Loading..." />;
  }

  if (data.length === 0) {
    return (
      <div className="card h-full">
        <div className="card-header">
          <h2 className="card-title flex items-center gap-2">
            {getIcon()}
            {title}
          </h2>
        </div>
        <EmptyState
          icon={<Clock className="w-8 h-8 text-gray-400" />}
          title="No recent activity"
          description={`No ${type} found`}
        />
      </div>
    );
  }

  return (
    <div className="card h-full">
      <div className="card-header">
        <h2 className="card-title flex items-center gap-2">
          {getIcon()}
          {title}
        </h2>
      </div>
      
      <div className="space-y-4">
        {data.slice(0, 5).map((item, index) => (
          <div
            key={item.id || index}
            className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
              <span className="text-sm font-medium text-gray-600">{index + 1}</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 truncate">{getTitle(item)}</p>
              <p className="text-sm text-gray-500">{getTime(item)}</p>
            </div>
            {getSeverity(item) && (
              <div className="flex-shrink-0">
                <Badge value={getSeverity(item) || ''} type={type === 'crisis' ? 'severity' : 'priority'} />
              </div>
            )}
          </div>
        ))}
      </div>
      
      {data.length > 5 && (
        <div className="mt-4 pt-4 border-t border-gray-100 text-center">
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            View all {type}s →
          </button>
        </div>
      )}
    </div>
  );
}

export default RecentActivity;
