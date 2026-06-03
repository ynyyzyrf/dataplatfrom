/** Application router configuration */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import AppLayout from '../components/layout/AppLayout';
import LoginPage from '../pages/Login/LoginPage';
import DashboardListPage from '../pages/Dashboard/DashboardListPage';
import DataSourceListPage from '../pages/DataSource/DataSourceListPage';
import SyncJobListPage from '../pages/SyncJob/SyncJobListPage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboards" replace /> },
      { path: 'dashboards', element: <DashboardListPage /> },
      { path: 'data-sources', element: <DataSourceListPage /> },
      { path: 'sync-jobs', element: <SyncJobListPage /> },
    ],
  },
  // Catch-all
  {
    path: '*',
    element: <Navigate to="/dashboards" replace />,
  },
]);
