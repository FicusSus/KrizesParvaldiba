import React from 'react'

function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="bg-gray-100 border-t border-gray-200">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-center md:text-left">
            <p className="text-sm text-gray-600">
              © {year} Crisis Prediction System. All rights reserved.
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Monitor, predict, and respond to crises effectively.
            </p>
          </div>
          <div className="flex gap-4 text-sm text-gray-600">
            <a href="#" className="hover:text-primary-600 transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-primary-600 transition-colors">
              Terms of Service
            </a>
            <a href="#" className="hover:text-primary-600 transition-colors">
              Documentation
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer