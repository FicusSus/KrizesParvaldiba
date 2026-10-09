import React from 'react'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import { CrisisSeverity } from '../../types'

interface CrisisStatsCardProps {
  total: number
  active: number
  highPriority: number
}

function CrisisStatsCard({ total, active, highPriority }: CrisisStatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="card-title">Crisis Overview</h3>
          <p className="text-sm text-gray-500 mt-1">Total predictions</p>
        </div>
        <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center">
          <AlertTriangle className="w-6 h-6 text-primary-600" />
        </div>
      </div>

      <div className="space-y-4">
        {/* Total Crises */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Total Crises</p>
            <p className="text-2xl font-bold text-gray-900">{total}</p>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-primary">All Types</span>
          </div>
        </div>

        {/* Active Crises */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Active</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-warning-600">{active}</p>
              <span className="text-xs bg-warning-100 text-warning-600 px-2 py-1 rounded-full">
                Needs Attention
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-warning">Predicted</span>
            <span className="badge badge-danger">Confirmed</span>
            <span className="badge badge-danger">Ongoing</span>
          </div>
        </div>

        {/* High Priority */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div>
            <p className="text-sm text-gray-600">High Priority</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-danger-600">{highPriority}</p>
              <span className="text-xs bg-danger-100 text-danger-600 px-2 py-1 rounded-full">
                Urgent
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-danger">High</span>
            <span className="badge bg-danger-200 text-danger-800">Critical</span>
          </div>
        </div>

        {/* Trend indicator */}
        <div className="flex items-center gap-2 pt-2">
          <div className="w-2 h-2 bg-success-500 rounded-full" />
          <span className="text-sm text-success-600">System monitoring</span>
        </div>
      </div>
    </motion.div>
  )
}

export default CrisisStatsCard