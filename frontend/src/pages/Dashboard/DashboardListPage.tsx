/** Dashboard list page — card grid with search, filter & stats */

import { useState, useEffect, useCallback } from 'react';
import {
  Card, Button, Space, Tag, Modal, Form, Input, Select, message, Popconfirm,
  Row, Col, Statistic, InputNumber, theme,
} from 'antd';
import {
  PlusOutlined, ReloadOutlined, EditOutlined, EyeOutlined, DeleteOutlined,
  DashboardOutlined, ApiOutlined, SyncOutlined, BuildOutlined,
  SearchOutlined, FilterOutlined, UnorderedListOutlined, AppstoreOutlined,
  ClockCircleOutlined, UserOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';

const { TextArea } = Input;

// -- Types ---------------------------------------------------------------

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

// -- Constants -----------------------------------------------------------

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  draft: { color: 'default', label: '草稿' },
  published: { color: 'success', label: '已发布' },
  archived: { color: 'warning', label: '已归档' },
};

const VISIBILITY_MAP: Record<string, { icon: React.ReactNode; color: string }> = {
  private: { icon: <UserOutlined />, color: 'default', label: '私有' },
  public: { icon: <DashboardOutlined />, color: 'blue', label: '公开' },
};

const EMPTY_STATE = {
  dashboards: [] as DashboardItem[],
  total: 0,
};

// -- Helpers -------------------------------------------------------------

