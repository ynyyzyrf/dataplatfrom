# 企業級數據平台需求文檔

版本：v0.1
狀態：需求設計稿
產品定位：企業級數據接入、同步、存儲、分析與自定義 Dashboard 搭建平台

---

## 1. 項目背景

企業內部通常存在多個業務系統，例如 CRM、ERP、財務系統、客服系統、工單系統、營銷平台、內部 SaaS 等。這些系統的數據分散在不同平台中，接口標準、認證方式、數據格式和更新頻率各不相同，導致企業很難快速構建統一的數據看板和業務分析能力。

本項目希望搭建一個企業級數據平台，支持用戶在前端配置不同系統的接口，平台負責定時拉取數據、存儲數據、建模數據，最終通過可自定義搭建的 Dashboard 進行展示。

進一步地，平台需要支持高級版能力：企業開發者可以開發、上傳、註冊自定義 Dashboard 組件，業務用戶可以在 Dashboard Builder 中拖拽使用這些組件，實現企業內部高度定制化的數據展示和數據應用搭建。

---

## 2. 產品定位

本平台定位為：

> 企業級低代碼數據應用平台。

核心能力包括：

1. 支持前端配置外部系統 API。
2. 支持 Bearer Token / API Key 等認證方式。
3. 支持手動或定時拉取外部數據。
4. 支持數據入庫、原始數據存儲、字段映射和結構化存儲。
5. 支持基於數據表進行查詢、聚合和分析。
6. 支持 Dashboard 自定義搭建。
7. 支持拖拽式組件配置。
8. 支持企業開發者開發、上傳和發布自定義組件。
9. 支持組件沙箱、權限、審核、版本管理和安全隔離。
10. 支持企業級 RBAC 權限、審計、監控和告警。

---

## 3. 目標用戶

| 角色            | 說明                              |
| ------------- | ------------------------------- |
| 平台管理員         | 負責平台配置、用戶管理、權限管理、組件審核、系統安全      |
| 數據管理員         | 負責接入外部系統 API、配置數據源、字段映射和同步任務    |
| 數據工程師         | 負責數據模型設計、數據清洗、同步策略和查詢性能優化       |
| Dashboard 編輯者 | 負責搭建 Dashboard、配置圖表、配置數據綁定和發布看板 |
| 組件開發者         | 負責開發企業內部自定義組件並提交平台審核            |
| 業務查看者         | 查看已發布 Dashboard 和報表，不具備配置權限     |
| 安全審核人         | 審核自定義組件的安全風險、權限聲明和使用範圍          |

---

## 4. 核心業務流程

### 4.1 數據接入流程

```text
創建數據源
→ 配置 API URL
→ 配置認證方式
→ 配置 Header / Query / Body
→ 測試連接
→ 預覽返回數據
→ 配置字段映射
→ 保存數據源
```

### 4.2 數據同步流程

```text
創建同步任務
→ 選擇數據源
→ 配置同步頻率
→ 配置全量 / 增量同步
→ 執行同步
→ 保存原始數據
→ 結構化入庫
→ 記錄同步日誌
```

### 4.3 Dashboard 搭建流程

```text
創建 Dashboard
→ 從組件庫拖入組件
→ 綁定數據表
→ 配置維度、指標、篩選條件
→ 配置樣式和交互
→ 預覽
→ 發布
→ 分配權限
```

### 4.4 自定義組件流程

```text
開發者開發組件
→ 編寫組件 Manifest
→ 本地測試
→ 打包組件
→ 上傳到平台
→ 平台安全檢查
→ 管理員審核
→ 發布到組件庫
→ Dashboard 編輯者拖拽使用
→ 綁定數據
→ 發布 Dashboard
```

---

## 5. 產品功能範圍

### 5.1 MVP 基礎能力

| 模塊              | 是否包含 | 說明                            |
| --------------- | ---: | ----------------------------- |
| 數據源管理           |    是 | 支持配置外部 REST API               |
| Bearer Token 認證 |    是 | 支持 Authorization Bearer Token |
| API Key 認證      |    是 | 支持 Header / Query 傳入          |
| 手動同步            |    是 | 用戶可立即觸發同步                     |
| 定時同步            |    是 | 支持固定頻率和 Cron                  |
| 原始數據存儲          |    是 | 保存 API 返回的原始 JSON             |
| 字段映射            |    是 | JSON 字段映射到內部結構化字段             |
| 結構化入庫           |    是 | 將數據寫入平台數據庫                    |
| 基礎 Dashboard    |    是 | 支持看板創建、保存、發布                  |
| 基礎圖表組件          |    是 | 指標卡、表格、柱狀圖、折線圖、餅圖             |
| 權限管理            |    是 | 支持基礎 RBAC                     |
| 同步日誌            |    是 | 記錄任務執行情況                      |
| 審計日誌            |    是 | 記錄關鍵操作                        |

### 5.2 高級版能力

| 模塊                | 說明                     |
| ----------------- | ---------------------- |
| Dashboard Builder | 支持拖拽式自定義搭建             |
| 組件庫               | 管理系統組件與自定義組件           |
| 自定義組件             | 支持企業開發者開發和上傳組件         |
| 組件 Manifest       | 描述組件元信息、配置項、數據需求和事件能力  |
| 動態配置面板            | 根據 Manifest 自動生成右側配置面板 |
| 數據綁定器             | 支持自定義組件與平台數據表綁定        |
| 組件版本管理            | 支持多版本、升級、下架和兼容策略       |
| 組件審核              | 支持安全審核、管理員審核和發布流程      |
| 組件沙箱              | 支持組件隔離渲染，避免影響主平台       |
| 事件聯動              | 支持組件之間的篩選、點擊、鑽取等互動     |
| 錯誤隔離              | 自定義組件崩潰不影響整個 Dashboard |

---

## 6. 數據源管理

### 6.1 新增數據源

