/** Role & permission management page */

import { useState, useEffect } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, message, Popconfirm, Select, Card,
} from 'antd';
import { PlusOutlined, ReloadOutlined, SafetyOutlined } from '@ant-design/icons';
import client from '../../api/client';

interface PermissionItem {
  id: string;
  name: string;
  resource: string;
  action: string;
}

interface RoleItem {
  id: string;
  name: string;
  description?: string;
  permissions: PermissionItem[];
  user_count: number;
}

export default function RoleListPage() {
  const [roles, setRoles] = useState<RoleItem[]>([]);
  const [permissions, setPermissions] = useState<PermissionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [permModalOpen, setPermModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<RoleItem | null>(null);
  const [selectedPermIds, setSelectedPermIds] = useState<string[]>([]);
  const [form] = Form.useForm();

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const { data } = await client.get('/roles');
      setRoles(data);
    } catch {
      message.error('加载角色失败');
    }
    setLoading(false);
  };

  const fetchPermissions = async () => {
    try {
      const { data } = await client.get('/roles/permissions/all');
      setPermissions(data);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchRoles(); fetchPermissions(); }, []);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await client.post('/roles', values);
      message.success('角色已创建');
      setEditModalOpen(false);
      form.resetFields();
      fetchRoles();
    } catch {
      message.error('角色创建失败');
    }
  };

  const handleDelete = async (roleId: string) => {
    try {
      await client.delete(`/roles/${roleId}`);
      message.success('角色已删除');
      fetchRoles();
    } catch {
      message.error('角色删除失败');
    }
  };

  const openPermModal = (role: RoleItem) => {
    setEditingRole(role);
    setSelectedPermIds(role.permissions.map(p => p.id));
    setPermModalOpen(true);
  };

  const handleSavePerms = async () => {
    if (!editingRole) return;
    try {
      await client.put(`/roles/${editingRole.id}/permissions`, selectedPermIds);
      message.success('权限已更新');
      setPermModalOpen(false);
      fetchRoles();
    } catch {
      message.error('权限更新失败');
    }
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name', render: (n: string) => <Tag color="purple">{n}</Tag> },
    { title: '描述', dataIndex: 'description', key: 'description' },
    {
      title: '权限',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (perms: PermissionItem[]) =>
        perms.map(p => <Tag key={p.id}>{p.name}</Tag>),
    },
    { title: '用户', dataIndex: 'user_count', key: 'user_count' },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: RoleItem) => (
        <Space>
          <Button size="small" icon={<SafetyOutlined />} onClick={() => openPermModal(record)}>
            权限
          </Button>
          <Popconfirm title="确定删除此角色？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>角色管理</h3>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => { fetchRoles(); fetchPermissions(); }}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setEditModalOpen(true)}>
            新建角色
          </Button>
        </Space>
      </div>

      <Card size="small" title="权限参考" style={{ marginBottom: 16 }}>
        {permissions.map(p => (
          <Tag key={p.id} color="geekblue" style={{ marginBottom: 4 }}>
            {p.name} ({p.resource}:{p.action})
          </Tag>
        ))}
      </Card>

      <Table columns={columns} dataSource={roles} rowKey="id" loading={loading} />

      <Modal
        title="新建角色"
        open={editModalOpen}
        onOk={handleCreate}
        onCancel={() => { setEditModalOpen(false); form.resetFields(); }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`分配权限 — ${editingRole?.name}`}
        open={permModalOpen}
        onOk={handleSavePerms}
        onCancel={() => setPermModalOpen(false)}
        width={600}
      >
        <Select
          mode="multiple"
          style={{ width: '100%' }}
          placeholder="选择权限"
          value={selectedPermIds}
          onChange={setSelectedPermIds}
          options={permissions.map(p => ({
            label: `${p.name} (${p.resource}:${p.action})`,
            value: p.id,
          }))}
        />
      </Modal>
    </div>
  );
}
