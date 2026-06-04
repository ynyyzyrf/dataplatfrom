# 通用數據平台 (GDP) — 開發進度記錄

> 最後更新：2026-06-04

---

## 一、專案概覽

| 項目 | 說明 |
|------|------|
| 專案名稱 | General Data Platform (GDP) |
| 版本 | 0.1.0 |
| 倉庫 | `https://gitlab.sjfood.us/osc-ai/test` (main) |
| 開發環境 | Windows 11, Python 3.12, Node.js |

### 技術棧

| 層級 | 技術 | 備註 |
|------|------|------|
| 後端框架 | FastAPI 0.115 | 非同步 |
| ORM | SQLAlchemy 2.0 (async) | |
| 資料庫 | **PostgreSQL 16.13** | 已切換，原開發用 SQLite |
| 快取/隊列 | Redis 7 | 配置中 |
| 任務調度 | Celery + Celery Beat | 規劃中 |
| 認證 | JWT (Access + Refresh) | |
| 加密 | Fernet (cryptography) | |
| 測試 | pytest + httpx | 66 tests |
| 前端框架 | React 18 + TypeScript | |
| UI 庫 | Ant Design 5 (zhCN) | |
| 狀態管理 | Zustand | |
| 建構工具 | Vite 8 | |
| 拖拽引擎 | react-grid-layout v2 + @dnd-kit | |
| 容器化 | Docker + docker-compose | 規劃中 |

---

## 二、開發階段總覽

| 階段 | 狀態 | 說明 |
|------|------|------|
| Phase 1 | ✅ **已完成** | 基礎數據平台閉環（API → 同步 → 入庫 → 展示） |
| Phase 2 | ✅ **已完成** | Dashboard Builder + 企業級能力（拖拽、告警、RBAC、分享） |
| Phase 3 | 📋 規劃中 | 高級自定義組件（Manifest 驅動 + iframe 沙箱 + 審核流程） |
| Phase 4 | 📋 規劃中 | 智能化與生態化（AI 分析、多租戶、組件市場） |

---

## 三、Phase 1 完成情況 — 基礎數據平台

### 已實現功能

- ✅ 用戶認證體系（JWT 登入/登出/刷新）
- ✅ RBAC 權限管理（用戶、角色、權限、CRUD）
- ✅ REST API 數據源管理（Bearer Token / API Key 認證）
- ✅ 數據源測試連接（含憑證加密儲存 Fernet）
- ✅ 同步任務管理（全量/增量/分頁模式、手動觸發）
- ✅ 同步執行記錄
- ✅ Dashboard 基礎 CRUD（含 Widget 組件管理）
- ✅ 查詢服務（聚合查詢 API）
- ✅ 審計日誌（中間件自動記錄 + 查詢頁面）
- ✅ SSRF 防護
- ✅ 前端完整頁面（登入、數據源、同步任務、Dashboard、審計日誌）

### 代碼統計

| 指標 | 數量 |
|------|------|
| 後端 Python 檔案 | 69 個 (`app/`) |
| 前端 TS/TSX 檔案 | 21 個 (`src/`) |
| 測試檔案 | 11 個 |
| 測試案例 | 66 個（全部通過） |
| 資料表 | 19 張（18 業務表 + alembic_version） |

---

## 四、Phase 2 完成情況 — Dashboard Builder & 企業級能力

### P2-1 ~ P2-6：Dashboard Builder

- ✅ 三欄拖拽佈局（組件庫 | 畫布 | 屬性面板）
- ✅ 8 種內建組件：指標卡、數據表、柱狀圖、折線圖、餅圖、篩選器、文本塊、嵌入 (iframe)
- ✅ react-grid-layout v2 畫布（拖放、調整大小/位置）
- ✅ 右側屬性面板（基礎/數據/事件/樣式 四個標籤頁）
- ✅ 數據綁定配置（數據表、維度、指標聚合、排序、限制）
- ✅ 事件聯動配置（觸發事件 → 動作 → 目標組件 → 過濾參數）
- ✅ 組件複製/刪除

### P2-7：Dashboard 狀態機

- ✅ 三種狀態：草稿 (Draft) → 已發布 (Published) → 已歸檔 (Archived)
- ✅ 後端狀態轉換 API（publish / archive / preview）

### P2-8：資源級 RBAC 擴容

- ✅ Dashboard 分享模型（按角色 / 按用戶）
- ✅ 查看/編輯權限級別
- ✅ Share CRUD API

### P2-9 ~ P2-11：監控與告警

- ✅ 監控面板（平台總覽 API + 前端頁面）
- ✅ 告警規則引擎（5 種規則類型）：
  - `consecutive_failures` — 連續失敗
  - `http_error` — HTTP 錯誤
  - `timeout` — 超時
  - `zero_data` — 零數據
  - `token_expiry` — 令牌過期
