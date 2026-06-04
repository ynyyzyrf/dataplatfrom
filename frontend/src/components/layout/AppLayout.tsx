/** Main application layout with sidebar navigation */

import { useState } from 'react';
import { Layout, Menu, Button, theme, Dropdown } from 'antd';
import {
  DashboardOutlined,
  ApiOutlined,
  SyncOutlined,
  DatabaseOutlined,
  TeamOutlined,
  SafetyOutlined,
  AuditOutlined,
  AlertOutlined,
  BellOutlined,
  MonitorOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/auth';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/dashboards', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/data-sources', icon: <ApiOutlined />, label: '数据源' },
  { key: '/sync-jobs', icon: <SyncOutlined />, label: '同步任务' },
  { key: '/data-records', icon: <DatabaseOutlined />, label: '数据浏览' },
  { key: '/monitoring', icon: <MonitorOutlined />, label: '监控' },
  { type: 'divider' as const },
  { key: '/alert-rules', icon: <AlertOutlined />, label: '告警规则' },
  { key: '/notifications', icon: <BellOutlined />, label: '通知' },
  { type: 'divider' as const },
  { key: '/users', icon: <TeamOutlined />, label: '用户管理' },
  { key: '/roles', icon: <SafetyOutlined />, label: '角色管理' },
  { key: '/audit-logs', icon: <AuditOutlined />, label: '审计日志' },
];

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems = [
    { key: 'profile', icon: <UserOutlined />, label: user?.username || '用户' },
    { type: 'divider' as const },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true, onClick: handleLogout },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{
          height: 32, margin: 16, display: 'flex', alignItems: 'center',
          justifyContent: 'center', color: '#fff', fontWeight: 'bold', fontSize: collapsed ? 14 : 18,
        }}>
          {collapsed ? 'GDP' : 'DataPlatform'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: colorBgContainer, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Button type="text" icon={<UserOutlined />}>
              {user?.username}
            </Button>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: colorBgContainer, borderRadius: borderRadiusLG }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
