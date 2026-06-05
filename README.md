# Dataplatform

> **企業級低代碼數據應用平台** — 一站式 API 數據接入、同步、存儲、分析與可視化儀表盤構建

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 目錄

- [項目簡介](#項目簡介)
- [技術棧](#技術棧)
- [核心功能](#核心功能)
- [項目結構](#項目結構)
- [快速開始](#快速開始)
- [使用示例](#使用示例)
- [發展藍圖](#發展藍圖)
- [貢獻指南](#貢獻指南)
- [許可證](#許可證)

---

## 項目簡介

**Dataplatform** 是一個面向企業的通用數據平台，旨在解決「多系統 API 數據整合」的痛點。用戶可以：

1. 在前端配置外部系統的 REST API 作為**數據源**
2. 通過**同步任務**定期拉取數據，存入平台數據庫
3. 使用拖拽式 **Dashboard Builder** 構建可視化圖表
4. 配置**告警規則**，在數據異常時即時通知
5. 通過**基於角色的權限控制 (RBAC)** 管理團隊協作

平台涵蓋從 **API 接入 → 數據同步 → 存儲建模 → 可視化展示 → 監控告警** 的完整閉環，無需編寫後端代碼。

> **開發階段**：Phase 1 & 2 已完成（基礎平台 + Dashboard Builder + 企業級能力）  
> **最新版本**：v0.1.0

---

## 技術棧

### 後端

| 類別 | 技術 |
|------|------|
| 框架 | Python 3.12 + FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (async) |
| 數據庫 | PostgreSQL 16 (jsonb) |
| 快取/佇列 | Redis 7 |
| 任務調度 | Celery + Celery Beat |
| 認證 | JWT (Access + Refresh Token) |
| 加密 | Fernet (cryptography) |
| 遷移 | Alembic |
| 測試 | pytest + httpx + pytest-asyncio |

### 前端

| 類別 | 技術 |
|------|------|
| 框架 | React 19 + TypeScript 6 |
| UI 庫 | Ant Design 6 + @ant-design/charts |
| 狀態管理 | Zustand 5 |
| 路由 | React Router 7 |
| 數據請求 | Axios + @tanstack/react-query |
| 拖拽引擎 | react-grid-layout v2 + @dnd-kit |
| 構建工具 | Vite 8 |
| 國際化 | Ant Design zhCN（全系統簡體中文） |

### DevOps

| 類別 | 技術 |
|------|------|
| 容器化 | Docker + docker-compose（7 服務） |
| 對象存儲 | MinIO |

---

## 核心功能

### 🔌 API 數據源管理
- 配置 REST API 的 URL、請求方法（GET/POST）、Header
- 支援多種認證方式：無認證、Bearer Token、API Key（憑證加密存儲）
- 數據源測試連接，即時查看 API 返回樣例

### 🔄 數據同步任務
- 全量 / 增量 / 分頁三種同步模式
- 定時調度（間隔時間 / Cron 表達式）
- 手動觸發即時同步
- 執行記錄追蹤（耗時、數據量、錯誤信息）

### 📊 可視化儀表盤構建器
- **三欄佈局**：組件庫 | 畫布 | 屬性面板
- **8 種內建組件**：指標卡、數據表、柱狀圖、折線圖、餅圖、篩選器、文本塊、嵌入 (iframe)
- **拖拽佈局**：自由調整大小與位置
- **數據綁定**：選擇數據表、維度、指標聚合（計數/求和/平均/最大/最小）
- **事件聯動**：組件間互動（點擊 → 過濾 → 刷新）
- **樣式自定義**：背景色、字體、邊框、圓角、邊距

### 📋 儀表盤生命週期 & 分享
- **三種狀態**：草稿 → 已發布 → 已歸檔
- **分享機制**：按角色或用戶分配查看 / 編輯權限

### 📝 數據瀏覽
- 同步完成後直接在頁面查看原始 API 數據
- 支援按數據源、HTTP 狀態碼、時間範圍篩選
- 展開單行查看完整 JSON Payload

### 🔔 告警規則引擎
- **5 種規則類型**：連續失敗、HTTP 錯誤、超時、零數據、令牌過期
- 同步任務執行後自動評估
- 多渠道通知：站內通知、電子郵件、Slack、Webhook

### 🔐 RBAC 權限管理
- 用戶、角色、權限三層模型
- 預設角色：Admin（管理員）、Editor（編輯者）、Viewer（查看者）
- 資源級權限控制

### 📜 審計日誌
- 中間件自動記錄關鍵操作
- 記錄用戶、動作、資源、IP 地址、請求詳情

---

## 項目結構

```
dataplatform/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API 路由（12 個模塊）
│   │   ├── models/              # ORM 模型（18 張業務表）
│   │   ├── schemas/             # Pydantic schema
│   │   ├── services/            # 業務邏輯服務層
│   │   ├── security/            # JWT 認證 + 授權
│   │   ├── connectors/          # 外部 API 連接器
│   │   ├── middleware/          # 審計日誌中間件
│   │   ├── workers/             # Celery 任務定義
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 數據庫引擎與會話
│   │   └── main.py              # FastAPI 入口
│   ├── tests/                   # pytest 測試（72 個測試）
│   ├── alembic/                 # 數據庫遷移
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/               # 頁面組件（12 頁）
│   │   ├── components/          # 共享組件
│   │   ├── router/              # 路由配置
│   │   ├── stores/              # Zustand 狀態管理
│   │   └── api/                 # API 客戶端
│   └── package.json
├── docs/                        # 產品文檔與開發計劃
├── docker-compose.yml           # 7 服務容器化部署
└── Makefile                     # 開發命令快捷鍵
```

---

## 快速開始

### 前置要求

| 工具 | 版本要求 |
|------|----------|
| Python | ≥ 3.12 |
| Node.js | ≥ 20 |
| PostgreSQL | ≥ 16 |
| Redis | ≥ 7 |
| Docker（可選） | ≥ 24 |

### 環境配置

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env，填入 PostgreSQL 連接資訊
# GDP_DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/gdp
```

### 本地開發

```bash
# 1. 安裝後端依賴
cd backend
pip install -r requirements-dev.txt

# 2. 安裝前端依賴
cd frontend
npm install

# 3. 啟動 PostgreSQL 和 Redis（Docker）
docker compose up -d postgres redis

# 4. 創建數據庫並執行遷移
createdb gdp
cd backend && alembic upgrade head

# 5. 啟動後端開發服務器（熱重載）
make backend-run     # http://localhost:8000

# 6. 啟動前端開發服務器（新終端）
make frontend-dev    # http://localhost:5176

# 7. 運行測試
make backend-test    # 72 個測試案例
```

啟動後訪問：

| 服務 | 地址 |
|------|------|
| 前端介面 | `http://localhost:5176` |
| 後端 API | `http://localhost:8000` |
| Swagger 文檔 | `http://localhost:8000/api/docs` |
| ReDoc 文檔 | `http://localhost:8000/api/redoc` |

### Docker 一鍵部署

```bash
# 啟動全部服務
docker compose up -d

# 查看日誌
docker compose logs -f backend
```

---

## 使用示例

### 1. 創建數據源

```bash
curl -X POST http://localhost:8000/api/v1/data-sources \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub API",
    "request_method": "GET",
    "request_url": "https://api.github.com/repos/rails/rails/issues",
    "auth_type": "bearer_token",
    "auth_config": {"token": "ghp_xxxxxx"},
    "timeout_seconds": 30
  }'
```

### 2. 創建同步任務

```bash
curl -X POST http://localhost:8000/api/v1/sync-jobs \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "data_source_id": "<ds_id>",
    "name": "每日同步 Issues",
    "schedule_type": "cron",
    "schedule_config": "0 8 * * *",
    "sync_mode": "full"
  }'
```

### 3. 瀏覽同步數據

```bash
# 分頁查詢數據記錄
curl -X GET "http://localhost:8000/api/v1/data-records?page=1&page_size=20" \
  -H "Authorization: Bearer <your_token>"

# 查看單條記錄完整 JSON
curl -X GET "http://localhost:8000/api/v1/data-records/<record_id>" \
  -H "Authorization: Bearer <your_token>"
```

### 4. 創建告警規則

```bash
curl -X POST http://localhost:8000/api/v1/alert-rules \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "同步連續失敗告警",
    "rule_type": "consecutive_failures",
    "target_type": "sync_job",
    "threshold": 3,
    "window_minutes": 30,
    "channels": ["in_app", "email"],
    "is_active": true
  }'
```

---

## 發展藍圖

| 階段 | 狀態 | 內容 |
|------|------|------|
| **Phase 1** | ✅ 已完成 | 基礎數據平台閉環（API 接入 → 同步 → 入庫 → 展示） |
| **Phase 2** | ✅ 已完成 | Dashboard Builder + 告警 + RBAC + 通知 + 分享 + 數據瀏覽 |
| **Phase 3** | 📋 規劃中 | 自定義組件系統（Manifest + iframe 沙箱 + 版本管理 + 審核） |
| **Phase 4** | 📋 規劃中 | 智能化與生態化（NL2Query、AI 分析、多租戶、組件市場） |

---

## 貢獻指南

我們歡迎任何形式的貢獻！

### 流程

1. **Fork** 本倉庫
2. 創建功能分支：`git checkout -b feature/amazing-feature`
3. 提交變更：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 開發規範

- **提交訊息**：遵循 [Conventional Commits](https://www.conventionalcommits.org/)（`feat:`、`fix:`、`chore:`、`docs:`）
- **後端**：遵守 PEP 8，使用 ruff 進行 lint/format
- **前端**：TypeScript 嚴格模式 + ESLint
- **測試**：新增功能需包含 pytest 測試

### 運行測試

```bash
# 後端測試
make backend-test

# 前端類型檢查
cd frontend && npx tsc --noEmit

# 前端構建
make frontend-build
```

---

## 許可證

本項目採用 MIT 許可證。詳見 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <sub>Built with ❤️ using FastAPI + React + Ant Design</sub>
</p>
