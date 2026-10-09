import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

interface PublicRouteProps {
  children?: React.ReactNode
}

function PublicRoute({ children }: PublicRouteProps) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    // You can add a loading spinner here
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full border-4 border-primary-200 border-t-primary-600 h-12 w-12" />
      </div>
    )
  }

  // If user is authenticated, redirect to dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

export default PublicRoute