用戶可以在前端新增外部系統數據源。

字段包括：

| 字段        | 說明                              | 是否必填 |
| --------- | ------------------------------- | ---: |
| 數據源名稱     | 例如 Salesforce 客戶數據、Shopify 訂單數據 |    是 |
| 數據源描述     | 說明數據用途                          |    否 |
| 所屬分組      | CRM、財務、客服、營銷等                   |    否 |
| 接口 URL    | 外部系統 API 地址                     |    是 |
| 請求方法      | GET / POST，後續支持 PUT / DELETE    |    是 |
| 認證方式      | None / Bearer Token / API Key   |    是 |
| 請求 Header | 自定義 Header                      |    否 |
| Query 參數  | URL 查詢參數                        |    否 |
| Body 參數   | POST 請求體                        |    否 |
| 返回格式      | MVP 先支持 JSON                    |    是 |
| 超時時間      | 默認 30 秒                         |    否 |
| 重試次數      | 默認 3 次                          |    否 |

---

### 6.2 Bearer Token 認證

平台支持 Bearer Token 接入方式。

請求時自動添加：

```http
Authorization: Bearer <token>
```

安全要求：

1. Token 不允許明文展示。
2. Token 入庫前必須加密。
3. 前端只展示脫敏內容。
4. 用戶只能更新 Token，不能查看完整 Token。
5. 日誌中禁止打印 Token。

---

### 6.3 API Key 認證

API Key 支持兩種傳入方式：

| 傳入位置   | 示例                     |
| ------ | ---------------------- |
| Header | `x-api-key: <api_key>` |
| Query  | `?api_key=<api_key>`   |

配置字段包括：

| 字段     | 說明                       |
| ------ | ------------------------ |
| Key 名稱 | 例如 `x-api-key`、`api_key` |
| Key 值  | 實際密鑰                     |
| 傳入位置   | Header / Query           |

---

### 6.4 接口測試

保存數據源前，用戶可以點擊「測試連接」。

測試內容包括：

1. URL 是否可訪問。
2. 認證是否成功。
3. 返回是否為合法 JSON。
4. 是否能解析出數據列表。
5. 是否能展示返回樣例。

測試結果包括：

| 結果項      | 說明                |
| -------- | ----------------- |
| 狀態       | 成功 / 失敗           |
| HTTP 狀態碼 | 200、401、403、500 等 |
| 響應耗時     | 毫秒                |
| 錯誤信息     | 認證失敗、超時、格式錯誤等     |
| 返回樣例     | 展示前幾條數據           |
| 解析字段     | 自動識別 JSON 字段      |

---

## 7. 數據同步任務

### 7.1 手動同步

用戶可以點擊「立即同步」按鈕，平台即時調用接口並拉取數據。

同步過程中需要展示：

1. 同步中狀態。
2. 成功拉取條數。
3. 成功入庫條數。
4. 失敗條數。
5. 錯誤原因。
6. 同步耗時。
7. 最近同步時間。

---

### 7.2 定時同步

平台支持用戶配置同步頻率。

支持方式：

| 類型       | 示例                    |
| -------- | --------------------- |
| 固定間隔     | 每 5 分鐘、每 30 分鐘、每 1 小時 |
| 每日定時     | 每天凌晨 2 點              |
| 每週定時     | 每週一早上 8 點             |
| Cron 表達式 | `0 2 * * *`           |

同步任務字段包括：

| 字段    | 說明           |
| ----- | ------------ |
| 任務名稱  | 例如「每日同步訂單數據」 |
| 關聯數據源 | 關聯某個 API 數據源 |
| 同步頻率  | 固定間隔 / Cron  |
| 是否啟用  | 啟用 / 暫停      |
| 超時時間  | 單次任務最大執行時間   |
| 重試策略  | 失敗後重試次數與間隔   |
| 失敗通知  | 通知管理員或數據負責人  |

---

### 7.3 同步模式

平台支持以下同步模式：

| 模式   | 說明                                 |
| ---- | ---------------------------------- |
| 全量同步 | 每次拉取完整數據                           |
| 增量同步 | 根據時間字段或游標拉取新增 / 更新數據               |
| 分頁同步 | 按 page / page_size 或 cursor 拉取多頁數據 |
| 覆蓋同步 | 每次同步後覆蓋舊數據                         |
| 追加同步 | 每次同步都追加歷史快照                        |

MVP 建議支持：

1. 全量同步。
2. 基於時間字段的增量同步。
3. 基於 page / page_size 的分頁同步。
4. Upsert 寫入策略。

---

## 8. 數據存儲與字段映射

### 8.1 原始數據存儲

平台應保存外部 API 返回的原始 JSON。

用途：

1. 排查同步問題。
2. 支持重新解析。
3. 支持數據審計。
4. 避免字段映射錯誤導致數據丟失。

示例表：`raw_api_records`

| 字段              | 說明       |
| --------------- | -------- |
| id              | 主鍵       |
| data_source_id  | 數據源 ID   |
| sync_job_id     | 同步任務 ID  |
| raw_payload     | 原始 JSON  |
| response_status | HTTP 狀態碼 |
| fetched_at      | 拉取時間     |
| created_at      | 創建時間     |

---

### 8.2 結構化數據存儲

平台將原始 JSON 經字段映射後寫入結構化數據表。

示例 API 返回：

```json
{
  "id": "order_001",
  "customer": {
    "name": "Alice"
  },
  "amount": 99.9,
  "status": "paid",
  "created_at": "2026-06-01T10:00:00Z"
}
```

字段映射示例：

| 平台字段              | JSON 路徑         |
| ----------------- | --------------- |
| external_order_id | `id`            |
| customer_name     | `customer.name` |
| amount            | `amount`        |
| status            | `status`        |
| order_created_at  | `created_at`    |

---

### 8.3 字段類型

平台應支持以下字段類型：

