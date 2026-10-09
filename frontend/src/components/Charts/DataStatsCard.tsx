import React from 'react'
import { Database, CheckCircle, Clock, FileText } from 'lucide-react'
import { motion } from 'framer-motion'

interface DataStatsCardProps {
  total: number
  processed: number
  pending: number
}

function DataStatsCard({ total, processed, pending }: DataStatsCardProps) {
  const processedPercentage = total > 0 ? ((processed / total) * 100).toFixed(1) : '0'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="card-title">Data Processing</h3>
          <p className="text-sm text-gray-500 mt-1">Dataset status</p>
        </div>
        <div className="w-12 h-12 bg-secondary-50 rounded-xl flex items-center justify-center">
          <Database className="w-6 h-6 text-secondary-600" />
        </div>
      </div>

      <div className="space-y-4">
        {/* Total Datasets */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Total Datasets</p>
            <p className="text-2xl font-bold text-gray-900">{total}</p>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-secondary">All Types</span>
          </div>
        </div>

        {/* Processed */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Processed</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-success-600">{processed}</p>
              <span className="text-xs bg-success-100 text-success-600 px-2 py-1 rounded-full">
                {processedPercentage}% complete
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-success">
              <CheckCircle className="w-3 h-3 mr-1" />
              Completed
            </span>
          </div>
        </div>

        {/* Pending */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div>
            <p className="text-sm text-gray-600">In Progress</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-warning-600">{pending}</p>
              <span className="text-xs bg-warning-100 text-warning-600 px-2 py-1 rounded-full">
                Processing
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="badge badge-warning">
              <Clock className="w-3 h-3 mr-1" />
              Processing
            </span>
            <span className="badge badge-secondary">
              <FileText className="w-3 h-3 mr-1" />
              Raw
            </span>
          </div>
        </div>

        {/* Capacity indicator */}
        <div className="flex items-center gap-2 pt-2">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-success-500 h-2 rounded-full"
              style={{ width: `${processedPercentage}%` }}
            />
          </div>
          <span className="text-sm text-gray-600 whitespace-nowrap">
            {processedPercentage}% processed
          </span>
        </div>
      </div>
    </motion.div>
  )
}

export default DataStatsCard