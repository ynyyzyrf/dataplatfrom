/** Data Source list page — full CRUD */

import { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select, InputNumber,
  message, Popconfirm,
} from 'antd';
import { PlusOutlined, ReloadOutlined, EditOutlined } from '@ant-design/icons';
import client from '../../api/client';

interface DataSourceItem {
  id: string;
  name: string;
  description?: string;
  group?: string;
  request_method: string;
  request_url: string;
  auth_type: string;
  auth_config?: Record<string, any>;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export default function DataSourceListPage() {
  const [sources, setSources] = useState<DataSourceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<DataSourceItem | null>(null);
  const [form] = Form.useForm();
  const authType = Form.useWatch('auth_type', form);

  const fetchSources = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await client.get('/data-sources', { params: { page_size: 100 } });
      setSources(data.items);
    } catch {
      message.error('加载数据源失败');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchSources(); }, [fetchSources]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      // Build auth_config from form fields
      if (values.auth_type === 'bearer_token') {
        values.auth_config = { token: values._bearer_token || '' };
      } else if (values.auth_type === 'api_key') {
        values.auth_config = {
          header_name: values._api_key_header || '',
          api_key: values._api_key_value || '',
        };
      } else {
        values.auth_config = null;
      }
      // Clean up temp fields
      delete values._bearer_token;
      delete values._api_key_header;
      delete values._api_key_value;

      if (editing) {
        await client.patch(`/data-sources/${editing.id}`, values);
        message.success('更新成功');
      } else {
        await client.post('/data-sources', values);
        message.success('创建成功');
      }
      setModalOpen(false);
      form.resetFields();
      setEditing(null);
      fetchSources();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(editing ? '更新失败' : '创建失败');
    }
  };

  const handleEdit = (record: DataSourceItem) => {
    setEditing(record);
    const fields: any = { ...record };
    // Populate auth config fields from record
    if (record.auth_config) {
      if (record.auth_type === 'bearer_token') {
        fields._bearer_token = record.auth_config.token || '';
      } else if (record.auth_type === 'api_key') {
        fields._api_key_header = record.auth_config.header_name || '';
        fields._api_key_value = record.auth_config.api_key || '';
      }
    }
    form.setFieldsValue(fields);
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await client.delete(`/data-sources/${id}`);
      message.success('删除成功');
      fetchSources();
    } catch {
      message.error('删除失败');
    }
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: '请求方法', dataIndex: 'request_method', key: 'method', width: 80,
      render: (m: string) => <Tag color={m === 'GET' ? 'green' : 'blue'}>{m}</Tag>,
    },
    { title: '请求地址', dataIndex: 'request_url', key: 'url', ellipsis: true },
    { title: '认证', dataIndex: 'auth_type', key: 'auth', width: 120,
      render: (a: string) => {
        const colors: Record<string, string> = { none: 'default', bearer_token: 'orange', api_key: 'purple' };
        const labels: Record<string, string> = { none: '无', bearer_token: 'Bearer 令牌', api_key: 'API 密钥' };
        return <Tag color={colors[a] || 'default'}>{labels[a] || a}</Tag>;
      },
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 90,
      render: (s: string) => <Tag color={s === 'active' ? 'success' : 'error'}>{s}</Tag>,
    },
    {
      title: '操作', key: 'actions', width: 140,
      render: (_: unknown, record: DataSourceItem) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>数据源</h3>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchSources}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => {
            setEditing(null);
            form.resetFields();
            form.setFieldsValue({ request_method: 'GET', auth_type: 'none', timeout_seconds: 30, retry_count: 3 });
            setModalOpen(true);
          }}>
            新建数据源
          </Button>
        </Space>
      </div>

      <Table columns={columns} dataSource={sources} rowKey="id" loading={loading}
        pagination={{ pageSize: 20 }} size="middle" />

      <Modal
        title={editing ? '编辑数据源' : '新建数据源'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields(); }}
        width={640}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input placeholder="例如：GitHub API" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="group" label="分组">
            <Input placeholder="例如：外部API" />
          </Form.Item>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="request_method" label="请求方法" rules={[{ required: true }]}>
              <Select style={{ width: 120 }}>
                <Select.Option value="GET">GET</Select.Option>
                <Select.Option value="POST">POST</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="auth_type" label="认证方式" rules={[{ required: true }]}>
              <Select style={{ width: 160 }}>
                <Select.Option value="none">无</Select.Option>
                <Select.Option value="bearer_token">Bearer Token</Select.Option>
                <Select.Option value="api_key">API Key</Select.Option>
              </Select>
            </Form.Item>
          </Space>
          {authType === 'bearer_token' && (
            <Form.Item name="_bearer_token" label="Bearer Token" rules={[{ required: true, message: '请输入 Bearer Token' }]}>
              <Input.Password placeholder="輸入 Bearer Token" />
            </Form.Item>
          )}
          {authType === 'api_key' && (
            <>
              <Form.Item name="_api_key_header" label="API Key 頭部名稱" rules={[{ required: true, message: '請輸入 Header 名稱' }]}>
                <Input placeholder="例如：X-API-Key" />
              </Form.Item>
              <Form.Item name="_api_key_value" label="API Key 值" rules={[{ required: true, message: '請輸入 API Key' }]}>
                <Input.Password placeholder="輸入 API Key 值" />
              </Form.Item>
            </>
          )}
          <Form.Item name="request_url" label="请求地址" rules={[{ required: true, type: 'url' }]}>
            <Input placeholder="https://api.example.com/data" />
          </Form.Item>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="timeout_seconds" label="超时时间（秒）">
              <InputNumber min={1} max={300} />
            </Form.Item>
            <Form.Item name="retry_count" label="重试次数">
              <InputNumber min={0} max={10} />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  );
}