| 類型       | 說明   |
| -------- | ---- |
| String   | 文本   |
| Number   | 數字   |
| Boolean  | 布爾值  |
| DateTime | 日期時間 |
| JSON     | 嵌套對象 |
| Array    | 數組   |

---

### 8.4 主鍵與去重策略

每個結構化數據表需要配置唯一鍵。

支持方式：

| 策略      | 說明                          |
| ------- | --------------------------- |
| 單字段唯一鍵  | 例如 `order_id`               |
| 多字段唯一鍵  | 例如 `platform + external_id` |
| 系統自動 ID | 沒有外部 ID 時由平台生成              |

寫入策略包括：

| 策略          | 說明           |
| ----------- | ------------ |
| Insert Only | 只新增，不更新      |
| Upsert      | 存在則更新，不存在則插入 |
| Replace     | 每次同步後覆蓋舊數據   |
| Append      | 每次追加歷史快照     |

---

## 9. 查詢與聚合能力

平台需要提供統一 Query Service，供 Dashboard 組件查詢數據。

MVP 查詢能力包括：

1. 選擇數據表。
2. 選擇維度字段。
3. 選擇指標字段。
4. 配置聚合方式。
5. 配置篩選條件。
6. 配置排序。
7. 配置時間範圍。
8. 配置返回條數。

聚合方式包括：

| 聚合方式           | 說明   |
| -------------- | ---- |
| Count          | 計數   |
| Sum            | 求和   |
| Avg            | 平均值  |
| Max            | 最大值  |
| Min            | 最小值  |
| Distinct Count | 去重計數 |

---

## 10. Dashboard Builder

### 10.1 功能定位

平台提供低代碼 Dashboard Builder，支持用戶通過拖拽和配置方式自定義搭建數據看板。

用戶可以添加內置圖表組件和自定義組件，綁定已接入數據源，配置維度、指標、聚合、篩選、樣式和交互，並將 Dashboard 保存、預覽、發布和授權給不同角色使用。

---

### 10.2 編輯器布局

Dashboard Builder 頁面建議分為三個區域：

```text
左側：組件庫
中間：畫布區域
右側：屬性配置面板
```

#### 左側組件庫

展示可用組件，包括：

1. 基礎圖表。
2. 指標卡。
3. 表格。
4. 篩選器。
5. 文本組件。
6. iframe 組件。
7. 自定義組件。

#### 中間畫布

支持：

1. 拖拽組件。
2. 調整組件大小。
3. 調整組件位置。
4. 複製組件。
5. 刪除組件。
6. 預覽效果。
7. 保存 Dashboard。

#### 右側屬性面板

支持配置：

1. 基本信息。
2. 數據來源。
3. 維度和指標。
4. 篩選條件。
5. 聚合方式。
6. 排序方式。
7. 樣式配置。
8. 交互配置。
9. 刷新頻率。

---

### 10.3 Dashboard 狀態

| 狀態        | 說明              |
| --------- | --------------- |
| Draft     | 草稿，可編輯，不對普通用戶可見 |
| Published | 已發布，可被授權用戶查看    |
| Archived  | 已歸檔，不再展示        |
| Deleted   | 已刪除             |

---

### 10.4 基礎組件

| 組件        | 用途               |
| --------- | ---------------- |
| 指標卡       | 總收入、訂單數、用戶數等單一指標 |
| 表格        | 展示明細數據           |
| 柱狀圖       | 分類對比             |
| 折線圖       | 時間趨勢             |
| 餅圖        | 佔比分析             |
| 篩選器       | 全局篩選條件           |
| 文本組件      | 標題、說明、備註         |
| iframe 組件 | 嵌入外部頁面           |

---

## 11. 高級版：自定義組件

### 11.1 功能定位

平台支持企業開發者開發、註冊、上傳和發布自定義 Dashboard 組件。

自定義組件通過標準 Manifest 描述組件配置、數據需求、事件能力和權限需求。業務用戶可以在 Dashboard Builder 中拖拽使用已發布組件，並通過配置面板完成數據綁定、樣式配置和事件聯動。

平台需要提供組件沙箱、版本管理、權限控制、安全審核、錯誤隔離和運行時數據查詢能力，確保自定義組件在企業級場景下安全、穩定、可擴展。

---

### 11.2 自定義組件類型

| 類型          | 說明                                |
| ----------- | --------------------------------- |
| iframe 組件   | 通過 iframe 嵌入外部頁面，安全性高，集成簡單        |
| Schema 驅動組件 | 通過 Manifest 和 Schema 描述配置，不開放任意代碼 |
| 代碼型組件       | 支持 React / Vue 組件包，上傳後在沙箱中渲染      |

建議優先級：

```text
P0：iframe 組件
P0：Manifest + Schema 驅動組件
P1：React / Vue 代碼型組件
P2：組件市場與生態
```

---

### 11.3 自定義組件使用場景

| 類型     | 示例              |
| ------ | --------------- |
| 業務卡片   | 銷售排行榜、客服 SLA 卡片 |
| 複雜圖表   | 地圖、桑基圖、熱力圖、漏斗圖  |
| 流程組件   | 訂單流轉狀態、審批流程圖    |
| 大屏組件   | 3D 數字大屏、動態指標牆   |
| 行業組件   | 金融風控矩陣、供應鏈節點圖   |
| 外部系統組件 | iframe 嵌入第三方報表  |
| 交互組件   | 點擊篩選、鑽取分析、彈窗詳情  |

---

### 11.4 自定義組件 Manifest

每個自定義組件都需要提供 Manifest，用於描述組件如何被平台識別、配置和渲染。

示例：

