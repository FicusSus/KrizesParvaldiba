import React from 'react'
import { Bell, CheckCircle, Clock, XCircle } from 'lucide-react'
import { motion } from 'framer-motion'

interface WarningStatsCardProps {
  total: number
  delivered: number
  pending: number
}

function WarningStatsCard({ total, delivered, pending }: WarningStatsCardProps) {
  const deliveryRate = total > 0 ? ((delivered / total) * 100).toFixed(1) : '0'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="card-title">Warning System</h3>
          <p className="text-sm text-gray-500 mt-1">Notification status</p>
        </div>
        <div className="w-12 h-12 bg-warning-50 rounded-xl flex items-center justify-center">
          <Bell className="w-6 h-6 text-warning-600" />
        </div>
      </div>

      <div className="space-y-4">
        {/* Total Warnings */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Total Warnings</p>
            <p className="text-2xl font-bold text-gray-900">{total}</p>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-warning">All Channels</span>
          </div>
        </div>

        {/* Delivered */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Delivered</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-success-600">{delivered}</p>
              <span className="text-xs bg-success-100 text-success-600 px-2 py-1 rounded-full">
                {deliveryRate}% rate
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-success">
              <CheckCircle className="w-3 h-3 mr-1" />
              Delivered
            </span>
            <span className="badge badge-success">
              <CheckCircle className="w-3 h-3 mr-1" />
              Read
            </span>
          </div>
        </div>

        {/* Pending */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div>
            <p className="text-sm text-gray-600">Pending</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-warning-600">{pending}</p>
              <span className="text-xs bg-warning-100 text-warning-600 px-2 py-1 rounded-full">
                In Queue
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-warning">
              <Clock className="w-3 h-3 mr-1" />
              Pending
            </span>
            <span className="badge badge-danger">
              <XCircle className="w-3 h-3 mr-1" />
              Failed
            </span>
          </div>
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 pt-2">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
          <span className="text-sm text-success-600">System operational</span>
        </div>
      </div>
    </motion.div>
  )
}

export default WarningStatsCard