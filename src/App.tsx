/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import { useThemeStore } from './stores/themeStore';

// Layouts
import { DashboardLayout } from './components/layout/DashboardLayout';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardOverviewPage } from './pages/DashboardOverviewPage';
import { ScanBrowserPage } from './pages/ScanBrowserPage';
import { ProtectMyDataPage } from './pages/ProtectMyDataPage';
import { ProtectedSitesPage } from './pages/ProtectedSitesPage';
import { SiteDetailPage } from './pages/SiteDetailPage';
import { LiveActivityPage } from './pages/LiveActivityPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { PoliciesPage } from './pages/PoliciesPage';
import { SettingsPage } from './pages/SettingsPage';

export default function App() {
  const { initialize } = useAuthStore();
  const { initTheme } = useThemeStore();

  useEffect(() => {
    initTheme();
    initialize();
  }, [initialize, initTheme]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Dashboard & Shield Management (Protected by DashboardLayout) */}
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<DashboardOverviewPage />} />
          <Route path="/scan" element={<ScanBrowserPage />} />
          <Route path="/protect" element={<ProtectMyDataPage />} />
          <Route path="/sites" element={<ProtectedSitesPage />} />
          <Route path="/sites/:id" element={<SiteDetailPage />} />
          <Route path="/activity" element={<LiveActivityPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/policies" element={<PoliciesPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
