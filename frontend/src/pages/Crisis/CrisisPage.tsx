"""
Crisis Page

Parent component for crisis-related routes.
"""

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { CrisisListPage } from './CrisisListPage';

function CrisisPage() {
  return (
    <Routes>
      <Route index element={<CrisisListPage />} />
      <Route path="list" element={<CrisisListPage />} />
      <Route path="predict" element={<div>Prediction Page (Coming Soon)</div>} />
      <Route path=":id" element={<div>Crisis Detail Page (Coming Soon)</div>} />
      <Route path="*" element={<Navigate to="." replace />} />
    </Routes>
  );
}

export default CrisisPage;
