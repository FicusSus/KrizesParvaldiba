import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

interface ProtectedRouteProps {
  children?: React.ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuthStore()
  const location = useLocation()

  if (isLoading) {
    // You can add a loading spinner here
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full border-4 border-primary-200 border-t-primary-600 h-12 w-12" />
      </div>
    )
  }

  if (!isAuthenticated) {
    // Redirect to login page, but save the requested location
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export default ProtectedRoute