- ✅ 告警評估（同步任務執行後自動評估）
- ✅ 通知服務（站內通知 + 通知中心頁面）
- ✅ 多頻道支援（in_app / email / slack / webhook）

### P2-12 ~ P2-13：預覽與分享

- ✅ Dashboard 預覽頁面（只讀渲染各類組件）
- ✅ 分享模態框（選角色/權限級別）

### Phase 2 新增 API

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/api/v1/dashboards/{id}/publish` | 發布儀表盤 |
| POST | `/api/v1/dashboards/{id}/archive` | 歸檔儀表盤 |
| GET | `/api/v1/dashboards/{id}/preview` | 預覽儀表盤 |
| POST | `/api/v1/dashboards/{id}/share` | 分享儀表盤 |
| GET | `/api/v1/dashboards/{id}/shares` | 查詢分享列表 |
| DELETE | `/api/v1/dashboards/shares/{id}` | 撤銷分享 |
| GET | `/api/v1/alert-rules` | 告警規則列表 |
| POST | `/api/v1/alert-rules` | 創建告警規則 |
| GET | `/api/v1/alert-rules/{id}` | 告警規則詳情 |
| PUT | `/api/v1/alert-rules/{id}` | 更新告警規則 |
| DELETE | `/api/v1/alert-rules/{id}` | 刪除告警規則 |
| GET | `/api/v1/notifications` | 通知列表 |
| GET | `/api/v1/notifications/unread-count` | 未讀數量 |
| PATCH | `/api/v1/notifications/{id}/read` | 標記已讀 |
| PATCH | `/api/v1/notifications/mark-all-read` | 全部已讀 |
| GET | `/api/v1/monitoring/overview` | 平台監控概覽 |

### Phase 2 新增前端頁面

| 頁面 | 路由 | 說明 |
|------|------|------|
| Dashboard Builder | `/dashboards/:id/build` | 拖拽式編輯器（完整） |
| Dashboard Preview | `/dashboards/:id/preview` | 只讀預覽 |
| 告警規則管理 | `/alert-rules` | 列表、新建、編輯、刪除 |
| 通知中心 | `/notifications` | 站內通知、已讀/未讀 |
| 平台監控 | `/monitoring` | 總覽統計、任務效能 |

---

## 五、資料庫結構

### 完整資料表（19 張）

| 類別 | 表名 | 說明 |
|------|------|------|
| **RBAC** | `users` | 用戶 |
| | `roles` | 角色 |
| | `permissions` | 權限 |
| | `user_roles` | 用戶-角色關聯 |
| | `role_permissions` | 角色-權限關聯 |
| **數據流** | `data_sources` | API 數據源配置 |
| | `sync_jobs` | 同步任務 |
| | `sync_job_runs` | 同步執行記錄 |
| | `data_mappings` | 欄位映射 |
| | `raw_api_records` | 原始 JSON 記錄 |
| **儀表盤** | `dashboards` | 儀表盤 |
| | `dashboard_widgets` | 儀表盤組件 |
| | `dashboard_shares` | 儀表盤分享 *(P2)* |
| | `custom_components` | 自定義組件 |
| | `custom_component_versions` | 組件版本 |
| **安全/監控** | `audit_logs` | 審計日誌 |
| | `alert_rules` | 告警規則 *(P2)* |
| | `notifications` | 通知 *(P2)* |
| **系統** | `alembic_version` | 遷移版本記錄 |

---

## 六、中文化 (i18n)

已完成全系統簡體中文化，覆蓋所有用戶可見文字：

- ✅ 後端：12 個服務文件（異常訊息、服務層錯誤提示、種子資料）
- ✅ 前端：全部 12 個頁面 + 佈局組件
- ✅ Ant Design 已配置 `zhCN` locale
- ✅ 消息提示、表單標籤、按鈕文字、模態框、選單等全部中文化

---

## 七、環境配置

### 當前資料庫連線

```
GDP_DATABASE_URL=postgresql+asyncpg://postgres:******@localhost:5432/gdp
GDP_DATABASE_SYNC_URL=postgresql://postgres:******@localhost:5432/gdp
```

### 啟動命令

```bash
# 後端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend
npx vite --port 5176 --host
```

| 服務 | 地址 |
|------|------|
| 後端 API | `http://localhost:8000` |
| API 文件 (Swagger) | `http://localhost:8000/docs` |
| 前端介面 | `http://localhost:5176` |

---

## 八、下一步計劃

### Phase 3：高級自定義組件

1. Manifest 驅動自定義組件系統
2. iframe 沙箱隔離執行
3. 組件版本管理（發布、回滾）
4. 組件市場基礎
5. 安全審核流程

### 待優化項目

- [ ] Docker Compose 一鍵部署
- [ ] Celery 非同步任務（同步任務排程）
- [ ] Redis 快取層
- [ ] CI/CD Pipeline
- [ ] API Rate Limiting
- [ ] 前端單元測試
- [ ] E2E 整合測試
