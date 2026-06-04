/** Application router configuration */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import AppLayout from '../components/layout/AppLayout';
import LoginPage from '../pages/Login/LoginPage';
import DashboardListPage from '../pages/Dashboard/DashboardListPage';
import DashboardBuilder from '../pages/Dashboard/DashboardBuilder';
import DashboardPreview from '../pages/Dashboard/DashboardPreview';
import DataSourceListPage from '../pages/DataSource/DataSourceListPage';
import SyncJobListPage from '../pages/SyncJob/SyncJobListPage';
import UserListPage from '../pages/Users/UserListPage';
import RoleListPage from '../pages/Roles/RoleListPage';
import AuditLogPage from '../pages/Audit/AuditLogPage';
import AlertRuleListPage from '../pages/Alerts/AlertRuleListPage';
import NotificationPage from '../pages/Notifications/NotificationPage';
import MonitoringPage from '../pages/Monitoring/MonitoringPage';
import DataRecordListPage from '../pages/DataRecord/DataRecordListPage';

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
      { path: 'dashboards/:id/build', element: <DashboardBuilder /> },
      { path: 'dashboards/:id/preview', element: <DashboardPreview /> },
      { path: 'data-sources', element: <DataSourceListPage /> },
      { path: 'sync-jobs', element: <SyncJobListPage /> },
      { path: 'data-records', element: <DataRecordListPage /> },
      { path: 'users', element: <UserListPage /> },
      { path: 'roles', element: <RoleListPage /> },
      { path: 'audit-logs', element: <AuditLogPage /> },
      { path: 'alert-rules', element: <AlertRuleListPage /> },
      { path: 'notifications', element: <NotificationPage /> },
      { path: 'monitoring', element: <MonitoringPage /> },
    ],
  },
  // Catch-all
  {
    path: '*',
    element: <Navigate to="/dashboards" replace />,
  },
]);