```json
{
  "component_key": "sales_ranking_card",
  "name": "Sales Ranking Card",
  "display_name": "銷售排行榜",
  "description": "展示銷售人員業績排行",
  "version": "1.0.0",
  "category": "business",
  "framework": "react",
  "entry": "index.js",
  "thumbnail": "thumbnail.png",
  "author": "Data Team",
  "props_schema": {
    "title": {
      "type": "string",
      "label": "標題",
      "default": "銷售排行榜"
    },
    "limit": {
      "type": "number",
      "label": "展示數量",
      "default": 10
    },
    "show_avatar": {
      "type": "boolean",
      "label": "是否顯示頭像",
      "default": true
    }
  },
  "data_schema": {
    "required_fields": [
      {
        "field_key": "name",
        "label": "銷售姓名",
        "type": "string",
        "role": "dimension"
      },
      {
        "field_key": "amount",
        "label": "銷售金額",
        "type": "number",
        "role": "metric"
      }
    ]
  },
  "events": [
    {
      "name": "onItemClick",
      "label": "點擊排行項"
    }
  ],
  "permissions": {
    "allow_network": false,
    "allow_storage": false,
    "allow_iframe": false,
    "allow_export": true
  }
}
```

---

### 11.5 自定義組件數據綁定

自定義組件不應直接連接數據庫，也不應直接訪問外部 API。

正確方式：

```text
自定義組件聲明數據需求
→ Dashboard Builder 讓用戶做字段映射
→ 平台 Query Service 查詢數據
→ 平台將結果傳給組件
→ 組件只負責渲染展示
```

#### 推薦數據模式

```text
Component props.data = 平台查詢結果
```

優點：

1. 安全。
2. 權限可控。
3. 查詢邏輯統一。
4. 組件不需要知道資料庫細節。
5. 方便做審計和性能優化。

---

### 11.6 組件運行時上下文

平台需要為組件提供標準 Runtime Context。

示例：

```ts
type ComponentRuntimeContext = {
  dashboardId: string;
  widgetId: string;
  userId: string;
  tenantId: string;
  theme: "light" | "dark";
  locale: "zh-CN" | "en-US";
  permissions: string[];
  filters: Record<string, any>;
  data: any[];
  props: Record<string, any>;
  emit: (eventName: string, payload: any) => void;
  query: (queryConfig: QueryConfig) => Promise<any>;
};
```

組件可以：

1. 讀取平台傳入的數據。
2. 讀取自身 props 配置。
3. 讀取 Dashboard 全局篩選條件。
4. 發出交互事件。
5. 在受控範圍內請求平台 Query Service。

組件不可以：

1. 直接讀取其他組件數據。
2. 直接訪問密鑰。
3. 直接查詢資料庫。
4. 繞過權限訪問數據。
5. 任意訪問外部網絡。
6. 修改平台主應用 DOM。
7. 操作平台全局狀態。

---

### 11.7 組件事件聯動

自定義組件應支持事件機制，方便構建互動式 Dashboard。

常見事件：

| 事件             | 說明      |
| -------------- | ------- |
| onClick        | 點擊組件    |
| onItemClick    | 點擊某一條數據 |
| onFilterChange | 篩選條件變更  |
| onDrillDown    | 鑽取到下一層  |
| onRefresh      | 手動刷新    |
| onExport       | 導出數據    |

示例：

```text
銷售排行榜 onItemClick
→ 發出 sales_id = 123
→ Dashboard 全局 filter 更新
→ 訂單趨勢圖刷新
→ 客戶分布圖刷新
→ 明細表格刷新
```

---

### 11.8 組件沙箱與安全隔離

代碼型自定義組件必須在沙箱中運行。

推薦方案：

| 方案             | 說明               |
| -------------- | ---------------- |
| iframe sandbox | 安全隔離最強，推薦用於低可信組件 |
| Web Worker     | 適合計算邏輯，不適合 UI    |
| Micro Frontend | 適合企業內部可信組件       |
| Shadow DOM     | 適合樣式隔離，但安全隔離不足   |

建議策略：

> 外部或低可信組件使用 iframe sandbox；企業內部高可信組件可以使用 Micro Frontend，但仍需要權限控制、依賴隔離和錯誤隔離。

---

### 11.9 組件安全要求

默認禁止自定義組件：

1. 訪問完整 Token / API Key。
2. 訪問瀏覽器 localStorage 中的平台憑證。
3. 任意外部網絡請求。
4. 執行不受控腳本。
5. 修改主平台 DOM。
6. 讀取其他 Dashboard 或組件數據。
7. 繞過平台 Query Service 讀取數據。
8. 在日誌中輸出敏感數據。

組件上傳後需要經過：

1. 文件類型校驗。
2. Manifest 格式校驗。
3. 依賴包掃描。
4. 惡意代碼檢查。
5. 組件體積限制檢查。
6. 權限聲明檢查。
7. 人工審核。
8. 沙箱測試。

---

### 11.10 組件版本管理

每個組件可以存在多個版本。

示例：

```text
sales_ranking_card@1.0.0
sales_ranking_card@1.1.0
sales_ranking_card@2.0.0
```

Dashboard Widget 應綁定具體版本，而不是永遠使用最新版本。

示例：

```json
{
  "widget_id": "w_001",
  "component_key": "sales_ranking_card",
  "component_version": "1.0.0"
}
```

升級策略：

| 策略   | 說明                       |
| ---- | ------------------------ |
| 手動升級 | Dashboard 編輯者手動選擇升級      |
| 兼容升級 | 小版本自動升級，例如 1.0.0 → 1.0.1 |
| 強制升級 | 存在安全漏洞時由管理員強制升級          |

下架策略：

1. 已使用的 Dashboard 不應立即崩潰。
2. 已發布 Dashboard 可繼續使用舊版本。
3. 新 Dashboard 不能再添加已下架組件。
4. 管理員可以設置最終停用日期。

---

### 11.11 組件錯誤兜底

自定義組件渲染失敗時：

1. 不影響整個 Dashboard。
2. 該組件區域展示錯誤提示。
3. 記錄錯誤日誌。
4. 通知組件開發者。
5. Dashboard 查看者看到友好提示。
6. Dashboard 編輯者可以看到詳細錯誤信息。

