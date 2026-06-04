/** Notification center page */

import { useState, useEffect, useCallback } from 'react';
import { Table, Button, Tag, Space, message, Badge, Tabs } from 'antd';
import { ReloadOutlined, MailOutlined, CheckOutlined } from '@ant-design/icons';
import client from '../../api/client';

interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  source?: string;
  is_read: boolean;
  metadata_json?: Record<string, any>;
  created_at: string;
}

export default function NotificationPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = { page_size: 100 };
      if (filter === 'unread') params.unread_only = true;
      const { data } = await client.get('/notifications', { params });
      setNotifications(data.items);
    } catch { message.error('加载通知失败'); }
    setLoading(false);
  }, [filter]);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const { data } = await client.get('/notifications/unread-count');
      setUnreadCount(data.unread_count);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchNotifications(); fetchUnreadCount(); }, [fetchNotifications, fetchUnreadCount]);

  const handleMarkRead = async (id: string) => {
    try {
      await client.patch(`/notifications/${id}/read`);
      setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch { message.error('操作失败'); }
  };

  const handleMarkAllRead = async () => {
    try {
      const { data } = await client.patch('/notifications/mark-all-read');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
      message.success(`${data.marked_read}条已标记为已读`);
    } catch { message.error('操作失败'); }
  };

  const typeColors: Record<string, string> = {
    alert: 'red', warning: 'orange', info: 'blue', success: 'green', error: 'red',
  };

  const columns = [
    {
      title: '', dataIndex: 'is_read', key: 'read', width: 20,
      render: (read: boolean) => !read ? <Badge status="processing" /> : null,
    },
    {
      title: '类型', dataIndex: 'notification_type', key: 'type', width: 80,
      render: (t: string) => <Tag color={typeColors[t] || 'default'}>{t}</Tag>,
    },
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
    { title: '消息', dataIndex: 'message', key: 'message', ellipsis: true },
    { title: '来源', dataIndex: 'source', key: 'source', width: 120, ellipsis: true },
    {
      title: '时间', dataIndex: 'created_at', key: 'time', width: 160,
      render: (v: string) => v ? new Date(v).toLocaleString() : '-',
    },
    {
      title: '操作', key: 'actions', width: 90,
      render: (_: unknown, record: Notification) => (
        !record.is_read ? (
          <Button size="small" icon={<CheckOutlined />} onClick={() => handleMarkRead(record.id)}>
            标记已读
          </Button>
        ) : null
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Space>
          <h3>通知</h3>
          {unreadCount > 0 && <Badge count={unreadCount} />}
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => { fetchNotifications(); fetchUnreadCount(); }}>
            刷新
          </Button>
          {unreadCount > 0 && (
            <Button icon={<MailOutlined />} onClick={handleMarkAllRead}>
              全部标记已读
            </Button>
          )}
        </Space>
      </div>

      <Tabs
        activeKey={filter}
        onChange={(key) => setFilter(key as 'all' | 'unread')}
        items={[
          { key: 'all', label: '全部' },
          { key: 'unread', label: `未读（${unreadCount}）` },
        ]}
        style={{ marginBottom: 12 }}
      />

      <Table columns={columns} dataSource={notifications} rowKey="id" loading={loading}
        pagination={{ pageSize: 20 }} size="middle"
        rowClassName={(record) => !record.is_read ? 'notification-unread' : ''}
      />

      <style>{`
        .notification-unread { background: #f0f5ff; font-weight: 500; }
      `}</style>
    </div>
  );
}
