/** Audit log viewer page */

import { useState, useEffect, useCallback } from 'react';
import { Table, Tag, Button, message } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import client from '../../api/client';

interface AuditItem {
  id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  created_at: string;
}

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await client.get('/audit-logs', { params: { page_size: 100 } });
      setLogs(data.items);
    } catch { message.error('加载审计日志失败'); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const actionColors: Record<string, string> = {
    create: 'green', update: 'blue', delete: 'red', execute: 'orange',
  };

  const columns = [
    { title: '时间', dataIndex: 'created_at', key: 'time', width: 180,
      render: (v: string) => v ? new Date(v).toLocaleString() : '-',
    },
    {
      title: '动作', dataIndex: 'action', key: 'action', width: 90,
      render: (a: string) => <Tag color={actionColors[a] || 'default'}>{a}</Tag>,
    },
    { title: '资源', dataIndex: 'resource_type', key: 'resource', width: 110 },
    { title: '资源ID', dataIndex: 'resource_id', key: 'res_id', width: 120, ellipsis: true },
    { title: '用户', dataIndex: 'user_id', key: 'user', width: 120, ellipsis: true },
    { title: 'IP地址', dataIndex: 'ip_address', key: 'ip', width: 130 },
    {
      title: '详情', dataIndex: 'details', key: 'details', ellipsis: true,
      render: (d: Record<string, any>) => d ? `状态：${d.status_code} | ${d.method} ${d.path}` : '-',
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>审计日志</h3>
        <Button icon={<ReloadOutlined />} onClick={fetchLogs}>刷新</Button>
      </div>
      <Table columns={columns} dataSource={logs} rowKey="id" loading={loading}
        pagination={{ pageSize: 20 }} size="small" />
    </div>
  );
}