錯誤提示示例：

```text
組件加載失敗，請聯繫管理員或組件開發者。
錯誤代碼：CUSTOM_COMPONENT_RENDER_ERROR
```

---

## 12. 組件庫

### 12.1 組件分類

| 分類    | 示例          |
| ----- | ----------- |
| 基礎圖表  | 柱狀圖、折線圖、餅圖  |
| 指標組件  | 指標卡、同比環比卡   |
| 業務組件  | 銷售排行、工單 SLA |
| 地圖組件  | 區域地圖、門店地圖   |
| 流程組件  | 流程圖、狀態流轉    |
| 嵌入組件  | iframe、外部報表 |
| 自定義組件 | 企業內部上傳組件    |

---

### 12.2 組件詳情頁

每個組件應有詳情頁。

字段包括：

| 信息     | 說明                    |
| ------ | --------------------- |
| 組件名稱   | 顯示名稱                  |
| 組件 key | 唯一標識                  |
| 版本列表   | 所有可用版本                |
| 作者     | 開發者                   |
| 描述     | 用途說明                  |
| 預覽圖    | thumbnail             |
| 使用次數   | 被多少 Dashboard 使用      |
| 權限聲明   | 需要哪些能力                |
| 更新記錄   | changelog             |
| 審核狀態   | 待審核 / 已發布 / 已拒絕 / 已下架 |

---

## 13. 權限與安全

### 13.1 RBAC 權限模型

建議角色：

| 角色                  | 權限                         |
| ------------------- | -------------------------- |
| Super Admin         | 全部權限                       |
| Admin               | 管理數據源、任務、用戶、Dashboard、組件審核 |
| Data Engineer       | 管理數據源、字段映射和同步任務            |
| Component Developer | 開發並提交自定義組件                 |
| Analyst             | 創建和編輯 Dashboard            |
| Viewer              | 只讀查看 Dashboard             |
| Security Reviewer   | 審核組件安全風險                   |

---

### 13.2 資源級權限

權限應覆蓋以下資源：

| 資源        | 權限動作                |
| --------- | ------------------- |
| 數據源       | 查看、新增、編輯、刪除、測試      |
| 同步任務      | 查看、新增、啟用、暫停、刪除、手動執行 |
| 數據表       | 查看、查詢、刪除            |
| Dashboard | 查看、創建、編輯、發布、分享、刪除   |
| 組件        | 查看、創建、上傳、審核、發布、下架   |
| 用戶        | 查看、新增、禁用、分配角色       |
| 系統配置      | 查看、編輯               |

---

### 13.3 密鑰安全

Token、API Key 等敏感信息必須加密存儲。

安全要求：

1. 密鑰不允許明文返回前端。
2. 密鑰字段展示時必須脫敏。
3. 後端日誌不得打印完整密鑰。
4. 支持定期輪換密鑰。
5. 支持憑證失效提醒。
6. 生產環境建議接入 KMS 或密鑰管理服務。

---

### 13.4 SSRF 防護

由於平台允許配置外部 API URL，因此需要防止 SSRF 風險。

要求：

1. 禁止訪問內網 IP。
2. 禁止訪問 metadata 地址。
3. 支持域名白名單。
4. 支持請求超時限制。
5. 支持最大響應體積限制。
6. 禁止自動跟隨不安全重定向。

---

### 13.5 審計日誌

需要記錄以下操作：

| 操作           | 示例                 |
| ------------ | ------------------ |
| 登錄           | 用戶登錄成功 / 失敗        |
| 數據源變更        | 新增、修改、刪除數據源        |
| 密鑰變更         | 更新 Token / API Key |
| 任務操作         | 啟用、暫停、手動執行同步       |
| Dashboard 操作 | 創建、編輯、發布、刪除        |
| 組件操作         | 上傳、提交審核、發布、下架      |
| 權限操作         | 分配角色、修改權限          |
| 數據操作         | 刪除數據表、修改字段映射       |

---

## 14. 任務監控與告警

### 14.1 同步任務日誌

每次同步任務都應生成執行記錄。

字段包括：

| 字段     | 說明             |
| ------ | -------------- |
| 任務 ID  | 關聯同步任務         |
| 數據源 ID | 關聯數據源          |
| 開始時間   | 任務開始時間         |
| 結束時間   | 任務結束時間         |
| 執行狀態   | 成功 / 失敗 / 部分成功 |
| 拉取條數   | 從接口獲取的數據量      |
| 入庫條數   | 成功寫入的數據量       |
| 失敗條數   | 寫入失敗數量         |
| 錯誤信息   | 失敗原因           |
| 重試次數   | 實際重試次數         |

---

### 14.2 告警規則

平台應支持以下告警：

1. 任務連續失敗 N 次。
2. 接口返回 401 / 403。
3. 接口超時。
4. 拉取數據量突然為 0。
5. 入庫失敗。
6. Token 即將過期。
7. 自定義組件渲染錯誤。
8. 自定義組件安全掃描失敗。

告警方式：

| 方式            | 優先級 |
| ------------- | --- |
| 站內通知          | P0  |
| Email         | P0  |
| Slack / Teams | P1  |
| Webhook       | P1  |

---

## 15. 系統架構建議

### 15.1 整體架構

```text
前端配置台 / Dashboard Builder
   |
   v
後端 API 服務
   |
   v
權限與審計服務
   |
   v
數據源管理服務
   |
   v
任務調度器 / Worker
   |
   v
Connector Runtime
   |
   v
數據處理與字段映射服務
   |
   v
數據庫 / 數據倉庫
   |
   v
Query Service
   |
   v
Dashboard Rendering Service
   |
   v
自定義組件 Runtime / Sandbox
```

---

### 15.2 模塊劃分

