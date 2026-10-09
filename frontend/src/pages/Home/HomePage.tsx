import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Database, 
  AlertTriangle, 
  Bell, 
  ArrowRight,
  ShieldCheck 
} from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { motion } from 'framer-motion'

// Feature cards data
const features = [
  {
    icon: LayoutDashboard,
    title: 'Real-time Dashboard',
    description: 'Monitor crisis predictions and system health in real-time with comprehensive dashboards.',
    link: '/dashboard',
    color: 'primary',
  },
  {
    icon: Database,
    title: 'Large Data Processing',
    description: 'Process and analyze large datasets efficiently with our high-performance data pipeline.',
    link: '/data',
    color: 'secondary',
  },
  {
    icon: AlertTriangle,
    title: 'Crisis Prediction',
    description: 'Advanced ML models predict potential crises and their severity with high accuracy.',
    link: '/crisis',
    color: 'warning',
  },
  {
    icon: Bell,
    title: 'Warning System',
    description: 'Receive timely warnings via multiple channels to take proactive measures.',
    link: '/warnings',
    color: 'danger',
  },
]

// Stats data
const stats = [
  { value: '10K+', label: 'Datasets Processed' },
  { value: '99%', label: 'Prediction Accuracy' },
  { value: '24/7', label: 'Real-time Monitoring' },
  { value: '1M+', label: 'Warnings Sent' },
]

function HomePage() {
  const { user } = useAuthStore()
  const [isLoaded, setIsLoaded] = useState(false)

  // Animation on load
  useEffect(() => {
    setIsLoaded(true)
  }, [])

  return (
    <div className="space-y-8">
      {/* Hero section */}
      <motion.section 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center py-8"
      >
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Crisis Prediction & Warning System
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Advanced analytics and machine learning to predict and prevent crises 
            before they impact your operations.
          </p>
        </motion.div>

        {user && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mt-8"
          >
            <Link to="/dashboard" className="btn btn-primary btn-lg">
              Go to Dashboard
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
          </motion.div>
        )}

        {!user && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mt-8 flex gap-4 justify-center"
          >
            <Link to="/login" className="btn btn-primary btn-lg">
              Get Started
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
            <Link to="/register" className="btn btn-outline btn-lg">
              Create Account
            </Link>
          </motion.div>
        )}
      </motion.section>

      {/* Stats section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.6 }}
        className="py-8"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 text-center">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 + index * 0.1, duration: 0.6 }}
              className="p-6 bg-white rounded-xl shadow-sm border border-gray-100"
            >
              <div className="text-3xl font-bold text-primary-600 mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Features section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="py-8"
      >
        <h2 className="text-2xl font-bold text-center mb-8">
          Key Features
        </h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.4 + index * 0.1, duration: 0.6 }}
                whileHover={{ y: -5, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }}
                className="card p-6 transition-shadow"
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl bg-${feature.color}-50`}>
                    <Icon className={`w-6 h-6 text-${feature.color}-600`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {feature.description}
                    </p>
                    <Link 
                      to={feature.link} 
                      className="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
                    >
                      Learn more
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </motion.section>

      {/* Security and Compliance */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.8, duration: 0.6 }}
        className="py-8 text-center"
      >
        <div className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 rounded-full">
          <ShieldCheck className="w-5 h-5 text-success-600" />
          <span className="text-sm font-medium text-gray-700">
            Enterprise-grade security & compliance
          </span>
        </div>
      </motion.section>
    </div>
  )
}

export default HomePage