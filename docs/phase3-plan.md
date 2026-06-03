# Phase 3：高級版自定義組件 — 開發計劃

**目標**：Manifest 驅動 + iframe 沙箱 + 版本管理 + 審核流程
**預估工期**：8-10 週
**依賴**：Phase 2 完成
**狀態**：規劃中

---

## 1. 任務總覽

| 編號 | 任務 | 預估工期 | 負責人 | 依賴 |
|------|------|----------|--------|------|
| P3-1 | 組件註冊數據模型 | 1 天 | 後端 | Phase 2 |
| P3-2 | Manifest 校驗服務 | 1.5 天 | 後端 | P3-1 |
| P3-3 | 組件上傳與存儲 | 1.5 天 | 後端+前端 | P3-1 |
| P3-4 | 安全掃描服務 | 2 天 | 後端 | P3-3 |
| P3-5 | 組件審核流程 | 2 天 | 後端+前端 | P3-2, P3-4 |
| P3-6 | 組件版本管理 | 1.5 天 | 後端 | P3-1 |
| P3-7 | iframe 沙箱渲染 | 2 天 | 前端 | Phase 2 |
| P3-8 | 組件 Runtime Context | 1.5 天 | 前端 | P3-7 |
| P3-9 | Schema 驅動配置面板 | 2 天 | 前端 | P3-2 |
| P3-10 | 組件數據綁定器 | 2 天 | 後端+前端 | P3-8 |
| P3-11 | 組件事件系統 | 2 天 | 前端 | P3-8 |
| P3-12 | 組件錯誤隔離 | 1 天 | 前端 | P3-7 |
| P3-13 | 組件庫管理頁 | 2 天 | 前端+後端 | P3-5 |
| P3-14 | React 代碼型組件支持 | 3 天 | 前端+後端 | P3-7 |

---

## 2. 關鍵設計要點

### 2.1 組件 Manifest JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["component_key", "name", "version"],
  "properties": {
    "component_key": { "type": "string", "pattern": "^[a-z][a-z0-9_]*$" },
    "name": { "type": "string", "minLength": 1 },
    "display_name": { "type": "string" },
    "description": { "type": "string" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "category": { "type": "string" },
    "framework": { "type": "string", "enum": ["react", "vue", "none"] },
    "entry": { "type": "string" },
    "thumbnail": { "type": "string" },
    "author": { "type": "string" },
    "props_schema": { "$ref": "#/$defs/propsSchema" },
    "data_schema": { "$ref": "#/$defs/dataSchema" },
    "events": { "type": "array", "items": { "$ref": "#/$defs/event" } },
    "permissions": { "$ref": "#/$defs/permissions" }
  }
}
```

### 2.2 組件沙箱架構

```
┌──────────────────────────────────────────────┐
│              Dashboard 主應用                   │
│  ┌────────────────────────────────────────┐  │
│  │         iframe sandbox                 │  │
│  │  srcdoc = 組件 HTML bundle             │  │
│  │  sandbox = "allow-scripts allow-same-origin" │ │
│  │  + CSP header 限制網絡請求                    │  │
│  │                                        │  │
│  │  ←── postMessage ──→  Runtime Context  │  │
│  │  ←── props.data ───→  查詢結果數據       │  │
│  │  ←── emit event ───→  事件系統          │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  錯誤邊界 <ErrorBoundary>                      │
│  → 組件渲染失敗時顯示錯誤提示，不影響主應用       │
└──────────────────────────────────────────────┘
```

### 2.3 組件版本管理策略

```
component_key: sales_ranking_card
  ├─ version 1.0.0  (published)
  │   └─ dashboard widget w_001 binds to this version
  ├─ version 1.1.0  (published)  ← 小版本兼容升級
  │   └─ 可被新 dashboard 引用
  └─ version 2.0.0  (draft/reviewing)
      └─ 不兼容升級，需重新審核
```

版本兼容策略：
- **修訂版本 (patch, x.y.Z)**：自動升級，功能增強，不破壞配置
- **小版本 (minor, x.Y.z)**：兼容升級，需通知用戶
- **主版本 (major, X.y.z)**：不兼容升級，需手動確認

### 2.4 安全掃描流程

```
組件包上傳
  → 文件類型校驗 (.js, .css, .png, .html)
  → 總體積檢查 (≤ 5MB)
  → 依賴包掃描 (npm audit / pip audit)
  → 惡意代碼模式匹配 (eval, setTimeout string, document.cookie, etc.)
  → 權限聲明檢查 (permissions 字段與實際行為對比)
  → iframe sandbox 測試運行 (自動測試)
  → 生成安全掃描報告
  → 提交人工審核