| 模塊                   | 職責                    |
| -------------------- | --------------------- |
| User & Auth Service  | 用戶、角色、權限、登錄           |
| Data Source Service  | 數據源配置、認證配置、接口測試       |
| Sync Job Service     | 任務配置、任務調度、執行記錄        |
| Connector Runtime    | 實際調用外部 API            |
| Data Mapping Service | 字段解析、字段映射、類型轉換        |
| Storage Service      | 原始數據和結構化數據存儲          |
| Query Service        | 為 Dashboard 和組件提供查詢能力 |
| Dashboard Service    | Dashboard、佈局、組件配置     |
| Component Registry   | 自定義組件註冊、版本、狀態管理       |
| Component Runtime    | 自定義組件沙箱渲染與數據傳入        |
| Audit Log Service    | 操作記錄與安全審計             |
| Notification Service | 告警與通知                 |

---

## 16. 數據庫表設計

### 16.1 data_sources

| 字段                    | 類型        | 說明                            |
| --------------------- | --------- | ----------------------------- |
| id                    | uuid      | 主鍵                            |
| name                  | varchar   | 數據源名稱                         |
| description           | text      | 描述                            |
| request_method        | varchar   | GET / POST                    |
| request_url           | text      | 接口地址                          |
| auth_type             | varchar   | none / bearer_token / api_key |
| auth_config_encrypted | text      | 加密後的認證配置                      |
| headers_config        | jsonb     | Header 配置                     |
| query_config          | jsonb     | Query 配置                      |
| body_config           | jsonb     | Body 配置                       |
| status                | varchar   | active / inactive             |
| created_by            | uuid      | 創建人                           |
| created_at            | timestamp | 創建時間                          |
| updated_at            | timestamp | 更新時間                          |

---

### 16.2 sync_jobs

| 字段                 | 類型        | 說明                                 |
| ------------------ | --------- | ---------------------------------- |
| id                 | uuid      | 主鍵                                 |
| data_source_id     | uuid      | 數據源 ID                             |
| name               | varchar   | 任務名稱                               |
| schedule_type      | varchar   | interval / cron                    |
| schedule_config    | jsonb     | 調度配置                               |
| sync_mode          | varchar   | full / incremental                 |
| incremental_config | jsonb     | 增量配置                               |
| write_mode         | varchar   | insert / upsert / replace / append |
| is_enabled         | boolean   | 是否啟用                               |
| last_run_at        | timestamp | 最近執行時間                             |
| next_run_at        | timestamp | 下次執行時間                             |
| created_at         | timestamp | 創建時間                               |
| updated_at         | timestamp | 更新時間                               |

---

### 16.3 sync_job_runs

| 字段             | 類型        | 說明                                           |
| -------------- | --------- | -------------------------------------------- |
| id             | uuid      | 主鍵                                           |
| sync_job_id    | uuid      | 任務 ID                                        |
| status         | varchar   | running / success / failed / partial_success |
| started_at     | timestamp | 開始時間                                         |
| finished_at    | timestamp | 結束時間                                         |
| fetched_count  | int       | 拉取條數                                         |
| inserted_count | int       | 入庫條數                                         |
| failed_count   | int       | 失敗條數                                         |
| error_message  | text      | 錯誤信息                                         |
| execution_logs | jsonb     | 詳細執行日誌                                       |

---

### 16.4 data_mappings

| 字段                 | 類型        | 說明     |
| ------------------ | --------- | ------ |
| id                 | uuid      | 主鍵     |
| data_source_id     | uuid      | 數據源 ID |
| target_table_name  | varchar   | 目標表名   |
| primary_key_config | jsonb     | 主鍵配置   |
| field_mappings     | jsonb     | 字段映射   |
| created_at         | timestamp | 創建時間   |
| updated_at         | timestamp | 更新時間   |

---

### 16.5 dashboards

| 字段            | 類型        | 說明                           |
| ------------- | --------- | ---------------------------- |
| id            | uuid      | 主鍵                           |
| name          | varchar   | Dashboard 名稱                 |
| description   | text      | 描述                           |
| layout_config | jsonb     | 佈局配置                         |
| visibility    | varchar   | private / team / public      |
| status        | varchar   | draft / published / archived |
| created_by    | uuid      | 創建人                          |
| created_at    | timestamp | 創建時間                         |
| updated_at    | timestamp | 更新時間                         |

---

### 16.6 dashboard_widgets

| 字段                  | 類型        | 說明                                     |
| ------------------- | --------- | -------------------------------------- |
| id                  | uuid      | 主鍵                                     |
| dashboard_id        | uuid      | Dashboard ID                           |
| component_source    | varchar   | system / custom / iframe               |
| component_key       | varchar   | 組件 key                                 |
| component_version   | varchar   | 組件版本                                   |
| widget_type         | varchar   | chart / table / metric / text / custom |
| title               | varchar   | 組件標題                                   |
| query_config        | jsonb     | 查詢配置                                   |
| props_config        | jsonb     | 組件配置                                   |
| data_binding_config | jsonb     | 數據綁定配置                                 |
| event_config        | jsonb     | 事件聯動配置                                 |
| visual_config       | jsonb     | 視覺配置                                   |
| position_config     | jsonb     | 位置與大小                                  |
| created_at          | timestamp | 創建時間                                   |
| updated_at          | timestamp | 更新時間                                   |

---

### 16.7 custom_components

| 字段            | 類型        | 說明                                                  |
| ------------- | --------- | --------------------------------------------------- |
| id            | uuid      | 主鍵                                                  |
| component_key | varchar   | 組件唯一標識                                              |
| name          | varchar   | 組件英文名稱                                              |
| display_name  | varchar   | 顯示名稱                                                |
| description   | text      | 描述                                                  |
| category      | varchar   | 分類                                                  |
| owner_id      | uuid      | 開發者                                                 |
| status        | varchar   | draft / reviewing / published / rejected / archived |
| created_at    | timestamp | 創建時間                                                |
| updated_at    | timestamp | 更新時間                                                |

