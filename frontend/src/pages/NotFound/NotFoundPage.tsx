/**
 * Not Found Page
 * 404 page for routes that don't exist.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="mb-6">
          <AlertTriangle className="w-24 h-24 text-danger-600 mx-auto" />
        </div>
        <h1 className="text-6xl font-bold text-danger-600 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Page Not Found</h2>
        <p className="text-gray-600 mb-6">
          The page you are looking for does not exist or has been moved.
        </p>
        <div className="flex gap-4 justify-center">
          <button onClick={() => navigate('/')} className="btn btn-primary">
            Go to Home
          </button>
          <button onClick={() => navigate(-1)} className="btn btn-secondary">
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
}

export default NotFoundPage;
