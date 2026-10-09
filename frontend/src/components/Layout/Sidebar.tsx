import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Database, 
  AlertTriangle, 
  Bell, 
  Users, 
  Settings, 
  Home 
} from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { UserRole } from '../../types'

// Navigation items
const navItems = [
  {
    to: '/',
    icon: Home,
    label: 'Home',
    roles: [UserRole.ADMIN, UserRole.ANALYST, UserRole.USER],
  },
  {
    to: '/dashboard',
    icon: LayoutDashboard,
    label: 'Dashboard',
    roles: [UserRole.ADMIN, UserRole.ANALYST, UserRole.USER],
  },
  {
    to: '/data',
    icon: Database,
    label: 'Data',
    roles: [UserRole.ADMIN, UserRole.ANALYST],
  },
  {
    to: '/crisis',
    icon: AlertTriangle,
    label: 'Crisis',
    roles: [UserRole.ADMIN, UserRole.ANALYST, UserRole.USER],
  },
  {
    to: '/warnings',
    icon: Bell,
    label: 'Warnings',
    roles: [UserRole.ADMIN, UserRole.ANALYST, UserRole.USER],
  },
  {
    to: '/users',
    icon: Users,
    label: 'Users',
    roles: [UserRole.ADMIN],
  },
  {
    to: '/settings',
    icon: Settings,
    label: 'Settings',
    roles: [UserRole.ADMIN, UserRole.ANALYST, UserRole.USER],
  },
]

function Sidebar() {
  const location = useLocation()
  const { user } = useAuthStore()

  // Filter navigation items based on user role
  const visibleNavItems = navItems.filter(item => 
    user && item.roles.includes(user.role as UserRole)
  )

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-white border-r border-gray-200 hidden md:block">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center justify-center h-16 border-b border-gray-200">
          <h1 className="text-xl font-bold text-primary-600">CrisisPredict</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {visibleNavItems.map((item) => {
              const isActive = location.pathname === item.to
              return (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-primary-50 text-primary-600 font-medium' 
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* User info at bottom */}
        <div className="p-4 border-t border-gray-200">
          {user && (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                <span className="text-primary-600 font-medium text-sm">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">{user.username}</p>
                <p className="text-sm text-gray-500 truncate">{user.email}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar