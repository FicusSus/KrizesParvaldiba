import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import Footer from './Footer'
import { useAuthStore } from '../../stores/authStore'

function Layout() {
  const { user } = useAuthStore()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header />
      
      <div className="flex">
        {/* Sidebar */}
        {user && <Sidebar />}
        
        {/* Main Content */}
        <main className="flex-1 p-6 md:p-8 lg:p-10">
          <Outlet />
        </main>
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  )
}

export default Layout