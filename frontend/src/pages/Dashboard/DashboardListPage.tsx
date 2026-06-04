/** Dashboard list page — CRUD */

import { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select, message, Popconfirm, Card,
  Row, Col, Statistic,
} from 'antd';
import {
  PlusOutlined, ReloadOutlined, EditOutlined, EyeOutlined,
  DashboardOutlined, ApiOutlined, SyncOutlined, BuildOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';

interface DashboardItem {
  id: string;
  name: string;
  description?: string;
  status: string;
  visibility: string;
  widget_count: number;
  created_at?: string;
  updated_at?: string;
}

interface DataSourceItem { id: string; name: string; }
interface SyncJobItem { id: string; name: string; }

export default function DashboardListPage() {
  const navigate = useNavigate();
  const [dashboards, setDashboards] = useState<DashboardItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ ds: 0, jobs: 0, widgets: 0 });
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<DashboardItem | null>(null);
  const [form] = Form.useForm();

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [dashRes, dsRes, jobRes] = await Promise.all([
        client.get('/dashboards', { params: { page_size: 100 } }),
        client.get('/data-sources', { params: { page_size: 1 } }),
        client.get('/sync-jobs', { params: { page_size: 1 } }),
      ]);
      setDashboards(dashRes.data.items);
      const widgetTotal = dashRes.data.items.reduce((s: number, d: DashboardItem) => s + d.widget_count, 0);
      setStats({ ds: dsRes.data.total, jobs: jobRes.data.total, widgets: widgetTotal });
    } catch { /* ignore */ }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editing) {
        await client.patch(`/dashboards/${editing.id}`, values);
        message.success('更新成功');
      } else {
        await client.post('/dashboards', values);
        message.success('创建成功');
      }
      setModalOpen(false); form.resetFields(); setEditing(null);
      fetchAll();
    } catch (e: any) { if (e?.errorFields) return; message.error('操作失败'); }
  };

  const handleDelete = async (id: string) => {
    try { await client.delete(`/dashboards/${id}`); message.success('删除成功'); fetchAll(); }
    catch { message.error('删除失败'); }
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'desc', ellipsis: true },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (s: string) => {
        const colors: Record<string, string> = { draft: 'default', published: 'green', archived: 'red' };
        const labels: Record<string, string> = { draft: '草稿', published: '已发布', archived: '已归档' };
        return <Tag color={colors[s] || 'default'}>{labels[s] || s}</Tag>;
      },
    },
    {
      title: '可见性', dataIndex: 'visibility', key: 'visibility', width: 100,
      render: (v: string) => {
        const labels: Record<string, string> = { private: '私有', public: '公开' };
        return <Tag color={v === 'public' ? 'blue' : 'default'}>{labels[v] || v}</Tag>;
      },
    },
    { title: '组件数', dataIndex: 'widget_count', key: 'widgets', width: 80 },
    {
      title: '操作', key: 'actions', width: 240,
      render: (_: unknown, record: DashboardItem) => (
        <Space>
          <Button size="small" icon={<BuildOutlined />} type="primary"
            onClick={() => navigate(`/dashboards/${record.id}/build`)}>
            构建
          </Button>
          <Button size="small" icon={<EyeOutlined />}
            onClick={() => navigate(`/dashboards/${record.id}/preview`)}>
            预览
          </Button>
          <Button size="small" icon={<EditOutlined />} onClick={() => {
            setEditing(record); form.setFieldsValue(record); setModalOpen(true);
          }}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card><Statistic title="仪表盘" value={dashboards.length} prefix={<DashboardOutlined />} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="数据源" value={stats.ds} prefix={<ApiOutlined />} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="同步任务" value={stats.jobs} prefix={<SyncOutlined />} /></Card>
        </Col>
      </Row>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>仪表盘</h3>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchAll}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => {
            setEditing(null); form.resetFields();
            form.setFieldsValue({ visibility: 'private' });
            setModalOpen(true);
          }}>新建仪表盘</Button>
        </Space>
      </div>

      <Table columns={columns} dataSource={dashboards} rowKey="id" loading={loading}
        pagination={{ pageSize: 20 }} size="middle" />

      <Modal title={editing ? '编辑仪表盘' : '新建仪表盘'}
        open={modalOpen} onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields(); }}
        width={500} destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Space size="middle">
            <Form.Item name="visibility" label="可见性">
              <Select style={{ width: 120 }}>
                <Select.Option value="private">私有</Select.Option>
                <Select.Option value="public">公开</Select.Option>
              </Select>
            </Form.Item>
            {editing && (
              <Form.Item name="status" label="状态">
                <Select style={{ width: 130 }}>
                  <Select.Option value="draft">草稿</Select.Option>
                  <Select.Option value="published">已发布</Select.Option>
                  <Select.Option value="archived">已归档</Select.Option>
                </Select>
              </Form.Item>
            )}
          </Space>
        </Form>
      </Modal>
    </div>
  );
}
