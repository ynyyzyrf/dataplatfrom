# Phase 4：智能化與生態化 — 開發計劃

**目標**：組件市場、自然語言生成 Dashboard、AI 分析、多租戶
**預估工期**：8-12 週（探索性強）
**依賴**：Phase 3 完成
**狀態**：規劃中

---

## 1. 任務總覽

| 編號 | 任務 | 預估工期 | 負責人 | 依賴 |
|------|------|----------|--------|------|
| P4-1 | 組件市場 | 3 天 | 前端+後端 | Phase 3 |
| P4-2 | NL2Query 服務（自然語言 → 查詢） | 3 天 | 後端 | Phase 2 |
| P4-3 | AI 數據分析（自動洞察、趨勢、異常檢測） | 4 天 | 後端 | P4-2 |
| P4-4 | 報表訂閱與定時發送 | 2 天 | 前端+後端 | Phase 2 |
| P4-5 | 多租戶架構改造 | 4 天 | 後端 | Phase 3 |
| P4-6 | 自動化安全掃描（CI/CD 集成） | 2 天 | 後端 | Phase 3 |
| P4-7 | 企業級組件分發 | 2 天 | 後端 | P4-5 |

---

## 2. 關鍵設計要點

### 2.1 組件市場

```
┌──────────────────────────────────────────┐
│            組件市場首頁                     │
│                                          │
│  🔍 搜索組件...                            │
│                                          │
│  分類: [圖表] [業務] [地圖] [流程] [嵌入]   │
│                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐           │
│  │預覽圖 │  │預覽圖 │  │預覽圖 │           │
│  │名稱  │  │名稱  │  │名稱  │           │
│  │評分⭐ │  │評分⭐ │  │評分⭐ │           │
│  │安裝→ │  │安裝→ │  │安裝→ │           │
│  └──────┘  └──────┘  └──────┘           │
└──────────────────────────────────────────┘
```

功能：
- 組件發現、評分、評論
- 一鍵安裝到當前租户
- 組件版本兼容檢查
- 熱門組件排行

### 2.2 NL2Query（自然語言 → 查詢）

```
用戶輸入: "上個季度各區域的銷售額和訂單量趨勢"
  ↓
LLM 分析意圖
  ↓
{
  "table": "sales_data",
  "dimensions": ["region"],
  "metrics": [
    {"field": "amount", "aggregation": "sum", "alias": "sales_amount"},
    {"field": "order_count", "aggregation": "count", "alias": "order_count"}
  ],
  "filters": [
    {"field": "quarter", "operator": "=", "value": "Q3_2026"}
  ],
  "sort": [{"field": "sales_amount", "direction": "desc"}],
  "chart_type": "line"
}
  ↓
Query Service 查詢
  ↓
返回圖表數據 → Dashboard 渲染
```

### 2.3 多租戶架構

所有資源表增加 `tenant_id` 字段：

```python
class BaseModel(Base):
    __abstract__ = True
    
    id: Mapped[uuid] = mapped_column(UUID, primary_key=True, default=uuid4)
    tenant_id: Mapped[uuid] = mapped_column(UUID, ForeignKey("tenants.id"), nullable=False)
    created_by: Mapped[uuid] = mapped_column(UUID, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
```

租戶隔離策略：
- 所有 SQL 查詢自動附加 `WHERE tenant_id = :tenant_id`
- JWT Token 中攜帶 `tenant_id` claim
- API 層中間件校驗租戶權限
- 數據庫 level：MVP 同庫不同租户，生產可考慮分庫

---

## 3. 新增 API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/v1/market/components | 組件市場列表 |
| POST | /api/v1/market/components/{id}/install | 安裝組件到租户 |
| POST | /api/v1/ai/nl2query | 自然語言 → 查詢 |
| POST | /api/v1/ai/analyze | AI 數據分析 |
| GET | /api/v1/ai/insights/{dashboard_id} | 自動洞察 |
| POST | /api/v1/reports/subscribe | 創建報表訂閱 |
| GET | /api/v1/reports/subscriptions | 訂閱列表 |
| POST | /api/v1/tenants | 創建租戶 |
| GET | /api/v1/tenants/{id} | 租戶詳情 |
| PATCH | /api/v1/tenants/{id} | 更新租戶 |
| GET | /api/v1/tenant/quota | 租戶資源用量 |

---

## 4. 驗收標準

- [ ] 用戶可以在組件市場發現、評分、安裝組件
- [ ] 用戶可以用自然語言描述需求，平台生成對應的查詢和圖表
- [ ] AI 可以自動檢測數據異常並生成洞察報告
- [ ] 用戶可以訂閱報表，定時收到推送
- [ ] 多租戶數據完全隔離，不同租户看不到對方數據
- [ ] 組件上傳後自動執行安全掃描
- [ ] 支持企業級組件分發（按租户組組件）

---

## 5. 風險與注意事項

| 風險 | 應對 |
|------|------|
| NL2Query 準確度 | 先限定查詢範圍、提供確認步驟、持續優化 prompt |
| AI 調用成本 | 查詢緩存、定時批量分析、token 限額 |
| 多租戶改造範圍大 | 逐步引入 tenant_id，新表直接支持 |
| 組件市場審核 | 自動化 + 人工雙重審核，惡意組件一鍵下架 |
| 租戶資源濫用 | 用量配额、限流、超量告警 |

---

## 6. 與前面的關係

Phase 4 是在 Phase 1-3 的基礎上進行智能化和生態化擴展，不改變既有核心鏈路：

```
外部 API → 同步 → 入庫 → Query → Dashboard
                                         ↓
                                  Phase 3 自定義組件
                                         ↓
                                  Phase 4 組件市場 + AI
```

Phase 4 的功能可以独立交付，但需要依賴 Phase 1-3 的數據和能力基礎。
