/** Dashboard Preview — render dashboard in view mode */

import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Spin, Empty, Button, Space, Tag, Row, Col, Card, Statistic, Table } from 'antd';
import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import client from '../../api/client';

interface WidgetDef {
  id: string;
  widget_type: string;
  title: string;
  query_config: Record<string, any>;
  visual_config: Record<string, any>;
  position_config: Record<string, any>;
}

export default function DashboardPreview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = useCallback(async () => {
    if (!id) return;
    try {
      const { data } = await client.get(`/dashboards/${id}/preview`);
      setDashboard(data);
    } catch { /* ignore */ }
    setLoading(false);
  }, [id]);

  useEffect(() => { fetchDashboard(); }, [fetchDashboard]);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!dashboard) return <Empty description="未找到仪表盘" />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/dashboards')}>返回</Button>
          <h2 style={{ margin: 0 }}>{dashboard.name}</h2>
          <Tag color={dashboard.status === 'published' ? 'green' : 'gold'}>{dashboard.status}</Tag>
        </Space>
        <Button icon={<EditOutlined />} type="primary"
          onClick={() => navigate(`/dashboards/${dashboard.id}/build`)}>
          编辑
        </Button>
      </div>

      {dashboard.description && (
        <p style={{ color: '#666', marginBottom: 24 }}>{dashboard.description}</p>
      )}

      <Row gutter={[16, 16]}>
        {dashboard.widgets.map((widget: WidgetDef) => (
          <Col
            key={widget.id}
            xs={24} sm={12} md={8} lg={6}
            style={{ minHeight: 150 }}
          >
            <RenderWidget widget={widget} />
          </Col>
        ))}
      </Row>

      {dashboard.widgets.length === 0 && (
        <Empty description="暂无组件——编辑此仪表盘以添加内容" />
      )}
    </div>
  );
}

function RenderWidget({ widget }: { widget: WidgetDef }) {
  const vs = widget.visual_config || {};
  const cardStyle: React.CSSProperties = {
    height: '100%',
    backgroundColor: vs.backgroundColor || '#fff',
    color: vs.textColor || '#000',
    fontSize: vs.fontSize || 14,
    borderRadius: vs.borderRadius || 6,
    padding: vs.padding || 16,
    border: vs.showBorder !== false ? '1px solid #f0f0f0' : 'none',
  };

  const title = vs.showTitle !== false ? widget.title : undefined;

  const widgetTypeNames: Record<string, string> = { bar_chart: '柱状图', line_chart: '折线图', pie_chart: '饼图' };

  switch (widget.widget_type) {
    case 'metric_card':
      return (
        <Card style={cardStyle} hoverable>
          <Statistic title={title || '指标'} value={0} suffix="" />
        </Card>
      );

    case 'table':
      return (
        <Card title={title} style={cardStyle} hoverable>
          <Table
            dataSource={[]}
            columns={[{ title: '暂无数据', dataIndex: 'info' }]}
            size="small"
            pagination={false}
            locale={{ emptyText: '配置数据绑定以填充数据' }}
          />
        </Card>
      );

    case 'bar_chart':
    case 'line_chart':
    case 'pie_chart':
      return (
        <Card title={title} style={cardStyle} hoverable>
          <div style={{
            height: 180, display: 'flex', alignItems: 'center',
            justifyContent: 'center', background: '#fafafa',
            borderRadius: 4, color: '#bbb', fontSize: 13,
          }}>
            {widgetTypeNames[widget.widget_type] || widget.widget_type} — 数据可视化
          </div>
        </Card>
      );

    case 'filter':
      return (
        <Card size="small" style={cardStyle}>
          <span style={{ color: '#999', fontSize: 12 }}>筛选器: {widget.title}</span>
        </Card>
      );

    case 'text':
      return (
        <Card style={cardStyle}>
          <p style={{ margin: 0 }}>{widget.title}</p>
        </Card>
      );

    case 'iframe':
      return (
        <Card title={title} style={cardStyle}>
          <div style={{ height: 200, background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#bbb' }}>
            嵌入内容
          </div>
        </Card>
      );

    default:
      return (
        <Card title={title} style={cardStyle}>
          <span style={{ color: '#999' }}>{widget.widget_type}</span>
        </Card>
      );
  }
}
