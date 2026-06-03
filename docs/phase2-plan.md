# Phase 2：Dashboard Builder 與企業級能力 — 開發計劃

**目標**：拖拽式 Builder、配置面板、事件聯動、細粒度 RBAC、告警
**預估工期**：6-8 週
**依賴**：Phase 1 完成
**狀態**：規劃中

---

## 1. 任務總覽

| 編號 | 任務 | 預估工期 | 負責人 | 依賴 |
|------|------|----------|--------|------|
| P2-1 | 拖拽引擎集成 (@dnd-kit + react-grid-layout) | 2 天 | 前端 | Phase 1 |
| P2-2 | 左側組件庫組件 | 1 天 | 前端 | P2-1 |
| P2-3 | 畫布區域組件（拖放、調整大小/位置、複製/刪除） | 2 天 | 前端 | P2-1 |
| P2-4 | 右側屬性配置面板（數據源/維度/指標/篩選/樣式/事件/刷新） | 3 天 | 前端 | P2-1 |
| P2-5 | 數據綁定器 UI | 2 天 | 前端 | P2-4 |
| P2-6 | 事件聯動配置 UI | 2 天 | 前端 | P2-5 |
| P2-7 | Dashboard 狀態機（Draft/Published/Archived） | 1 天 | 後端 | Phase 1 |
| P2-8 | 資源級 RBAC 擴容（對照 PRD 13.2） | 2 天 | 後端 | Phase 1 |
| P2-9 | 任務監控面板 | 2 天 | 前端+後端 | Phase 1 |
| P2-10 | 告警規則引擎（連續失敗、超時、數據量為 0） | 2 天 | 後端 | P2-9 |
| P2-11 | 通知服務（站內 + Email） | 2 天 | 後端 | P2-10 |
| P2-12 | Dashboard 預覽與發布 | 1 天 | 前端 | P2-7 |
| P2-13 | 分享與權限分配 | 2 天 | 前端+後端 | P2-8 |

---

## 2. 關鍵設計要點

### 2.1 Dashboard Builder 佈局

```
┌──────────────────────────────────────────────────────────┐
│  Dashboard 名稱  │  預覽  │  保存  │  發布  │  分享     │
├──────────┬─────────────────────┬─────────────────────────┤
│          │                     │                         │
│ 組件庫   │    畫布區域          │    屬性配置面板          │
│          │                     │                         │
│ 📊 指標卡│  ┌────────┐  ┌───┐  │ 基本信息                 │
│ 📋 表格  │  │        │  │   │  │  標題:                   │
│ 📈 柱狀圖│  │   組件  │  │   │  │  數據源:                 │
│ 📉 折線圖│  │        │  │   │  │  維度:                   │
│ 🥧 餅圖  │  └────────┘  └───┘  │  指標:                   │
│ 🔍 篩選器│       │            │  篩選:                   │
│ 📝 文本  │  ┌────────┐  ┌───┐  │  排序:                   │
│ 🌐 iframe│  │        │  │   │  │  樣式:                   │
│ 🧩 自定義│  │   組件  │  │   │  │  刷新頻率:              │
│          │  │        │  └───┘  │                         │
├──────────┴─────────────────────┴─────────────────────────┤
```

### 2.2 事件聯動模型

```
Widget A (發件人)
  └─ event_config:
       event_type: onItemClick
       target_widgets: [widget_B, widget_C, widget_D]
       action: update_filter
       filter_payload: { sales_id: "{{item.sales_id}}" }

Widget B/C/D (收件人)
  └─ 收到事件後，根據 filter_payload 重新觸發查詢
```

### 2.3 資源級 RBAC 擴容

權限矩陣（對照 PRD 13.2）：

| 資源 | 查看 | 新增 | 編輯 | 刪除 | 測試 | 觸發 | 發布 | 審核 |
|------|------|------|------|------|------|------|------|------|
| 數據源 | Admin/DE | Admin/DE | Admin/DE | Admin | Admin/DE | — | — | — |
| 同步任務 | Admin/DE | Admin/DE | Admin/DE | Admin | — | Admin/DE | — | — |
| 數據表 | Admin/DE | — | — | Admin | — | — | — | — |
| Dashboard | 授權用戶 | Analyst | Analyst | Admin | — | Analyst | — | — |
| 組件 | 授權用戶 | CD | CD | Admin | — | — | Admin | Security Reviewer |
| 用戶 | Admin | Admin | Admin | Admin | — | — | — | — |
| 系統配置 | Admin | — | Admin | — | — | — | — | — |

### 2.4 告警規則模型

```python
class AlertRule(BaseModel):
    rule_name: str
    rule_type: str  # "consecutive_failures" | "http_error" | "timeout" | "zero_data" | "token_expiry"
    target_type: str  # "sync_job" | "data_source" | "custom_component"
    target_id: Optional[str]
    threshold: int  # 例如連續失敗次數
    window_minutes: int  # 時間窗口
    channels: list[str]  # ["inbound", "email", "slack", "webhook"]
    is_active: bool
```

---

## 3. 新增 API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/v1/dashboards/{id}/preview | Dashboard 預覽（渲染用） |
| POST | /api/v1/dashboards/{id}/publish | 發布 Dashboard |
| POST | /api/v1/dashboards/{id}/archive | 歸檔 Dashboard |
| POST | /api/v1/dashboards/{id}/share | 分享/分配權限 |
| GET | /api/v1/alert-rules | 告警規則列表 |
| POST | /api/v1/alert-rules | 創建告警規則 |
| PUT | /api/v1/alert-rules/{id} | 更新告警規則 |
| DELETE | /api/v1/alert-rules/{id} | 刪除告警規則 |
| GET | /api/v1/notifications | 通知列表 |
| PATCH | /api/v1/notifications/{id}/read | 標記已讀 |
| GET | /api/v1/dashboard-metrics | Dashboard 訪問統計 |

---

## 4. 前端新增頁面/組件

| 組件/頁面 | 說明 |
|------|------|
| Dashboard Builder（完整） | 拖拽引擎 + 畫布 + 屬性面板 |
| 組件庫面板 | 左側可拖拽組件列表 |
| 數據綁定器 | 選擇數據表、字段、聚合 |
| 事件聯動配置器 | 配置組件間互動 |
| 告警規則管理頁 | 列表、新建、編輯 |
| 通知中心 | 站內通知列表 |
| Dashboard 分享面板 | 按角色/用戶分配可見性 |

---

## 5. 驗收標準

- [ ] 用戶可以通過拖拽組件搭建 Dashboard
- [ ] 可以調整組件大小和位置
- [ ] 右側面板可以配置組件的數據綁定、樣式、事件
- [ ] 組件之間可以通過事件聯動（點擊篩選 → 刷新其他組件）
- [ ] Dashboard 有完整的狀態機（草稿 → 發布 → 歸檔）
- [ ] 資源級 RBAC 生效，不同角色看到不同內容
- [ ] 同步任務失敗時產生告警
- [ ] 告警通過配置的通道發送
- [ ] Dashboard 可以分享給指定角色/用戶

---

## 6. 依賴關係

```
P2-1 (拖拽引擎) → P2-2 (組件庫)
          ↓
       P2-3 (畫布) → P2-4 (屬性面板) → P2-5 (數據綁定) → P2-6 (事件聯動)

P2-7 (狀態機) → P2-12 (預覽/發布)
P2-8 (RBAC) → P2-13 (分享/權限)
P2-9 (監控) → P2-10 (告警) → P2-11 (通知)
```
