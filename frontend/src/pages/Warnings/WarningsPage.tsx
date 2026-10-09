"""
Warnings Page

Parent component for warning-related routes.
"""

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { WarningListPage } from './WarningListPage';

function WarningsPage() {
  return (
    <Routes>
      <Route index element={<WarningListPage />} />
      <Route path="list" element={<WarningListPage />} />
      <Route path=":id" element={<div>Warning Detail Page (Coming Soon)</div>} />
      <Route path="*" element={<Navigate to="." replace />} />
    </Routes>
  );
}

export default WarningsPage;
