/** User management page */

import { useState, useEffect } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select, message, Popconfirm, Switch,
} from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import client from '../../api/client';

interface UserItem {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  roles: string[];
}

interface RoleItem {
  id: string;
  name: string;
  description?: string;
}

export default function UserListPage() {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [roles, setRoles] = useState<RoleItem[]>([]);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserItem | null>(null);
  const [selectedRoleIds, setSelectedRoleIds] = useState<string[]>([]);
  const [form] = Form.useForm();

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const { data } = await client.get('/users', { params: { page_size: 100 } });
      setUsers(data.items);
    } catch {
      message.error('加载用户失败');
    }
    setLoading(false);
  };

  const fetchRoles = async () => {
    try {
      const { data } = await client.get('/roles');
      setRoles(data);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchUsers(); fetchRoles(); }, []);

  const handleToggleActive = async (user: UserItem) => {
    try {
      await client.patch(`/users/${user.id}`, { is_active: !user.is_active });
      message.success(`用户${user.is_active ? '已禁用' : '已启用'}`);
      fetchUsers();
    } catch {
      message.error('用户更新失败');
    }
  };

  const handleDelete = async (userId: string) => {
    try {
      await client.delete(`/users/${userId}`);
      message.success('用户已删除');
      fetchUsers();
    } catch {
      message.error('用户删除失败');
    }
  };

  const openRoleModal = (user: UserItem) => {
    setSelectedUser(user);
    setSelectedRoleIds(roles.filter(r => user.roles.includes(r.name)).map(r => r.id));
    setRoleModalOpen(true);
  };

  const handleSaveRoles = async () => {
    if (!selectedUser) return;
    try {
      await client.put(`/users/${selectedUser.id}/roles`, { role_ids: selectedRoleIds });
      message.success('角色已更新');
      setRoleModalOpen(false);
      fetchUsers();
    } catch {
      message.error('角色更新失败');
    }
  };

  const columns = [
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '邮箱', dataIndex: 'email', key: 'email' },
    {
      title: '角色',
      dataIndex: 'roles',
      key: 'roles',
      render: (r: string[]) => r.length > 0
        ? r.map(name => <Tag key={name} color="blue">{name}</Tag>)
        : <Tag color="default">无</Tag>,
    },
    {
      title: '激活',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (_: boolean, record: UserItem) => (
        <Switch checked={record.is_active} onChange={() => handleToggleActive(record)} />
      ),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: UserItem) => (
        <Space>
          <Button size="small" onClick={() => openRoleModal(record)}>角色</Button>
          <Popconfirm title="确定删除此用户？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>用户管理</h3>
        <Button icon={<ReloadOutlined />} onClick={fetchUsers}>刷新</Button>
      </div>
      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title={`分配角色 — ${selectedUser?.username}`}
        open={roleModalOpen}
        onOk={handleSaveRoles}
        onCancel={() => setRoleModalOpen(false)}
      >
        <Select
          mode="multiple"
          style={{ width: '100%' }}
          placeholder="选择角色"
          value={selectedRoleIds}
          onChange={setSelectedRoleIds}
          options={roles.map(r => ({ label: r.name, value: r.id }))}
        />
      </Modal>
    </div>
  );
}
