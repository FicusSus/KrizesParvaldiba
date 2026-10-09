import React, { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { Toaster } from 'sonner'
import Layout from './components/Layout/Layout'
import HomePage from './pages/Home/HomePage'
import DashboardPage from './pages/Dashboard/DashboardPage'
import DataPage from './pages/Data/DataPage'
import CrisisPage from './pages/Crisis/CrisisPage'
import WarningsPage from './pages/Warnings/WarningsPage'
import UsersPage from './pages/Users/UsersPage'
import SettingsPage from './pages/Settings/SettingsPage'
import LoginPage from './pages/Auth/LoginPage'
import RegisterPage from './pages/Auth/RegisterPage'
import NotFoundPage from './pages/NotFound/NotFoundPage'
import ProtectedRoute from './components/Auth/ProtectedRoute'
import PublicRoute from './components/Auth/PublicRoute'
import { useAuthStore } from './stores/authStore'
import { checkAuth } from './services/authService'

function App() {
  const location = useLocation()
  const { user, setUser, setToken, clearAuth } = useAuthStore()
  
  // Check authentication on app load
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const { user: currentUser, token } = await checkAuth()
        if (currentUser && token) {
          setUser(currentUser)
          setToken(token)
        } else {
          clearAuth()
        }
      } catch (error) {
        console.error('Auth initialization failed:', error)
        clearAuth()
      }
    }
    
    initializeAuth()
  }, [setUser, setToken, clearAuth])

  return (
    <>
      {/* Toast notifications */}
      <Toaster 
        position="top-right" 
        toastOptions={{
          classNames: {
            toast: 'bg-white border border-gray-200 shadow-lg rounded-lg',
            success: 'border-success-600',
            error: 'border-danger-600',
            warning: 'border-warning-600',
            info: 'border-primary-600',
          }
        }}
        richColors
      />
      
      {/* Main app routes */}
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          {/* Public routes */}
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
          
          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="data" element={<DataPage />} />
              <Route path="crisis" element={<CrisisPage />} />
              <Route path="warnings" element={<WarningsPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Route>
          
          {/* Redirects */}
          <Route path="/*" element={<NotFoundPage />} />
        </Routes>
      </AnimatePresence>
    </>
  )
}

export default App