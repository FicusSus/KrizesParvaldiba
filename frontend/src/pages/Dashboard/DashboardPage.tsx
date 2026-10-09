import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  AlertTriangle, 
  Database, 
  Bell, 
  TrendingUp,
  Clock,
  ShieldCheck,
  ArrowRight
} from 'lucide-react'
import { useDashboardStore } from '../../stores/dashboardStore'
import { dashboardService } from '../../services/dashboardService'
import { useAuthStore } from '../../stores/authStore'
import CrisisStatsCard from '../../components/Charts/CrisisStatsCard'
import WarningStatsCard from '../../components/Charts/WarningStatsCard'
import DataStatsCard from '../../components/Charts/DataStatsCard'
import SystemHealthCard from '../../components/Charts/SystemHealthCard'
import CrisisTimelineChart from '../../components/Charts/CrisisTimelineChart'
import RecentActivity from '../../components/Common/RecentActivity'
import { toast } from 'sonner'

function DashboardPage() {
  const { user } = useAuthStore()
  const { 
    stats, 
    crisisTrends, 
    dataProcessingStats, 
    recentCrises, 
    recentWarnings,
    isLoading, 
    error,
    setStats,
    setCrisisTrends,
    setDataProcessingStats,
    setRecentCrises,
    setRecentWarnings,
    setLoading,
    setError
  } = useDashboardStore()

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [dashboardStats, trends, processingStats, crises, warnings] = await Promise.all([
        dashboardService.getDashboardStats(),
        dashboardService.getCrisisTrends(30),
        dashboardService.getDataProcessingStats(),
        dashboardService.getRecentCrises(5),
        dashboardService.getRecentWarnings(5),
      ])
      
      setStats(dashboardStats)
      setCrisisTrends(trends)
      setDataProcessingStats(processingStats)
      setRecentCrises(crises)
      setRecentWarnings(warnings)
      
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
      setError('Failed to load dashboard data')
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData()
  }, [setStats, setCrisisTrends, setDataProcessingStats, setRecentCrises, setRecentWarnings, setLoading, setError])

  // Auto-refresh data every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchDashboardData()
    }, 5 * 60 * 1000) // 5 minutes
    
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* Welcome banner */}
      {user && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold mb-2">
                Welcome back, {user.full_name || user.username}!
              </h1>
              <p className="text-primary-100">
                Here's what's happening with your crisis prediction system.
              </p>
            </div>
            <div className="hidden md:block">
              <ShieldCheck className="w-12 h-12 opacity-20" />
            </div>
          </div>
        </motion.div>
      )}

      {/* Loading state */}
      {isLoading && !stats && (
        <div className="flex items-center justify-center py-12">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center gap-4"
          >
            <div className="animate-spin rounded-full border-4 border-primary-200 border-t-primary-600 h-12 w-12" />
            <p className="text-gray-600">Loading dashboard data...</p>
          </motion.div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="alert alert-danger"
        >
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5" />
            <span>{error}</span>
          </div>
          <button 
            onClick={fetchDashboardData}
            className="mt-2 btn btn-sm btn-outline"
          >
            Try again
          </button>
        </motion.div>
      )}

      {/* Stats cards */}
      {stats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <CrisisStatsCard 
            total={stats.total_crises} 
            active={stats.active_crises} 
            highPriority={stats.high_priority_crises}
          />
          
          <WarningStatsCard 
            total={stats.total_warnings} 
            delivered={stats.delivered_warnings} 
            pending={stats.pending_warnings}
          />
          
          <DataStatsCard 
            total={stats.total_datasets} 
            processed={stats.processed_datasets} 
            pending={stats.pending_datasets}
          />
          
          <SystemHealthCard 
            health={stats.system_health} 
            accuracy={stats.model_accuracy}
          />
        </motion.div>
      )}

      {/* Main content grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Crisis timeline chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <CrisisTimelineChart data={crisisTrends} isLoading={isLoading} />
        </motion.div>

        {/* Data processing stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          <div className="card h-full">
            <div className="card-header">
              <h2 className="card-title">Data Processing</h2>
            </div>
            
            {dataProcessingStats ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Total Size</span>
                  <span className="font-medium text-gray-900">
                    {(dataProcessingStats.total_size / (1024 * 1024)).toFixed(2)} GB
                  </span>
                </div>
                
                <div className="progress-bar">
                  <div 
                    className="progress-bar-fill bg-primary-600" 
                    style={{
                      width: `${(dataProcessingStats.processed_size / dataProcessingStats.total_size) * 100}%`
                    }}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <p className="text-sm text-gray-600">Rows Processed</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {dataProcessingStats.row_count.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Columns</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {dataProcessingStats.column_count}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Processing Time</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {dataProcessingStats.processing_time.toFixed(1)}s
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Memory Usage</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {dataProcessingStats.memory_usage.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center py-8">
                <p className="text-gray-500">Loading processing stats...</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Recent activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.6 }}
        className="grid lg:grid-cols-2 gap-6"
      >
        <RecentActivity 
          title="Recent Crises" 
          data={recentCrises} 
          type="crisis" 
          isLoading={isLoading}
        />
        <RecentActivity 
          title="Recent Warnings" 
          data={recentWarnings} 
          type="warning" 
          isLoading={isLoading}
        />
      </motion.div>

      {/* Quick actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.6 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="card-title">Quick Actions</h2>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link 
            to="/data" 
            className="flex flex-col items-center gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center">
              <Database className="w-6 h-6 text-primary-600" />
            </div>
            <span className="font-medium text-gray-900">Upload Data</span>
            <span className="text-sm text-gray-500">Add new datasets</span>
          </Link>
          
          <Link 
            to="/crisis" 
            className="flex flex-col items-center gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <div className="w-12 h-12 bg-warning-50 rounded-xl flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-warning-600" />
            </div>
            <span className="font-medium text-gray-900">View Crises</span>
            <span className="text-sm text-gray-500">Monitor predictions</span>
          </Link>
          
          <Link 
            to="/warnings" 
            className="flex flex-col items-center gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <div className="w-12 h-12 bg-danger-50 rounded-xl flex items-center justify-center">
              <Bell className="w-6 h-6 text-danger-600" />
            </div>
            <span className="font-medium text-gray-900">My Warnings</span>
            <span className="text-sm text-gray-500">Check notifications</span>
          </Link>
          
          <Link 
            to="/settings" 
            className="flex flex-col items-center gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <div className="w-12 h-12 bg-secondary-50 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-secondary-600" />
            </div>
            <span className="font-medium text-gray-900">Settings</span>
            <span className="text-sm text-gray-500">Configure system</span>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}

export default DashboardPage