/** Dashboard Builder — drag-and-drop widget layout editor */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Layout, Card, Row, Col, Button, Modal, Input, Select,
  Form, Tabs, Space, Tag, message, Spin, Empty, Tooltip, Dropdown, Switch, InputNumber, ColorPicker
} from 'antd';
import {
  SaveOutlined, EyeOutlined, SendOutlined, InboxOutlined,
  ShareAltOutlined, PlusOutlined, DeleteOutlined, CopyOutlined,
  BarChartOutlined, LineChartOutlined, PieChartOutlined,
  TableOutlined, NumberOutlined, FilterOutlined,
  FontSizeOutlined, CodeOutlined, ArrowLeftOutlined,
} from '@ant-design/icons';
import { Responsive as ResponsiveGridLayout } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import client from '../../api/client';

// -- Constants ---------------------------------------------------------

const WIDGET_TYPES: Record<string, { icon: React.ReactNode; label: string; w: number; h: number }> = {
  metric_card: { icon: <NumberOutlined />, label: '指标卡', w: 3, h: 2 },
  table: { icon: <TableOutlined />, label: '数据表', w: 6, h: 4 },
  bar_chart: { icon: <BarChartOutlined />, label: '柱状图', w: 4, h: 3 },
  line_chart: { icon: <LineChartOutlined />, label: '折线图', w: 4, h: 3 },
  pie_chart: { icon: <PieChartOutlined />, label: '饼图', w: 3, h: 3 },
  filter: { icon: <FilterOutlined />, label: '筛选器', w: 3, h: 1 },
  text: { icon: <FontSizeOutlined />, label: '文本块', w: 3, h: 1 },
  iframe: { icon: <CodeOutlined />, label: '嵌入', w: 4, h: 3 },
};

const AGG_OPTIONS = [
  { label: '计数', value: 'count' },
  { label: '求和', value: 'sum' },
  { label: '平均值', value: 'avg' },
  { label: '最大值', value: 'max' },
  { label: '最小值', value: 'min' },
];

// -- Types ------------------------------------------------------------

interface WidgetDef {
  id: string;
  widget_type: string;
  title: string;
  component_source: string;
  component_key?: string;
  query_config: Record<string, any>;
  props_config: Record<string, any>;
  data_binding_config: Record<string, any>;
  event_config: Record<string, any>;
  visual_config: Record<string, any>;
  position_config: Record<string, any>;
}

interface DashboardData {
  id: string;
  name: string;
  description?: string;
  status: string;
  visibility: string;
  layout_config: Record<string, any>;
  widgets: WidgetDef[];
}

interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
}

// -- Main Component ----------------------------------------------------

