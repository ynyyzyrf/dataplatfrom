/** Data record browser — view fetched API data */

import { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, Tag, Select, DatePicker, message, Drawer, Typography,
  Row, Col, Card, Statistic, Descriptions,
} from 'antd';
import {
  ReloadOutlined, DatabaseOutlined, EyeOutlined, ApiOutlined,
} from '@ant-design/icons';
import client from '../../api/client';

const { Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;

interface DataRecord {
  id: string;
  data_source_id: string;
  data_source_name?: string;
  sync_job_run_id?: string;
  response_status?: number;
  fetched_at?: string;
  created_at?: string;
  payload_preview?: string;
}

interface DataRecordDetail extends DataRecord {
  raw_payload?: any;
}

interface DataSourceItem {
  id: string;
  name: string;
}

export default function DataRecordListPage() {
  const [records, setRecords] = useState<DataRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Filters
  const [dataSources, setDataSources] = useState<DataSourceItem[]>([]);
  const [filterDsId, setFilterDsId] = useState<string | undefined>();
  const [filterStatus, setFilterStatus] = useState<number | undefined>();
  const [filterDateRange, setFilterDateRange] = useState<[string, string] | null>(null);

  // Detail
  const [detail, setDetail] = useState<DataRecordDetail | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = { page, page_size: pageSize };
      if (filterDsId) params.data_source_id = filterDsId;
      if (filterStatus !== undefined) params.response_status = filterStatus;
      if (filterDateRange) {
        params.start_date = filterDateRange[0];
        params.end_date = filterDateRange[1];
      }
      const { data } = await client.get('/data-records', { params });
      setRecords(data.items);
      setTotal(data.total);
    } catch { message.error('加载数据记录失败'); }
    setLoading(false);
  }, [page, pageSize, filterDsId, filterStatus, filterDateRange]);

  const fetchDataSources = useCallback(async () => {
    try {
      const { data } = await client.get('/data-sources', { params: { page_size: 100 } });
      setDataSources(data.items);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchRecords(); fetchDataSources(); }, [fetchRecords, fetchDataSources]);

  const showDetail = async (recordId: string) => {
    try {
      const { data } = await client.get(`/data-records/${recordId}`);
      setDetail(data);
      setDrawerOpen(true);
    } catch { message.error('加载详情失败'); }
  };

  const toggleExpand = (recordId: string) => {
    setExpandedRows((prev) => {
      const next = new Set(prev);
      if (next.has(recordId)) next.delete(recordId);
      else next.add(recordId);
      return next;
    });
  };

  const formatJson = (obj: any): string => {
    try {
      return JSON.stringify(obj, null, 2);
    } catch { return String(obj); }
  };

  const columns = [
    {
      title: '数据源', dataIndex: 'data_source_name', key: 'ds', width: 160, ellipsis: true,
      render: (n: string) => n || '-',
    },
    {
      title: '状态码', dataIndex: 'response_status', key: 'status', width: 90,
      render: (s: number | undefined) => {
        if (s === undefined || s === null) return <Tag color="default">N/A</Tag>;
        const color = s >= 200 && s < 300 ? 'green' : s >= 400 && s < 500 ? 'orange' : s >= 500 ? 'red' : 'blue';
        return <Tag color={color}>{s}</Tag>;
      },
    },
    {
      title: '获取时间', dataIndex: 'fetched_at', key: 'fetched', width: 180,
      render: (v: string) => v ? new Date(v).toLocaleString() : '-',
    },
    {
      title: '数据预览', dataIndex: 'payload_preview', key: 'preview', ellipsis: true,
      render: (p: string) => (
        <Text code ellipsis style={{ maxWidth: 400, fontSize: 12 }}>
          {p || '-'}
        </Text>
      ),
    },
    {
      title: '操作', key: 'actions', width: 160,
      render: (_: unknown, record: DataRecord) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />} onClick={() => showDetail(record.id)}>
            详情
          </Button>
          <Button size="small" onClick={() => toggleExpand(record.id)}>
            {expandedRows.has(record.id) ? '收起' : '展开'}
          </Button>
        </Space>
      ),
    },
  ];

  const expandedRowRender = (record: DataRecord) => (
    <pre style={{
      maxHeight: 400, overflow: 'auto', background: '#f5f5f5',
      padding: 12, borderRadius: 4, fontSize: 12, lineHeight: 1.5, margin: 0,
    }}>
      {formatJson(record)}
    </pre>
  );

  const statusOptions = [
    { label: '全部', value: undefined },
    { label: '2xx 成功', value: 200 },
    { label: '4xx 客户端错误', value: 400 },
    { label: '5xx 服务端错误', value: 500 },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>
          <DatabaseOutlined style={{ marginRight: 8 }} />
          数据浏览
        </h3>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => { fetchRecords(); fetchDataSources(); }}>
            刷新
          </Button>
        </Space>
      </div>

      {/* Stats Row */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic title="记录总数" value={total} prefix={<DatabaseOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="数据源" value={dataSources.length} prefix={<ApiOutlined />} />
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap size="middle">
          <span style={{ fontWeight: 500 }}>数据源：</span>
          <Select
            style={{ width: 200 }}
            placeholder="全部数据源"
            allowClear
            value={filterDsId}
            onChange={(v) => { setFilterDsId(v); setPage(1); }}
            options={dataSources.map((ds) => ({ label: ds.name, value: ds.id }))}
          />
          <span style={{ fontWeight: 500 }}>状态码：</span>
          <Select
            style={{ width: 150 }}
            placeholder="全部状态"
            allowClear
            value={filterStatus}
            onChange={(v) => { setFilterStatus(v); setPage(1); }}
            options={[
              { label: '1xx 信息', value: 100 },
              { label: '2xx 成功', value: 200 },
              { label: '3xx 重定向', value: 300 },
              { label: '4xx 客户端错误', value: 400 },
              { label: '5xx 服务端错误', value: 500 },
            ]}
          />
          <span style={{ fontWeight: 500 }}>时间范围：</span>
          <RangePicker
            showTime
            onChange={(dates) => {
              if (dates && dates[0] && dates[1]) {
                setFilterDateRange([dates[0].toISOString(), dates[1].toISOString()]);
              } else {
                setFilterDateRange(null);
              }
              setPage(1);
            }}
          />
        </Space>
      </Card>

      {/* Table */}
      <Table
        columns={columns}
        dataSource={records}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize,
          total,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条记录`,
          onChange: (p, ps) => { setPage(p); setPageSize(ps); },
        }}
        size="middle"
        expandable={{
          expandedRowRender: (record) => (
            <pre style={{
              maxHeight: 400, overflow: 'auto', background: '#f5f5f5',
              padding: 12, borderRadius: 4, fontSize: 12, lineHeight: 1.5, margin: 0,
            }}>
              {formatJson(records.find(r => r.id === record.id))}
            </pre>
          ),
          rowExpandable: () => true,
          expandedRowKeys: Array.from(expandedRows),
          onExpand: (_expanded, record) => toggleExpand(record.id),
        }}
      />

      {/* Detail Drawer */}
      <Drawer
        title="数据记录详情"
        open={drawerOpen}
        onClose={() => { setDrawerOpen(false); setDetail(null); }}
        width={640}
      >
        {detail && (
          <>
            <Descriptions column={2} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="ID">{detail.id}</Descriptions.Item>
              <Descriptions.Item label="数据源">{detail.data_source_name || detail.data_source_id}</Descriptions.Item>
              <Descriptions.Item label="同步任务运行 ID">{detail.sync_job_run_id || '-'}</Descriptions.Item>
              <Descriptions.Item label="HTTP 状态码">
                <Tag color={detail.response_status && detail.response_status >= 200 && detail.response_status < 300 ? 'green' : 'red'}>
                  {detail.response_status ?? 'N/A'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="获取时间">{detail.fetched_at ? new Date(detail.fetched_at).toLocaleString() : '-'}</Descriptions.Item>
              <Descriptions.Item label="创建时间">{detail.created_at ? new Date(detail.created_at).toLocaleString() : '-'}</Descriptions.Item>
            </Descriptions>
            <Paragraph strong>完整 Payload：</Paragraph>
            <pre style={{
              maxHeight: 500, overflow: 'auto', background: '#f5f5f5',
              padding: 16, borderRadius: 8, fontSize: 12, lineHeight: 1.5,
              border: '1px solid #e8e8e8',
            }}>
              {formatJson(detail.raw_payload)}
            </pre>
          </>
        )}
      </Drawer>
    </div>
  );
}