```

---

## 3. 新增/修改 API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | /api/v1/custom-components | 創建/上傳組件 |
| GET | /api/v1/custom-components | 組件列表 |
| GET | /api/v1/custom-components/{id} | 組件詳情 |
| PUT | /api/v1/custom-components/{id} | 更新組件 |
| DELETE | /api/v1/custom-components/{id} | 刪除組件 |
| POST | /api/v1/custom-components/{id}/submit-review | 提交審核 |
| POST | /api/v1/custom-components/{id}/versions/{vid}/publish | 發布版本 |
| GET | /api/v1/custom-components/{id}/versions | 版本列表 |
| POST | /api/v1/custom-components/{id}/scan | 觸發安全掃描 |
| GET | /api/v1/component-library | 組件庫（已發布） |
| POST | /api/v1/component-runtime/query | 組件運行時查詢 |
| GET | /api/v1/component-security-reports/{id} | 安全掃描報告 |

---

## 4. 組件 SDK (前端)

提供一個輕量 SDK，方便組件開發者集成：

```typescript
// 組件開發者只需導入 SDK
import { createComponent } from '@gdplatform/component-sdk';

const MyComponent = createComponent({
  name: 'sales_ranking_card',
  
  // 渲染函數 — 接收 props 和 data
  render: (props, data, context) => {
    return <div>
      <h2>{props.title}</h2>
      {data.map(item => <RankItem {...item} />)}
    </div>;
  },
  
  // 事件觸發
  onItemclick: (item) => {
    context.emit('onItemClick', { sales_id: item.id });
  },
});
```

SDK 暴露能力：
- `props` — 組件配置屬性
- `data` — 查詢結果數據
- `context` — Dashboard/用戶/主題/語言/權限
- `emit(eventName, payload)` — 發出事件
- `query(config)` — 受控查詢（需在 manifest 中允許）

---

## 5. 前端新增頁面/組件

| 組件/頁面 | 說明 |
|------|------|
| 組件開發工作台 | 新建組件、編輯 Manifest、上傳 bundle |
| 組件詳情頁 | 版本列表、審核狀態、使用次數 |
| 組件審核管理頁 | 待審核列表、通過/拒絕、審覈意見 |
| 組件庫瀏覽頁 | 所有已發布組件，分類瀏覽 |
| Schema 驅動表單 | 根據 manifest.props_schema 自動渲染配置表單 |
| iframe 沙箱渲染器 | 在 Dashboard Builder 和查看模式中渲染自定義組件 |
| 組件錯誤邊界 | 渲染失敗時的兜底 UI |

---

## 6. 驗收標準

- [ ] 開發者可以創建自定義組件，填寫 Manifest
- [ ] 平台校驗 Manifest 格式和必填字段
- [ ] 組件包可以上傳並存儲到對象存儲
- [ ] 安全掃描成功執行並生成報告
- [ ] 組件審核流程完整（提交 → 審核 → 發布/拒絕）
- [ ] 組件有完整版本管理，Dashboard 綁定具體版本
- [ ] iframe 沙箱可以正常渲染自定義組件
- [ ] 組件可以通過 Runtime Context 獲取數據和觸發事件
- [ ] Schema 驅動配置面板自動生成
- [ ] 組件渲染失敗不影響 Dashboard 主應用
- [ ] 新版本發布後，已發布 Dashboard 不受影響
- [ ] 已下架組件不能被新 Dashboard 添加

---

## 7. 風險與注意事項

| 風險 | 應對 |
|------|------|
| iframe postMessage 安全 | 驗證來源域名、序列化限制、不傳遞敏感數據 |
| 組件 bundle 過大 | 上傳時壓縮、CDN 分發、體積限制 |
| 組件依賴衝突 | 隔離執行環境（iframe）、限制第三方依賴 |
| 審核人力瓶頸 | 自動化安全掃描覆蓋率高於 80% |
| 版本升級破壞性 | 強制綁定版本、兼容策略、升級預檢 |