export default function DashboardBuilder() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedWidgetId, setSelectedWidgetId] = useState<string | null>(null);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [shareRole, setShareRole] = useState<string>('');
  const [sharePerm, setSharePerm] = useState<string>('view');

  // Fetch dashboard with full config
  const fetchDashboard = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const { data } = await client.get(`/dashboards/${id}/preview`);
      setDashboard(data);
      if (data.widgets.length > 0 && !selectedWidgetId) {
        setSelectedWidgetId(data.widgets[0].id);
      }
    } catch { message.error('加载仪表盘失败'); }
    setLoading(false);
  }, [id]);

  useEffect(() => { fetchDashboard(); }, [fetchDashboard]);

  // -- Layout helpers -------------------------------------------------

  const layout = useMemo((): LayoutItem[] => {
    if (!dashboard) return [];
    return dashboard.widgets.map((w) => {
      const pos = w.position_config || {};
      return {
        i: w.id,
        x: pos.x ?? 0,
        y: pos.y ?? 0,
        w: pos.w ?? WIDGET_TYPES[w.widget_type]?.w ?? 4,
        h: pos.h ?? WIDGET_TYPES[w.widget_type]?.h ?? 3,
        minW: 2,
        minH: 1,
      };
    });
  }, [dashboard]);

  const layouts = useMemo(() => ({ lg: layout }), [layout]);

  // -- Widget CRUD ----------------------------------------------------

  const selectedWidget = useMemo(() => {
    if (!dashboard || !selectedWidgetId) return null;
    return dashboard.widgets.find((w) => w.id === selectedWidgetId) || null;
  }, [dashboard, selectedWidgetId]);

  const addWidget = async (widgetType: string) => {
    if (!dashboard) return;
    const def = WIDGET_TYPES[widgetType];
    try {
      const { data: widget } = await client.post(`/dashboards/${dashboard.id}/widgets`, {
        widget_type: widgetType,
        title: `新建${def.label}`,
        query_config: {},
        props_config: {},
        data_binding_config: {},
        event_config: {},
        visual_config: {},
        position_config: { x: 0, y: 0, w: def.w, h: def.h },
      });
      setDashboard((prev) => prev ? {
        ...prev,
        widgets: [...prev.widgets, { ...widget, query_config: {}, props_config: {}, data_binding_config: {}, event_config: {}, visual_config: {}, position_config: widget.position_config || {} }],
      } : null);
      setSelectedWidgetId(widget.id);
      message.success('组件已添加');
    } catch { message.error('组件添加失败'); }
  };

  const deleteWidget = async (widgetId: string) => {
    if (!dashboard) return;
    try {
      await client.delete(`/dashboards/widgets/${widgetId}`);
      setDashboard((prev) => prev ? { ...prev, widgets: prev.widgets.filter((w) => w.id !== widgetId) } : null);
      setSelectedWidgetId(null);
      message.success('组件已移除');
    } catch { message.error('组件移除失败'); }
  };

  const duplicateWidget = async (widget: WidgetDef) => {
    if (!dashboard) return;
    try {
      const { data: newWidget } = await client.post(`/dashboards/${dashboard.id}/widgets`, {
        widget_type: widget.widget_type,
        title: `${widget.title}（副本）`,
        query_config: widget.query_config,
        data_binding_config: widget.data_binding_config,
        event_config: widget.event_config,
        visual_config: widget.visual_config,
        position_config: { ...widget.position_config, x: (widget.position_config.x || 0) + 1, y: (widget.position_config.y || 0) + 1 },
      });
      setDashboard((prev) => prev ? { ...prev, widgets: [...prev.widgets, { ...newWidget, query_config: newWidget.query_config || {}, props_config: {}, data_binding_config: newWidget.data_binding_config || {}, event_config: newWidget.event_config || {}, visual_config: newWidget.visual_config || {}, position_config: newWidget.position_config || {} }] } : null);
      message.success('组件已复制');
    } catch { message.error('组件复制失败'); }
  };

  // -- Save layout ----------------------------------------------------

  const onLayoutChange = async (newLayout: LayoutItem[]) => {
    if (!dashboard) return;
    const widgetUpdates = newLayout.map((item) => ({
      id: item.i,
      position_config: { x: item.x, y: item.y, w: item.w, h: item.h },
    }));

    setDashboard((prev) => {
      if (!prev) return null;
      const updatedWidgets = prev.widgets.map((w) => {
        const update = widgetUpdates.find((u) => u.id === w.id);
        return update ? { ...w, position_config: update.position_config } : w;
      });
      return { ...prev, widgets: updatedWidgets, layout_config: { layouts: { lg: newLayout } } };
    });

    // Batch update positions
    try {
      await Promise.all(widgetUpdates.map((u) =>
        client.patch(`/dashboards/widgets/${u.id}`, { position_config: u.position_config })
      ));
    } catch { /* silent fail on layout save */ }
  };

  // -- Save widget config ----------------------------------------------

  const updateWidgetConfig = async (widgetId: string, field: string, value: any) => {
    if (!dashboard) return;
    setDashboard((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        widgets: prev.widgets.map((w) => w.id === widgetId ? { ...w, [field]: value } : w),
      };
    });
    try {
      await client.patch(`/dashboards/widgets/${widgetId}`, { [field]: value });
    } catch { /* silent */ }
  };

  // -- Dashboard actions -----------------------------------------------

  const saveDashboard = async () => {
    if (!dashboard) return;
    setSaving(true);
    try {
      await client.patch(`/dashboards/${dashboard.id}`, {
        name: dashboard.name,
        description: dashboard.description,
        layout_config: dashboard.layout_config,
      });
      message.success('仪表盘已保存');
    } catch { message.error('保存失败'); }
    setSaving(false);
  };

  const publishDashboard = async () => {
    if (!dashboard) return;
    try {
      await client.post(`/dashboards/${dashboard.id}/publish`);
      setDashboard((prev) => prev ? { ...prev, status: 'published' } : null);
      message.success('仪表盘已发布！');
    } catch { message.error('发布失败'); }
  };

  const archiveDashboard = async () => {
    if (!dashboard) return;
    try {
      await client.post(`/dashboards/${dashboard.id}/archive`);
      setDashboard((prev) => prev ? { ...prev, status: 'archived' } : null);
      message.success('仪表盘已归档');
    } catch { message.error('归档失败'); }
  };

  const shareDashboard = async () => {
    if (!dashboard) return;
    try {
      await client.post(`/dashboards/${dashboard.id}/share`, {
        shared_with_role: shareRole || null,
        permission_level: sharePerm,
      });
      message.success('分享成功');
      setShareModalOpen(false);
    } catch { message.error('分享失败'); }
  };

  // -- Render ----------------------------------------------------------

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!dashboard) return <Empty description="未找到仪表盘" />;

  return (
    <div style={{ height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/dashboards')}>返回</Button>
          <Input
            style={{ width: 250, fontWeight: 600, fontSize: 16 }}
            value={dashboard.name}
            onChange={(e) => setDashboard((prev) => prev ? { ...prev, name: e.target.value } : null)}
          />
          <Tag color={dashboard.status === 'published' ? 'green' : dashboard.status === 'archived' ? 'red' : 'gold'}>
            {dashboard.status.toUpperCase()}
          </Tag>
        </Space>
        <Space>
          <Button icon={<SaveOutlined />} onClick={saveDashboard} loading={saving}>保存</Button>
          {dashboard.status === 'draft' && (
            <Button icon={<SendOutlined />} type="primary" onClick={publishDashboard}>发布</Button>
          )}
          {dashboard.status === 'published' && (
            <Button icon={<InboxOutlined />} onClick={archiveDashboard}>归档</Button>
          )}
          <Button icon={<ShareAltOutlined />} onClick={() => setShareModalOpen(true)}>分享</Button>
          <Button icon={<EyeOutlined />} onClick={() => navigate(`/dashboards/${dashboard.id}/preview`)}>预览</Button>
        </Space>
      </div>

      {/* Main 3-column layout */}
      <div style={{ flex: 1, display: 'flex', gap: 12, overflow: 'hidden' }}>
        {/* Left: Component Library */}
        <div style={{ width: 180, flexShrink: 0, overflowY: 'auto', borderRight: '1px solid #f0f0f0', paddingRight: 8 }}>
          <h4 style={{ marginBottom: 12 }}>组件库</h4>
          {Object.entries(WIDGET_TYPES).map(([key, def]) => (
            <Card
              key={key}
              size="small"
              hoverable
              style={{ marginBottom: 8, cursor: 'grab' }}
              onClick={() => addWidget(key)}
            >
              <Space>
                {def.icon}
                <span style={{ fontSize: 12 }}>{def.label}</span>
              </Space>
            </Card>
          ))}
        </div>

        {/* Center: Canvas */}
        <div style={{ flex: 1, overflowY: 'auto', background: '#fafafa', borderRadius: 8, padding: 8, minHeight: 400 }}>
          {dashboard.widgets.length === 0 ? (
            <Empty description="从左侧面板拖拽组件或点击添加" style={{ marginTop: 80 }} />
          ) : (
            <ResponsiveGridLayout
              className="layout"
              layouts={layouts}
              breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
              cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
              rowHeight={80}
              onLayoutChange={(l) => onLayoutChange(l)}
              draggableHandle=".widget-drag-handle"
              isResizable={true}
              isDraggable={true}
            >
              {dashboard.widgets.map((widget) => (
                <div
                  key={widget.id}
                  style={{
                    background: selectedWidgetId === widget.id ? '#e6f4ff' : '#fff',
                    border: selectedWidgetId === widget.id ? '2px solid #1677ff' : '1px solid #d9d9d9',
                    borderRadius: 6,
                    padding: 8,
                    cursor: 'pointer',
                    overflow: 'hidden',
                  }}
                  onClick={() => setSelectedWidgetId(widget.id)}
                >
                  <div className="widget-drag-handle" style={{ cursor: 'move', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <Space size={4}>
                      {WIDGET_TYPES[widget.widget_type]?.icon}
                      <strong style={{ fontSize: 12 }}>{widget.title}</strong>
                    </Space>
                    <Dropdown menu={{ items: [
                      { key: 'dup', icon: <CopyOutlined />, label: '复制', onClick: (e) => { e.domEvent.stopPropagation(); duplicateWidget(widget); } },
                      { key: 'del', icon: <DeleteOutlined />, label: '删除', danger: true, onClick: (e) => { e.domEvent.stopPropagation(); deleteWidget(widget.id); } },
                    ]}} trigger={['click']}>
                      <Button size="small" type="text" onClick={(e) => e.stopPropagation()}>⋯</Button>
                    </Dropdown>
                  </div>
                  <div style={{ fontSize: 11, color: '#999', textAlign: 'center', paddingTop: 8 }}>
                    {widget.widget_type.replace('_', ' ').toUpperCase()}
                  </div>
                </div>
              ))}
            </ResponsiveGridLayout>
          )}
        </div>

        {/* Right: Property Panel */}
        <div style={{ width: 320, flexShrink: 0, overflowY: 'auto', borderLeft: '1px solid #f0f0f0', paddingLeft: 8 }}>
          {selectedWidget ? (
            <Tabs
              size="small"
              items={[
                {
                  key: 'basic', label: '基础',
                  children: <BasicPanel widget={selectedWidget} onChange={(field, value) => updateWidgetConfig(selectedWidget.id, field, value)} />,
                },
                {
                  key: 'data', label: '数据',
                  children: <DataPanel widget={selectedWidget} onChange={(field, value) => updateWidgetConfig(selectedWidget.id, field, value)} />,
                },
                {
                  key: 'events', label: '事件',
                  children: <EventPanel widget={selectedWidget} allWidgets={dashboard.widgets} onChange={(field, value) => updateWidgetConfig(selectedWidget.id, field, value)} />,
                },
                {
                  key: 'style', label: '样式',
                  children: <StylePanel widget={selectedWidget} onChange={(field, value) => updateWidgetConfig(selectedWidget.id, field, value)} />,
                },
              ]}
            />
          ) : (
            <Empty description="选择一个组件进行配置" style={{ marginTop: 40 }} />
          )}
        </div>
      </div>

      {/* Share Modal */}
      <Modal title="分享仪表盘" open={shareModalOpen} onOk={shareDashboard} onCancel={() => setShareModalOpen(false)}>
        <Form layout="vertical">
          <Form.Item label="分享给角色">
            <Select placeholder="选择角色" allowClear value={shareRole} onChange={setShareRole}
              options={[
                { label: '管理员', value: 'admin' },
                { label: '编辑者', value: 'editor' },
                { label: '查看者', value: 'viewer' },
              ]}
            />
          </Form.Item>
          <Form.Item label="权限级别">
            <Select value={sharePerm} onChange={setSharePerm}
              options={[
                { label: '可查看', value: 'view' },
                { label: '可编辑', value: 'edit' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

// -- Sub-panels ----------------------------------------------------------

function BasicPanel({ widget, onChange }: { widget: WidgetDef; onChange: (field: string, value: any) => void }) {
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>标题</label>
        <Input size="small" value={widget.title} onChange={(e) => onChange('title', e.target.value)} />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>组件类型</label>
        <Select size="small" style={{ width: '100%' }} value={widget.widget_type}
          onChange={(v) => onChange('widget_type', v)}
          options={Object.entries(WIDGET_TYPES).map(([k, def]) => ({ label: def.label, value: k }))}
        />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>组件来源</label>
        <Select size="small" style={{ width: '100%' }} value={widget.component_source || 'system'}
          onChange={(v) => onChange('component_source', v)}
          options={[
            { label: '系统（内置）', value: 'system' },
            { label: '自定义组件', value: 'custom' },
          ]}
        />
      </div>
      {widget.component_source === 'custom' && (
        <div>
          <label style={{ fontSize: 12, color: '#666' }}>组件标识</label>
          <Input size="small" value={widget.component_key} onChange={(e) => onChange('component_key', e.target.value)} />
        </div>
      )}
    </Space>
  );
}

function DataPanel({ widget, onChange }: { widget: WidgetDef; onChange: (field: string, value: any) => void }) {
  const queryConfig = widget.query_config || {};
  const dataBinding = widget.data_binding_config || {};

  const updateQuery = (key: string, value: any) => {
    onChange('query_config', { ...queryConfig, [key]: value });
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>数据表</label>
        <Select size="small" style={{ width: '100%' }} value={queryConfig.table}
          onChange={(v) => updateQuery('table', v)}
          options={[
            { label: '原始API记录', value: 'raw_api_records' },
          ]}
        />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>维度（分组字段）</label>
        <Select size="small" mode="tags" style={{ width: '100%' }} value={queryConfig.dimensions || []}
          onChange={(v) => updateQuery('dimensions', v)}
          placeholder="例如：response_status"
        />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>指标</label>
        <Form.List name="metrics">
          {(fields, { add, remove }) => {
            const metrics = queryConfig.metrics || [];
            return (
              <div>
                {metrics.map((m: any, idx: number) => (
                  <div key={idx} style={{ display: 'flex', gap: 4, marginBottom: 4 }}>
                    <Input size="small" style={{ width: 80 }} placeholder="字段" value={m.field}
                      onChange={(e) => {
                        const newMetrics = [...metrics];
                        newMetrics[idx] = { ...newMetrics[idx], field: e.target.value };
                        updateQuery('metrics', newMetrics);
                      }}
                    />
                    <Select size="small" style={{ width: 80 }} value={m.aggregation}
                      onChange={(v) => {
                        const newMetrics = [...metrics];
                        newMetrics[idx] = { ...newMetrics[idx], aggregation: v };
                        updateQuery('metrics', newMetrics);
                      }}
                      options={AGG_OPTIONS}
                    />
                    <Input size="small" style={{ width: 70 }} placeholder="别名" value={m.alias}
                      onChange={(e) => {
                        const newMetrics = [...metrics];
                        newMetrics[idx] = { ...newMetrics[idx], alias: e.target.value };
                        updateQuery('metrics', newMetrics);
                      }}
                    />
                    <Button size="small" danger icon={<DeleteOutlined />} onClick={() => {
                      const newMetrics = metrics.filter((_: any, i: number) => i !== idx);
                      updateQuery('metrics', newMetrics);
                    }} />
                  </div>
                ))}
                <Button size="small" type="dashed" block onClick={() => updateQuery('metrics', [...metrics, { field: '', aggregation: 'count', alias: '' }])}>
                  + 添加指标
                </Button>
              </div>
            );
          }}
        </Form.List>
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>排序</label>
        {(queryConfig.sort || []).map((s: any, idx: number) => (
          <div key={idx} style={{ display: 'flex', gap: 4, marginBottom: 4 }}>
            <Input size="small" style={{ width: 100 }} placeholder="字段" value={s.field}
              onChange={(e) => {
                const newSort = [...(queryConfig.sort || [])];
                newSort[idx] = { ...newSort[idx], field: e.target.value };
                updateQuery('sort', newSort);
              }}
            />
            <Select size="small" style={{ width: 80 }} value={s.direction}
              onChange={(v) => {
                const newSort = [...(queryConfig.sort || [])];
                newSort[idx] = { ...newSort[idx], direction: v };
                updateQuery('sort', newSort);
              }}
              options={[{ label: '升序', value: 'asc' }, { label: '降序', value: 'desc' }]}
            />
            <Button size="small" danger icon={<DeleteOutlined />} onClick={() => {
              const newSort = (queryConfig.sort || []).filter((_: any, i: number) => i !== idx);
              updateQuery('sort', newSort);
            }} />
          </div>
        ))}
        <Button size="small" type="dashed" block onClick={() => updateQuery('sort', [...(queryConfig.sort || []), { field: '', direction: 'asc' }])}>
          + 添加排序
        </Button>
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>结果限制</label>
        <InputNumber size="small" style={{ width: '100%' }} value={queryConfig.limit} min={1} max={1000}
          onChange={(v) => updateQuery('limit', v)} />
      </div>
    </Space>
  );
}

function EventPanel({ widget, allWidgets, onChange }: { widget: WidgetDef; allWidgets: WidgetDef[]; onChange: (field: string, value: any) => void }) {
  const eventConfig = widget.event_config || {};

  const updateEvent = (key: string, value: any) => {
    onChange('event_config', { ...eventConfig, [key]: value });
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>事件类型</label>
        <Select size="small" style={{ width: '100%' }} value={eventConfig.event_type}
          onChange={(v) => updateEvent('event_type', v)}
          placeholder="选择触发事件"
          options={[
            { label: '点击项目时', value: 'onItemClick' },
            { label: '选择行时', value: 'onRowSelect' },
            { label: '筛选变化时', value: 'onFilterChange' },
            { label: '数据加载时', value: 'onDataLoad' },
          ]}
        />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>动作</label>
        <Select size="small" style={{ width: '100%' }} value={eventConfig.action}
          onChange={(v) => updateEvent('action', v)}
          placeholder="选择动作"
          options={[
            { label: '更新筛选', value: 'update_filter' },
            { label: '刷新数据', value: 'refresh_data' },
            { label: '导航到', value: 'navigate_to' },
            { label: '显示详情', value: 'show_detail' },
          ]}
        />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>目标组件</label>
        <Select size="small" mode="multiple" style={{ width: '100%' }} value={eventConfig.target_widgets || []}
          onChange={(v) => updateEvent('target_widgets', v)}
          placeholder="选择要通知的组件"
          options={allWidgets.filter((w) => w.id !== widget.id).map((w) => ({
            label: w.title, value: w.id,
          }))}
        />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>过滤参数（JSON）</label>
        <Input.TextArea size="small" rows={4} value={eventConfig.filter_payload ? JSON.stringify(eventConfig.filter_payload, null, 2) : ''}
          placeholder='{"field": "{{item.id}}"}'
          onChange={(e) => {
            try {
              const parsed = e.target.value ? JSON.parse(e.target.value) : {};
              updateEvent('filter_payload', parsed);
            } catch { /* invalid JSON */ }
          }}
        />
      </div>
    </Space>
  );
}

function StylePanel({ widget, onChange }: { widget: WidgetDef; onChange: (field: string, value: any) => void }) {
  const visualConfig = widget.visual_config || {};

  const updateVisual = (key: string, value: any) => {
    onChange('visual_config', { ...visualConfig, [key]: value });
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>背景颜色</label>
        <div>
          <Input size="small" value={visualConfig.backgroundColor || '#ffffff'}
            onChange={(e) => updateVisual('backgroundColor', e.target.value)}
            addonAfter={<input type="color" value={visualConfig.backgroundColor || '#ffffff'}
              style={{ width: 24, height: 24, border: 'none', cursor: 'pointer' }}
              onChange={(e) => updateVisual('backgroundColor', e.target.value)} />}
          />
        </div>
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>文字颜色</label>
        <Input size="small" value={visualConfig.textColor || '#000000'}
          onChange={(e) => updateVisual('textColor', e.target.value)}
          addonAfter={<input type="color" value={visualConfig.textColor || '#000000'}
            style={{ width: 24, height: 24, border: 'none', cursor: 'pointer' }}
            onChange={(e) => updateVisual('textColor', e.target.value)} />}
        />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>字体大小（px）</label>
        <InputNumber size="small" style={{ width: '100%' }} value={visualConfig.fontSize} min={8} max={48}
          onChange={(v) => updateVisual('fontSize', v)} />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>显示标题</label>
        <Switch size="small" checked={visualConfig.showTitle !== false}
          onChange={(v) => updateVisual('showTitle', v)} />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>显示边框</label>
        <Switch size="small" checked={visualConfig.showBorder !== false}
          onChange={(v) => updateVisual('showBorder', v)} />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>边框圆角（px）</label>
        <InputNumber size="small" style={{ width: '100%' }} value={visualConfig.borderRadius} min={0} max={24}
          onChange={(v) => updateVisual('borderRadius', v)} />
      </div>
      <div>
        <label style={{ fontSize: 12, color: '#666' }}>内边距（px）</label>
        <InputNumber size="small" style={{ width: '100%' }} value={visualConfig.padding} min={0} max={48}
          onChange={(v) => updateVisual('padding', v)} />
      </div>
    </Space>
  );
}