function formatDate(dateStr?: string): string {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

// -- Component -----------------------------------------------------------

export default function DashboardListPage() {
  const navigate = useNavigate();
  const { token } = theme.useToken();

  const [dashboards, setDashboards] = useState<DashboardItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ ds: 0, jobs: 0, widgets: 0 });
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<DashboardItem | null>(null);
  const [form] = Form.useForm();

  // Search & filter
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'card' | 'table'>('card');

  // -- Data fetching ---------------------------------------------------

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

  // -- Handlers --------------------------------------------------------

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
      setModalOpen(false);
      form.resetFields();
      setEditing(null);
      fetchAll();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error('操作失败');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await client.delete(`/dashboards/${id}`);
      message.success('删除成功');
      fetchAll();
    } catch {
      message.error('删除失败');
    }
  };

  // -- Filtered data ---------------------------------------------------

  const filtered = dashboards.filter((d) => {
    if (search && !d.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (statusFilter !== 'all' && d.status !== statusFilter) return false;
    return true;
  });

  // -- Render ----------------------------------------------------------

  return (
    <div>
      {/* Stats Banner */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card variant="borderless" style={{ background: 'linear-gradient(135deg, #667eea20, #764ba220)' }}>
            <Statistic
              title="仪表盘总数"
              value={dashboards.length}
              prefix={<DashboardOutlined />}
              valueStyle={{ color: '#667eea' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card variant="borderless" style={{ background: 'linear-gradient(135deg, #f093fb20, #f5576c20)' }}>
            <Statistic
              title="组件总数"
              value={stats.widgets}
              prefix={<EditOutlined />}
              valueStyle={{ color: '#f5576c' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card variant="borderless" style={{ background: 'linear-gradient(135deg, #4facfe20, #00f2fe20)' }}>
            <Statistic
              title="已发布"
              value={dashboards.filter((d) => d.status === 'published').length}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#4facfe' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <Space>
          <Input
            placeholder="搜索仪表盘名称…"
            prefix={<SearchOutlined />}
            style={{ width: 260 }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 140 }}
            options={[
              { label: '全部状态', value: 'all' },
              { label: '草稿', value: 'draft' },
              { label: '已发布', value: 'published' },
              { label: '已归档', value: 'archived' },
            ]}
          />
        </Space>
        <Space>
          <Button.Group>
            <Button
              icon={<AppstoreOutlined />}
              type={viewMode === 'card' ? 'primary' : 'default'}
              onClick={() => setViewMode('card')}
            />
            <Button
              icon={<UnorderedListOutlined />}
              type={viewMode === 'table' ? 'primary' : 'default'}
              onClick={() => setViewMode('table')}
            />
          </Button.Group>
          <Button icon={<ReloadOutlined />} onClick={fetchAll} loading={loading}>刷新</Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditing(null);
              form.resetFields();
              form.setFieldsValue({ visibility: 'private' });
              setModalOpen(true);
            }}
          >
            新建仪表盘
          </Button>
        </Space>
      </div>

      {/* Card Grid View */}
      {viewMode === 'card' && (
        <div>
          {filtered.length === 0 ? (
            <Card variant="borderless" style={{ textAlign: 'center', padding: '60px 0' }}>
              <DashboardOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
              <p style={{ color: '#999', marginTop: 12 }}>
                {search || statusFilter !== 'all' ? '没有找到匹配的仪表盘' : '还没有仪表盘，点击"新建仪表盘"开始'}
              </p>
            </Card>
          ) : (
            <Row gutter={[16, 16]}>
              {filtered.map((d) => (
                <Col xs={24} sm={12} md={8} lg={6} key={d.id}>
                  <DashboardCard
                    dashboard={d}
                    onBuild={() => navigate(`/dashboards/${d.id}/build`)}
                    onPreview={() => navigate(`/dashboards/${d.id}/preview`)}
                    onEdit={() => { setEditing(d); form.setFieldsValue(d); setModalOpen(true); }}
                    onDelete={() => handleDelete(d.id)}
                  />
                </Col>
              ))}
            </Row>
          )}
        </div>
      )}

      {/* Table View */}
      {viewMode === 'table' && (
        <Table
          columns={[
            { title: '名称', dataIndex: 'name', key: 'name', ellipsis: true },
            { title: '描述', dataIndex: 'description', key: 'desc', ellipsis: true },
            {
              title: '状态', dataIndex: 'status', key: 'status', width: 100,
              render: (s: string) => {
                const { color, label } = STATUS_MAP[s] || { color: 'default', label: s };
                return <Tag color={color}>{label}</Tag>;
              },
            },
            {
              title: '可见性', dataIndex: 'visibility', key: 'visibility', width: 100,
              render: (v: string) => {
                const { color, icon, label } = VISIBILITY_MAP[v] || { color: 'default', icon: null, label: v };
                return <Tag color={color}>{icon && <span style={{ marginRight: 4 }}>{icon}</span>}{label}</Tag>;
              },
            },
            { title: '组件数', dataIndex: 'widget_count', key: 'widgets', width: 80 },
            { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 140, render: formatDate },
            {
              title: '操作', key: 'actions', width: 240, fixed: 'right' as const,
              render: (_: unknown, record: DashboardItem) => (
                <Space size="small">
                  <Button size="small" icon={<BuildOutlined />} type="primary" onClick={() => navigate(`/dashboards/${record.id}/build`)}>
                    构建
                  </Button>
                  <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/dashboards/${record.id}/preview`)}>
                    预览
                  </Button>
                  <Button size="small" icon={<EditOutlined />} onClick={() => { setEditing(record); form.setFieldsValue(record); setModalOpen(true); }}>
                    编辑
                  </Button>
                  <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
                    <Button size="small" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
          dataSource={filtered}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          scroll={{ x: 800 }}
          size="middle"
        />
      )}

      {/* Modal */}
      <Modal
        title={editing ? '编辑仪表盘' : '新建仪表盘'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields(); }}
        width={500}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input placeholder="例如：销售数据看板" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="简要描述此仪表盘的用途" />
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

// -- Dashboard Card Sub-component --------------------------------------

function DashboardCard({
  dashboard,
  onBuild,
  onPreview,
  onEdit,
  onDelete,
}: {
  dashboard: DashboardItem;
  onBuild: () => void;
  onPreview: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const { color: statusColor, label: statusLabel } = STATUS_MAP[dashboard.status] || { color: 'default', label: dashboard.status };
  const { icon: visIcon, color: visColor, label: visLabel } = VISIBILITY_MAP[dashboard.visibility] || { color: 'default', icon: null, label: dashboard.visibility };

  return (
    <Card
      hoverable
      size="small"
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column' } }}
      extra={
        <Space size={4}>
          <Button size="small" type="text" icon={<EditOutlined />} onClick={(e) => { e.stopPropagation(); onEdit(); }} />
          <Popconfirm title="确定删除？" onConfirm={(e) => { e?.stopPropagation(); onDelete(); }}>
            <Button size="small" type="text" danger icon={<DeleteOutlined />} onClick={(e) => e.stopPropagation()} />
          </Popconfirm>
        </Space>
      }
      onClick={onEdit}
    >
      <div style={{ flex: 1, cursor: 'pointer' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <DashboardOutlined style={{ fontSize: 20, color: '#1677ff' }} />
          <span style={{ fontWeight: 600, fontSize: 15, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
            {dashboard.name}
          </span>
        </div>
        {dashboard.description && (
          <p style={{ color: '#888', fontSize: 12, margin: '0 0 10px 0', minHeight: 32, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
            {dashboard.description}
          </p>
        )}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 'auto' }}>
          <Tag color={statusColor}>{statusLabel}</Tag>
          <Tag color={visColor}>{visIcon && <span style={{ marginRight: 2 }}>{visIcon}</span>}{visLabel}</Tag>
          <Tag>{dashboard.widget_count} 组件</Tag>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
        <Button size="small" type="primary" style={{ flex: 1 }} icon={<BuildOutlined />} onClick={(e) => { e.stopPropagation(); onBuild(); }}>
          构建
        </Button>
        <Button size="small" icon={<EyeOutlined />} onClick={(e) => { e.stopPropagation(); onPreview(); }}>
          预览
        </Button>
      </div>
    </Card>
  );
}
