/**
 * System Health Card Component
 * Displays system health metrics
 */

import React from 'react';
import { Heart, CheckCircle, AlertTriangle } from 'lucide-react';

interface SystemHealthCardProps {
  health?: number;
  accuracy?: number;
}

function SystemHealthCard({ health = 100, accuracy = 95 }: SystemHealthCardProps) {
  const getHealthStatus = () => {
    if (health >= 80) return { label: 'Excellent', color: 'success' };
    if (health >= 50) return { label: 'Good', color: 'primary' };
    if (health >= 30) return { label: 'Warning', color: 'warning' };
    return { label: 'Critical', color: 'danger' };
  };

  const status = getHealthStatus();

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title flex items-center gap-2">
          <Heart className="w-5 h-5" />
          System Health
        </h2>
      </div>
      
      <div className="flex items-center gap-6 mt-4">
        <div className="flex-1">
          <div className="text-3xl font-bold text-gray-900">{health}%</div>
          <div className={`text-sm font-medium text-${status.color}-600`}>
            {status.label}
          </div>
          <div className="text-xs text-gray-500 mt-1">Overall Health</div>
        </div>
        
        <div className="w-20 h-20 relative">
          <svg className="w-full h-full" viewBox="0 0 36 36">
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="3"
            />
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke={health >= 80 ? '#22c55e' : health >= 50 ? '#3b82f6' : health >= 30 ? '#f59e0b' : '#ef4444'}
              strokeWidth="3"
              strokeDasharray={`${2 * Math.PI * 15.9155 * (health / 100)} 1000`}
              strokeLinecap="round"
              transform="rotate(-90 18 18)"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center text-lg font-bold">
            {health}%
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-100 space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Model Accuracy</span>
          <span className="font-medium text-gray-900">{accuracy}%</span>
        </div>
        <div className="flex items-center gap-2">
          <CheckCircle className={`w-4 h-4 text-${health >= 80 ? 'success' : 'gray'}-600`} />
          <span className={`text-sm text-${health >= 80 ? 'success' : 'gray'}-600`}>
            All systems operational
          </span>
        </div>
      </div>
    </div>
  );
}

export default SystemHealthCard;
