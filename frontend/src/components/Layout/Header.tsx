import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Menu, Bell, User, LogOut, Settings } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { useWarningStore } from '../../stores/warningStore'
import { warningService } from '../../services/warningService'

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  
  const { user, clearAuth } = useAuthStore()
  const { unreadCount, setUnreadCount } = useWarningStore()

  // Fetch unread count on mount
  useEffect(() => {
    if (user) {
      const fetchUnreadCount = async () => {
        try {
          const count = await warningService.getUnreadWarningsCount()
          setUnreadCount(count)
        } catch (error) {
          console.error('Failed to fetch unread count:', error)
        }
      }
      fetchUnreadCount()
    }
  }, [user, setUnreadCount])

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen)
  const toggleProfile = () => setIsProfileOpen(!isProfileOpen)
  const toggleNotifications = () => setIsNotificationsOpen(!isNotificationsOpen)

  const handleLogout = async () => {
    clearAuth()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-4 md:px-6 lg:px-8">
        {/* Mobile menu button */}
        <button
          onClick={toggleMenu}
          className="md:hidden p-2 rounded-lg hover:bg-gray-100"
        >
          <Menu className="w-6 h-6 text-gray-600" />
        </button>

        {/* Logo for mobile */}
        <div className="md:hidden">
          <Link to="/" className="text-lg font-bold text-primary-600">
            CrisisPredict
          </Link>
        </div>

        {/* Breadcrumb */}
        <div className="hidden md:flex flex-1 max-w-md">
          <nav className="flex items-center gap-2 text-sm text-gray-500">
            <span className="font-medium text-primary-600">
              {location.pathname === '/' ? 'Home' : location.pathname.split('/').pop()}
            </span>
          </nav>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          {user && (
            <>
              <button
                onClick={toggleNotifications}
                className="relative p-2 rounded-lg hover:bg-gray-100"
              >
                <Bell className="w-6 h-6 text-gray-600" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-danger-600 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>

              {/* Profile dropdown */}
              <button
                onClick={toggleProfile}
                className="p-2 rounded-lg hover:bg-gray-100"
              >
                <User className="w-6 h-6 text-gray-600" />
              </button>
            </>
          )}

          {/* Login/Register buttons for guests */}
          {!user && (
            <div className="flex gap-2">
              <Link to="/login" className="btn btn-outline">Login</Link>
              <Link to="/register" className="btn btn-primary">Register</Link>
            </div>
          )}
        </div>

        {/* Notifications dropdown */}
        {isNotificationsOpen && (
          <div className="absolute top-14 right-20 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-200 py-2 hidden md:block">
            <div className="px-4 py-2 border-b border-gray-200 mb-2">
              <h3 className="font-semibold text-gray-900">Notifications</h3>
            </div>
            <div className="max-h-80 overflow-y-auto">
              <div className="text-center py-4 text-gray-500 text-sm">
                No new notifications
              </div>
            </div>
            <div className="px-4 py-2 border-t border-gray-200">
              <Link 
                to="/warnings" 
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                onClick={() => setIsNotificationsOpen(false)}
              >
                View all warnings
              </Link>
            </div>
          </div>
        )}

        {/* Profile dropdown */}
        {isProfileOpen && user && (
          <div className="absolute top-14 right-6 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 hidden md:block">
            <div className="px-4 py-2 border-b border-gray-200 mb-2">
              <p className="font-medium text-gray-900">{user.username}</p>
              <p className="text-sm text-gray-500">{user.email}</p>
            </div>
            <div className="space-y-1">
              <Link
                to="/settings"
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                onClick={() => setIsProfileOpen(false)}
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 w-full px-4 py-2 text-sm text-danger-600 hover:bg-danger-50"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        )}

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 md:hidden">
            <div className="fixed top-0 left-0 h-full w-64 bg-white shadow-xl transform translate-x-0 transition-transform">
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <h1 className="text-lg font-bold text-primary-600">CrisisPredict</h1>
                <button onClick={toggleMenu} className="p-2">
                  <span className="text-2xl">&times;</span>
                </button>
              </div>
              <nav className="p-4">
                <ul className="space-y-2">
                  <li><Link to="/" className="block px-4 py-2 text-gray-700 hover:bg-gray-50" onClick={toggleMenu}>Home</Link></li>
                  <li><Link to="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-50" onClick={toggleMenu}>Dashboard</Link></li>
                  <li><Link to="/data" className="block px-4 py-2 text-gray-700 hover:bg-gray-50" onClick={toggleMenu}>Data</Link></li>
                  <li><Link to="/crisis" className="block px-4 py-2 text-gray-700 hover:bg-gray-50" onClick={toggleMenu}>Crisis</Link></li>
                  <li><Link to="/warnings" className="block px-4 py-2 text-gray-700 hover:bg-gray-50" onClick={toggleMenu}>Warnings</Link></li>
                  {user?.role === 'admin' && (
                    <li><Link to="/users" className="block px-4 py-2 text-gray-700 hover:bg-gray-50" onClick={toggleMenu}>Users</Link></li>
                  )}
                  <li><Link to="/settings" className="block px-4 py-2 text-gray-700 hover:bg-gray-50" onClick={toggleMenu}>Settings</Link></li>
                </ul>
              </nav>
              <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
                {user && (
                  <button onClick={handleLogout} className="btn btn-danger btn-block">
                    Logout
                  </button>
                )}
                {!user && (
                  <div className="space-y-2">
                    <Link to="/login" className="btn btn-outline btn-block" onClick={toggleMenu}>Login</Link>
                    <Link to="/register" className="btn btn-primary btn-block" onClick={toggleMenu}>Register</Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header