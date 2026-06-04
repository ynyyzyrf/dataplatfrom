/** Alert Rule management page */

import { useState, useEffect, useCallback } from 'react';
import { Table, Button, Space, Tag, Modal, Form, Input, Select, InputNumber, Switch, message, Popconfirm } from 'antd';
import { PlusOutlined, ReloadOutlined, EditOutlined } from '@ant-design/icons';
import client from '../../api/client';

interface AlertRule {
  id: string;
  name: string;
  rule_type: string;
  target_type: string;
  target_id?: string;
  threshold: number;
  window_minutes: number;
  channels: string[];
  is_active: boolean;
  created_at?: string;
}

export default function AlertRuleListPage() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<AlertRule | null>(null);
  const [form] = Form.useForm();

  const fetchRules = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await client.get('/alert-rules', { params: { page_size: 100 } });
      setRules(data.items);
    } catch { message.error('加载告警规则失败'); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchRules(); }, [fetchRules]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editing) {
        await client.put(`/alert-rules/${editing.id}`, values);
        message.success('更新成功');
      } else {
        await client.post('/alert-rules', values);
        message.success('创建成功');
      }
      setModalOpen(false); form.resetFields(); setEditing(null);
      fetchRules();
    } catch (e: any) { if (e?.errorFields) return; message.error('操作失败'); }
  };

  const handleDelete = async (id: string) => {
    try { await client.delete(`/alert-rules/${id}`); message.success('删除成功'); fetchRules(); }
    catch { message.error('删除失败'); }
  };

  const ruleTypeColors: Record<string, string> = {
    consecutive_failures: 'red',
    http_error: 'orange',
    timeout: 'gold',
    zero_data: 'purple',
    token_expiry: 'blue',
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    {
      title: '规则类型', dataIndex: 'rule_type', key: 'rule_type', width: 160,
      render: (t: string) => <Tag color={ruleTypeColors[t] || 'default'}>{t.replace('_', ' ')}</Tag>,
    },
    { title: '目标', dataIndex: 'target_type', key: 'target', width: 100 },
    { title: '阈值', dataIndex: 'threshold', key: 'threshold', width: 90 },
    { title: '窗口（分钟）', dataIndex: 'window_minutes', key: 'window', width: 110 },
    {
      title: '渠道', dataIndex: 'channels', key: 'channels', width: 150,
      render: (ch: string[]) => ch?.map((c) => <Tag key={c}>{c}</Tag>),
    },
    {
      title: '状态', dataIndex: 'is_active', key: 'active', width: 70,
      render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? '开' : '关'}</Tag>,
    },
    {
      title: '操作', key: 'actions', width: 120,
      render: (_: unknown, r: AlertRule) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => {
            setEditing(r); form.setFieldsValue(r); setModalOpen(true);
          }} />
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(r.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>告警规则</h3>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchRules}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => {
            setEditing(null);
            form.resetFields();
            form.setFieldsValue({ rule_type: 'http_error', target_type: 'sync_job', threshold: 1, window_minutes: 15, channels: ['in_app'], is_active: true });
            setModalOpen(true);
          }}>新建规则</Button>
        </Space>
      </div>

      <Table columns={columns} dataSource={rules} rowKey="id" loading={loading}
        pagination={{ pageSize: 20 }} size="middle" />

      <Modal title={editing ? '编辑告警规则' : '新建告警规则'}
        open={modalOpen} onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields(); }}
        width={560} destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="规则名称" rules={[{ required: true }]}>
            <Input placeholder="例如：连续失败告警" />
          </Form.Item>
          <Form.Item name="rule_type" label="规则类型" rules={[{ required: true }]}>
            <Select options={[
              { label: '连续失败', value: 'consecutive_failures' },
              { label: 'HTTP错误', value: 'http_error' },
              { label: '超时', value: 'timeout' },
              { label: '零数据', value: 'zero_data' },
              { label: '令牌过期', value: 'token_expiry' },
            ]} />
          </Form.Item>
          <Form.Item name="target_type" label="目标类型" rules={[{ required: true }]}>
            <Select options={[
              { label: '同步任务', value: 'sync_job' },
              { label: '数据源', value: 'data_source' },
            ]} />
          </Form.Item>
          <Form.Item name="target_id" label="目标ID（可选）">
            <Input placeholder="指定目标ID或留空适用于所有" />
          </Form.Item>
          <Space size="middle">
            <Form.Item name="threshold" label="阈值" rules={[{ required: true }]}>
              <InputNumber min={1} max={100} />
            </Form.Item>
            <Form.Item name="window_minutes" label="时间窗口（分钟）" rules={[{ required: true }]}>
              <InputNumber min={1} max={1440} />
            </Form.Item>
          </Space>
          <Form.Item name="channels" label="通知渠道">
            <Select mode="multiple" options={[
              { label: '应用内', value: 'in_app' },
              { label: '邮件', value: 'email' },
              { label: 'Slack', value: 'slack' },
              { label: 'Webhook', value: 'webhook' },
            ]} />
          </Form.Item>
          <Form.Item name="is_active" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
