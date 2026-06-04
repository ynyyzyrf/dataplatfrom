/** Monitoring dashboard page */

import { useState, useEffect, useCallback } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Spin, Space, Button, Progress } from 'antd';
import {
  ApiOutlined, SyncOutlined, DashboardOutlined,
  AlertOutlined, CheckCircleOutlined, CloseCircleOutlined,
  ReloadOutlined, ClockCircleOutlined,
} from '@ant-design/icons';
import client from '../../api/client';

interface JobRunStats {
  sync_job_id: string;
  sync_job_name: string;
  data_source_name?: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  running_runs: number;
  success_rate: number;
  last_run_status?: string;
  last_run_at?: string;
  avg_duration_ms: number;
  total_fetched: number;
  total_inserted: number;
}

interface MonitoringData {
  total_data_sources: number;
  total_sync_jobs: number;
  active_sync_jobs: number;
  total_dashboards: number;
  total_runs_today: number;
  failed_runs_today: number;
  active_alerts: number;
  job_stats: JobRunStats[];
}

export default function MonitoringPage() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await client.get('/monitoring/overview');
      setData(resp.data);
    } catch { /* ignore */ }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>平台监控</h3>
        <Button icon={<ReloadOutlined />} onClick={fetchData}>刷新</Button>
      </div>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card><Statistic title="数据源" value={data?.total_data_sources || 0} prefix={<ApiOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="同步任务（活跃）" value={data?.active_sync_jobs || 0}
            suffix={data ? `/ ${data.total_sync_jobs}` : ''} prefix={<SyncOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="仪表盘" value={data?.total_dashboards || 0} prefix={<DashboardOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="活跃告警" value={data?.active_alerts || 0}
            prefix={<AlertOutlined />} valueStyle={{ color: (data?.active_alerts || 0) > 0 ? '#cf1322' : undefined }} /></Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="今日活动" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Statistic title="运行总计" value={data?.total_runs_today || 0}
                  prefix={<ClockCircleOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="失败次数" value={data?.failed_runs_today || 0}
                  prefix={<CloseCircleOutlined />}
                  valueStyle={{ color: (data?.failed_runs_today || 0) > 0 ? '#cf1322' : undefined }} />
              </Col>
            </Row>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="整体健康度" size="small">
            <Progress
              type="circle"
              percent={data ? Math.round((data.total_runs_today - data.failed_runs_today) / Math.max(data.total_runs_today, 1) * 100) : 100}
              status={data && data.failed_runs_today > 0 ? 'exception' : 'success'}
              size={80}
            />
          </Card>
        </Col>
      </Row>

      <Card title="同步任务性能" style={{ marginTop: 16 }}>
        <Table
          dataSource={data?.job_stats || []}
          rowKey="sync_job_id"
          size="middle"
          pagination={{ pageSize: 20 }}
          columns={[
            { title: '任务', dataIndex: 'sync_job_name', key: 'job' },
            { title: '数据源', dataIndex: 'data_source_name', key: 'ds', ellipsis: true },
            {
              title: '成功率', dataIndex: 'success_rate', key: 'rate', width: 140,
              render: (r: number) => (
                <Progress percent={r} size="small"
                  status={r < 80 ? 'exception' : r < 95 ? 'active' : 'success'}
                  format={(p) => `${p?.toFixed(1)}%`} />
              ),
            },
            { title: '总计', dataIndex: 'total_runs', key: 'total', width: 70 },
            {
              title: '成功', dataIndex: 'successful_runs', key: 'success', width: 80,
              render: (v: number) => <Tag color="green">{v}</Tag>,
            },
            {
              title: '失败', dataIndex: 'failed_runs', key: 'failed', width: 70,
              render: (v: number) => <Tag color="red">{v}</Tag>,
            },
            {
              title: '运行中', dataIndex: 'running_runs', key: 'running', width: 80,
              render: (v: number) => v > 0 ? <Tag color="blue">{v}</Tag> : null,
            },
            {
              title: '平均耗时', dataIndex: 'avg_duration_ms', key: 'duration', width: 110,
              render: (v: number) => `${(v / 1000).toFixed(2)}s`,
            },
            { title: '已获取', dataIndex: 'total_fetched', key: 'fetched', width: 80 },
            { title: '已写入', dataIndex: 'total_inserted', key: 'inserted', width: 80 },
            {
              title: '最近状态', dataIndex: 'last_run_status', key: 'last_status', width: 100,
              render: (s: string) => s ? (
                <Tag color={s === 'success' ? 'green' : s === 'failed' ? 'red' : 'blue'}>{s}</Tag>
              ) : '-',
            },
            {
              title: '最近运行', dataIndex: 'last_run_at', key: 'last_run', width: 160,
              render: (v: string) => v ? new Date(v).toLocaleString() : '-',
            },
          ]}
        />
      </Card>
    </div>
  );
}