---

### 16.8 custom_component_versions

| 字段                   | 類型        | 說明                            |
| -------------------- | --------- | ----------------------------- |
| id                   | uuid      | 主鍵                            |
| component_id         | uuid      | 組件 ID                         |
| version              | varchar   | 版本號                           |
| manifest             | jsonb     | 組件 Manifest                   |
| bundle_url           | text      | 組件包地址                         |
| thumbnail_url        | text      | 預覽圖                           |
| changelog            | text      | 更新說明                          |
| security_scan_result | jsonb     | 安全掃描結果                        |
| review_status        | varchar   | pending / approved / rejected |
| published_at         | timestamp | 發布時間                          |
| created_at           | timestamp | 創建時間                          |

---

## 17. API 設計示例

### 17.1 創建數據源

```http
POST /api/data-sources
```

請求示例：

```json
{
  "name": "Order API",
  "description": "訂單數據接口",
  "request_method": "GET",
  "request_url": "https://api.example.com/orders",
  "auth_type": "bearer_token",
  "auth_config": {
    "token": "xxxxx"
  },
  "headers_config": {
    "Content-Type": "application/json"
  },
  "query_config": {
    "page_size": 100
  }
}
```

---

### 17.2 測試數據源

```http
POST /api/data-sources/test
```

返回示例：

```json
{
  "success": true,
  "status_code": 200,
  "response_time_ms": 342,
  "sample_data": [
    {
      "id": "order_001",
      "amount": 99.9,
      "status": "paid"
    }
  ],
  "detected_fields": [
    {
      "path": "id",
      "type": "string"
    },
    {
      "path": "amount",
      "type": "number"
    },
    {
      "path": "status",
      "type": "string"
    }
  ]
}
```

---

### 17.3 創建同步任務

```http
POST /api/sync-jobs
```

請求示例：

```json
{
  "data_source_id": "ds_001",
  "name": "每小時同步訂單",
  "schedule_type": "cron",
  "schedule_config": {
    "cron": "0 * * * *"
  },
  "sync_mode": "incremental",
  "incremental_config": {
    "field": "updated_at",
    "operator": ">",
    "value": "{{last_sync_time}}"
  },
  "write_mode": "upsert"
}
```

---

### 17.4 查詢圖表數據

```http
POST /api/query
```

請求示例：

```json
{
  "table": "orders",
  "dimensions": ["status"],
  "metrics": [
    {
      "field": "amount",
      "aggregation": "sum",
      "alias": "total_amount"
    }
  ],
  "filters": [
    {
      "field": "created_at",
      "operator": ">=",
      "value": "2026-06-01"
    }
  ],
  "sort": [
    {
      "field": "total_amount",
      "direction": "desc"
    }
  ],
  "limit": 10
}
```

---

### 17.5 上傳自定義組件

```http
POST /api/custom-components
```

請求示例：

```json
{
  "component_key": "sales_ranking_card",
  "display_name": "銷售排行榜",
  "description": "展示銷售人員業績排行",
  "category": "business",
  "version": "1.0.0",
  "manifest": {}
}
```

---

### 17.6 提交組件審核

```http
POST /api/custom-components/{component_id}/submit-review
```

---

### 17.7 發布組件

```http
POST /api/custom-components/{component_id}/versions/{version_id}/publish
```

---

### 17.8 獲取組件庫

```http
GET /api/component-library
```

返回示例：

```json
{
  "components": [
    {
      "component_key": "sales_ranking_card",
      "display_name": "銷售排行榜",
      "version": "1.0.0",
      "category": "business",
      "thumbnail_url": "https://example.com/thumbnail.png"
    }
  ]
}
```

---

### 17.9 組件運行時查詢數據

```http
POST /api/component-runtime/query
```

請求示例：

```json
{
  "dashboard_id": "dash_001",
  "widget_id": "widget_001",
  "query_config": {
    "table": "orders",
    "dimensions": ["sales_name"],
    "metrics": [
      {
        "field": "amount",
        "aggregation": "sum",
        "alias": "sales_amount"
      }
    ],
    "sort": [
      {
        "field": "sales_amount",
        "direction": "desc"
      }
    ],
    "limit": 10
  }
}
```

---

## 18. 非功能需求

### 18.1 性能

| 指標             | 要求             |
| -------------- | -------------- |
| 普通 API 查詢響應    | 3 秒內           |
| Dashboard 首屏加載 | 5 秒內           |
| 同步任務觸發延遲       | 1 分鐘內          |
| 單次同步最大數據量      | MVP 可先設定 10 萬條 |
| 圖表查詢超時         | 默認 30 秒        |
| 自定義組件渲染超時      | 建議 5 秒內        |

---

### 18.2 可用性

1. 核心服務可用性目標：99.5% 以上。
2. 任務執行失敗後支持自動重試。
3. 任務失敗不影響整個平台可用。
4. Dashboard 查詢失敗時展示明確錯誤信息。
5. 自定義組件失敗不影響整個 Dashboard。

---

### 18.3 擴展性

1. 接入層應設計為 Connector 架構。
2. 未來可擴展 OAuth2、Webhook、JDBC、SFTP、Google Sheet 等數據源。
3. 可視化組件應支持插件化擴展。
4. 查詢服務可從普通數據庫演進到 OLAP 引擎或數據倉庫。
5. 自定義組件支持版本化、分組、審核和多租戶分發。

---

### 18.4 安全性

1. 所有接口必須經過身份認證。
2. 敏感憑證加密存儲。
3. 外部 API 請求需要防止 SSRF。
4. 操作日誌不可被普通用戶刪除。
5. 不同租戶數據必須隔離。
6. 自定義組件必須沙箱隔離。
7. 自定義組件不得繞過平台權限和 Query Service。
8. 生產環境必須使用 HTTPS。

