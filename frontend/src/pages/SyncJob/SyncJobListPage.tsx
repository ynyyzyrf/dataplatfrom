/** Sync Job list page — full CRUD + execute */

import { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select, Switch,
  InputNumber, message, Popconfirm,
} from 'antd';
import {
  PlusOutlined, ReloadOutlined, EditOutlined, PlayCircleOutlined, HistoryOutlined,
} from '@ant-design/icons';
import client from '../../api/client';

interface SyncJobItem {
  id: string;
  data_source_id: string;
  name: string;
  schedule_type: string;
  schedule_config: Record<string, any>;
  sync_mode: string;
  write_mode: string;
  is_enabled: boolean;
  last_run_status?: string;
  run_count: number;
  created_at?: string;
}

interface DataSourceItem {
  id: string;
  name: string;
}

interface JobRun {
  id: string;
  sync_job_id: string;
  status: string;
  started_at: string;
  finished_at?: string;
  fetched_count: number;
  inserted_count: number;
  failed_count: number;
  error_message?: string;
}

export default function SyncJobListPage() {
  const [jobs, setJobs] = useState<SyncJobItem[]>([]);
  const [dataSources, setDataSources] = useState<DataSourceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<SyncJobItem | null>(null);
  const [runsModalOpen, setRunsModalOpen] = useState(false);
  const [runs, setRuns] = useState<JobRun[]>([]);
  const [selectedJob, setSelectedJob] = useState<SyncJobItem | null>(null);
  const [form] = Form.useForm();

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await client.get('/sync-jobs', { params: { page_size: 100 } });
      setJobs(data.items);
    } catch { message.error('加载同步任务失败'); }
    setLoading(false);
  }, []);

  const fetchDataSources = useCallback(async () => {
    try {
      const { data } = await client.get('/data-sources', { params: { page_size: 100 } });
      setDataSources(data.items);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchJobs(); fetchDataSources(); }, [fetchJobs, fetchDataSources]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editing) {
        await client.patch(`/sync-jobs/${editing.id}`, values);
        message.success('更新成功');
      } else {
        await client.post('/sync-jobs', values);
        message.success('创建成功');
      }
      setModalOpen(false); form.resetFields(); setEditing(null);
      fetchJobs();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(editing ? '更新失败' : '创建失败');
    }
  };

  const handleDelete = async (id: string) => {
    try { await client.delete(`/sync-jobs/${id}`); message.success('删除成功'); fetchJobs(); }
    catch { message.error('删除失败'); }
  };

  const handleExecute = async (id: string) => {
    try {
      const { data } = await client.post(`/sync-jobs/${id}/execute`);
      message.success(`同步${data.status}：获取${data.fetched_count}条，写入${data.inserted_count}条`);
      fetchJobs();
    } catch { message.error('执行失败'); }
  };

  const showRuns = async (job: SyncJobItem) => {
    setSelectedJob(job);
    try {
      const { data } = await client.get(`/sync-jobs/${job.id}/runs`, { params: { page_size: 50 } });
      setRuns(data.items);
    } catch { message.error('加载运行历史失败'); }
    setRunsModalOpen(true);
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    {
      title: '启用', dataIndex: 'is_enabled', key: 'enabled', width: 80,
      render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? '开' : '关'}</Tag>,
    },
    {
      title: '调度', dataIndex: 'schedule_type', key: 'schedule', width: 100,
      render: (t: string) => t === 'cron' ? <Tag color="purple">定时</Tag> : <Tag color="blue">间隔</Tag>,
    },
    { title: '模式', dataIndex: 'sync_mode', key: 'mode', width: 80 },
    {
      title: '上次运行', dataIndex: 'last_run_status', key: 'last_run', width: 100,
      render: (s: string | undefined) => {
        if (!s) return <Tag color="default">无</Tag>;
        const color = s === 'completed' ? 'success' : s === 'failed' ? 'error' : 'processing';
        return <Tag color={color}>{s}</Tag>;
      },
    },
    { title: '运行次数', dataIndex: 'run_count', key: 'runs', width: 60 },
    {
      title: '操作', key: 'actions', width: 260,
      render: (_: unknown, record: SyncJobItem) => (
        <Space>
          <Button size="small" icon={<PlayCircleOutlined />} onClick={() => handleExecute(record.id)}>执行</Button>
          <Button size="small" icon={<HistoryOutlined />} onClick={() => showRuns(record)}>历史</Button>
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

  const runColumns = [
    { title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (s: string) => {
        const colors: Record<string, string> = { completed: 'green', failed: 'red', running: 'blue' };
        return <Tag color={colors[s] || 'default'}>{s}</Tag>;
      },
    },
    { title: '开始时间', dataIndex: 'started_at', key: 'started', width: 180,
      render: (v: string) => v ? new Date(v).toLocaleString() : '-',
    },
    { title: '获取', dataIndex: 'fetched_count', key: 'fetched', width: 80 },
    { title: '写入', dataIndex: 'inserted_count', key: 'inserted', width: 80 },
    { title: '失败', dataIndex: 'failed_count', key: 'failed', width: 80 },
    { title: '错误', dataIndex: 'error_message', key: 'error', ellipsis: true },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>同步任务</h3>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => { fetchJobs(); fetchDataSources(); }}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => {
            setEditing(null); form.resetFields();
            form.setFieldsValue({ schedule_type: 'interval', sync_mode: 'full', write_mode: 'upsert', is_enabled: false, timeout_seconds: 300, retry_count: 3 });
            setModalOpen(true);
          }}>新建任务</Button>
        </Space>
      </div>

      <Table columns={columns} dataSource={jobs} rowKey="id" loading={loading} pagination={{ pageSize: 20 }} size="middle" />

      <Modal title={editing ? '编辑同步任务' : '新建同步任务'} open={modalOpen}
        onOk={handleSave} onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields(); }}
        width={600} destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="data_source_id" label="数据源" rules={[{ required: true }]}>
            <Select options={dataSources.map(d => ({ label: d.name, value: d.id }))} />
          </Form.Item>
          <Space size="middle">
            <Form.Item name="schedule_type" label="调度类型">
              <Select style={{ width: 120 }}>
                <Select.Option value="interval">间隔</Select.Option>
                <Select.Option value="cron">定时</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="sync_mode" label="同步模式">
              <Select style={{ width: 130 }}>
                <Select.Option value="full">全量</Select.Option>
                <Select.Option value="incremental">增量</Select.Option>
                <Select.Option value="paged">分页</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="write_mode" label="写入模式">
              <Select style={{ width: 120 }}>
                <Select.Option value="insert">插入</Select.Option>
                <Select.Option value="upsert">更新插入</Select.Option>
                <Select.Option value="replace">替换</Select.Option>
                <Select.Option value="append">追加</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="is_enabled" label="启用" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Space>
          <Space size="middle">
            <Form.Item name="timeout_seconds" label="超时时间（秒）">
              <InputNumber min={1} max={3600} />
            </Form.Item>
            <Form.Item name="retry_count" label="重试次数">
              <InputNumber min={0} max={10} />
            </Form.Item>
          </Space>
        </Form>
      </Modal>

      <Modal title={`运行历史 — ${selectedJob?.name || ''}`} open={runsModalOpen}
        onCancel={() => setRunsModalOpen(false)} footer={null} width={800}
      >
        <Table columns={runColumns} dataSource={runs} rowKey="id" pagination={{ pageSize: 10 }}
          size="small" />
      </Modal>
    </div>
  );
}