---

## 19. MVP 與版本規劃

### 19.1 Phase 1：基礎數據平台閉環

目標：完成 API 接入、同步、入庫、展示。

包含：

1. 數據源配置。
2. Bearer Token / API Key。
3. 測試連接。
4. 手動同步。
5. 定時同步。
6. 原始 JSON 存儲。
7. 字段映射。
8. 結構化數據表。
9. 基礎 Dashboard。
10. 基礎圖表。

---

### 19.2 Phase 2：Dashboard Builder 與企業級能力

目標：支持業務用戶自定義搭建 Dashboard。

包含：

1. 拖拽式 Dashboard Builder。
2. 組件庫。
3. 右側配置面板。
4. 數據綁定。
5. 樣式配置。
6. 事件聯動。
7. RBAC 細粒度權限。
8. 任務監控。
9. 同步失敗告警。
10. 審計日誌。

---

### 19.3 Phase 3：高級版自定義組件

目標：支持企業開發者開發和發布自定義組件。

包含：

1. iframe 組件。
2. Manifest + Schema 驅動組件。
3. 組件註冊。
4. 組件審核。
5. 組件版本管理。
6. 組件數據綁定。
7. 組件事件聯動。
8. 組件錯誤隔離。
9. 組件沙箱。
10. React / Vue 代碼型組件。

---

### 19.4 Phase 4：智能化與生態化

目標：讓平台從數據看板平台升級為數據應用平台。

包含：

1. 組件市場。
2. 自然語言生成 Dashboard。
3. AI 數據分析。
4. 自動洞察。
5. 報表訂閱與定時發送。
6. 多租戶組件分發。
7. 自動化安全掃描。
8. 企業內部組件生態。

---

## 20. 驗收標準

### 20.1 數據源接入驗收

1. 用戶可以創建 REST API 數據源。
2. 用戶可以配置 Bearer Token。
3. 用戶可以配置 API Key，並選擇 Header 或 Query 傳入。
4. 點擊測試連接後，可以看到請求結果和返回樣例。
5. 認證失敗時，前端能展示明確錯誤。

---

### 20.2 數據同步驗收

1. 用戶可以手動觸發同步。
2. 用戶可以設置定時同步。
3. 任務可以按照設置時間自動執行。
4. 同步結果可以寫入數據庫。
5. 同步成功和失敗均有執行記錄。
6. 任務失敗後可以查看錯誤原因。

---

### 20.3 數據映射驗收

1. 平台可以解析 JSON 返回樣例。
2. 用戶可以選擇字段並映射到內部字段。
3. 支持字段類型配置。
4. 支持配置唯一鍵。
5. 支持 Upsert 寫入策略。

---

### 20.4 Dashboard 驗收

1. 用戶可以創建 Dashboard。
2. 用戶可以拖拽添加組件。
3. 組件可以選擇數據表作為數據來源。
4. 組件支持維度、指標、聚合、篩選配置。
5. Dashboard 可以保存、預覽和發布。
6. 不同權限用戶只能看到自己有權限的 Dashboard。

---

### 20.5 自定義組件驗收

1. 開發者可以創建自定義組件。
2. 開發者可以上傳組件 Manifest。
3. 平台可以校驗 Manifest 格式。
4. 平台可以保存組件版本。
5. 開發者可以提交組件審核。
6. 管理員可以通過或拒絕組件。
7. 審核通過後，組件進入組件庫。
8. Dashboard 編輯者可以拖拽使用自定義組件。
9. 可以配置自定義組件 props。
10. 可以完成自定義組件數據綁定。
11. 自定義組件渲染失敗不影響整個 Dashboard。
12. 新版本發布後，不影響已發布 Dashboard。
13. 已下架組件不能被新 Dashboard 添加。

---

## 21. 主要風險與應對

| 風險               | 說明                   | 應對策略                |
| ---------------- | -------------------- | ------------------- |
| 外部 API 格式不穩定     | 字段變更可能導致同步失敗         | 保存原始 JSON，增加字段變更提示  |
| Token 過期         | API 認證失敗             | 支持失敗告警和憑證更新         |
| 數據量過大            | 拉取和查詢變慢              | 分頁同步、增量同步、查詢緩存      |
| API 限流           | 第三方接口限制請求頻率          | 任務限速、重試退避           |
| 字段映射複雜           | 嵌套 JSON、數組難處理        | MVP 先支持常見 JSON Path |
| 權限混亂             | 數據可能被未授權用戶看到         | 資源級權限和審計日誌          |
| 憑證洩露             | Token / API Key 泄漏風險 | 加密存儲、脫敏展示、禁止日誌打印    |
| 自定義組件安全風險        | 可能執行惡意代碼             | 沙箱隔離、安全掃描、權限審核      |
| 組件版本破壞 Dashboard | 新版本不兼容舊配置            | Dashboard 綁定具體組件版本  |
| 組件性能差            | 影響 Dashboard 加載      | 渲染超時、錯誤隔離、性能監控      |

---

## 22. 最終結論

本平台應建設為一個企業級低代碼數據應用平台，核心鏈路如下：

```text
外部系統 API 接入
→ Bearer Token / API Key 認證
→ 手動 / 定時同步
→ 原始數據保存
→ 字段映射與結構化入庫
→ 統一 Query Service
→ Dashboard Builder
→ 系統組件與自定義組件展示
→ 權限、安全、審計、監控
```

第一階段應優先打通「API 接入 → 數據同步 → 入庫 → 基礎 Dashboard」的完整閉環。

第二階段加強 Dashboard Builder，使業務用戶可以通過拖拽和配置方式自定義搭建看板。

第三階段建設自定義組件能力，支持企業開發者通過 Manifest、Schema、沙箱和版本管理機制開發並發布企業內部組件，讓平台從普通數據看板工具升級為真正的企業級數據應用平台。






