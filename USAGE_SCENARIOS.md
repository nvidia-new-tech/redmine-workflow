# redmine_task_create_robot_v2.py 使用情境指南

## 情境概述

`redmine_task_create_robot_v2.py` 支援多種使用情境，通過修改 JSON 配置檔案來適應不同的 Markdown 結構。

---

## 情境 1: 只生成 4 個主階段（預設）

### JSON 配置
```json
{
  "parent_issue_id": "41627",
  "tracker": "Feature",
  "sections": [
    {
      "subject": "資料蒐集流程驗證",
      "section_heading": "1. 資料蒐集"
    },
    {
      "subject": "資料清洗與訓練格式轉換驗證",
      "section_heading": "2. 資料清洗"
    },
    {
      "subject": "VLA 模型訓練驗證",
      "section_heading": "3. 訓練"
    },
    {
      "subject": "實機推論與部署驗證",
      "section_heading": "4. 實機推論"
    }
  ]
}
```

### 命令執行
```powershell
# 本地預覽
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run

# 實際建立
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json
```

### 結果
- 父議題: #41627
- 建立 4 個子議題（各自對應 Markdown 的 4 個章節）
- 每個子議題下建立對應數量的 task（7+9+9+10=35 個）

---

## 情境 2: 包含共通前置條件（完整版本）

`robot_v1.md` 中的 `## 共通前置條件` 部分有獨立的 Checklist（7 項）。

### JSON 配置
```json
{
  "parent_issue_id": "41627",
  "tracker": "Feature",
  "sections": [
    {
      "subject": "共通前置條件驗證",
      "section_heading": "共通前置條件"
    },
    {
      "subject": "資料蒐集流程驗證",
      "section_heading": "1. 資料蒐集"
    },
    {
      "subject": "資料清洗與訓練格式轉換驗證",
      "section_heading": "2. 資料清洗"
    },
    {
      "subject": "VLA 模型訓練驗證",
      "section_heading": "3. 訓練"
    },
    {
      "subject": "實機推論與部署驗證",
      "section_heading": "4. 實機推論"
    }
  ]
}
```

### 命令執行
```powershell
# 本地預覽
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run

# 列出計畫
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --plan-only

# 實際建立
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json
```

### 結果
- 父議題: #41627
- 建立 5 個子議題（共通前置條件 + 4 個主階段）
- 總共 42 個 task（7+7+9+9+10=42 個）

| 子議題 | Task 數 | Markdown 對應 |
|--------|---------|-------------|
| 共通前置條件驗證 | 7 | `## 共通前置條件` |
| 資料蒐集流程驗證 | 7 | `## 1. 資料蒐集` |
| 資料清洗與訓練格式轉換驗證 | 9 | `## 2. 資料清洗` |
| VLA 模型訓練驗證 | 9 | `## 3. 訓練` |
| 實機推論與部署驗證 | 10 | `## 4. 實機推論` |

---

## 情境 3: 分離共通前置條件到獨立父議題

若共通前置條件應該是獨立的父議題，而 4 個主階段在另一個父議題下。

### JSON 配置（前置條件專用）
```json
{
  "parent_issue_id": "41700",
  "tracker": "Feature",
  "sections": [
    {
      "subject": "共通前置條件驗證",
      "section_heading": "共通前置條件"
    }
  ]
}
```

### JSON 配置（4 個主階段）
```json
{
  "parent_issue_id": "41627",
  "tracker": "Feature",
  "sections": [
    {
      "subject": "資料蒐集流程驗證",
      "section_heading": "1. 資料蒐集"
    },
    {
      "subject": "資料清洗與訓練格式轉換驗證",
      "section_heading": "2. 資料清洗"
    },
    {
      "subject": "VLA 模型訓練驗證",
      "section_heading": "3. 訓練"
    },
    {
      "subject": "實機推論與部署驗證",
      "section_heading": "4. 實機推論"
    }
  ]
}
```

### 命令執行
```powershell
# 先建立共通前置條件（父議題: 41700）
python .\redmine_task_create_robot_v2.py --ID 41700 --SECTION_PLAN .\section_plans\robot_v1_prerequisites.json

# 再建立 4 個主階段（父議題: 41627）
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json
```

### 結果
- 父議題 #41700：共通前置條件驗證 → 7 個 task
- 父議題 #41627：4 個主階段 → 35 個 task
- Redmine 結構中共通前置條件與主項目平行

---

## 情境 4: 自訂 Markdown 章節順序

若 Markdown 文件的章節順序不同或有其他章節需要包含。

### JSON 配置（自訂順序）
```json
{
  "parent_issue_id": "41627",
  "tracker": "Feature",
  "sections": [
    {
      "subject": "實機推論與部署驗證",
      "section_heading": "4. 實機推論"
    },
    {
      "subject": "VLA 模型訓練驗證",
      "section_heading": "3. 訓練"
    },
    {
      "subject": "資料清洗與訓練格式轉換驗證",
      "section_heading": "2. 資料清洗"
    },
    {
      "subject": "資料蒐集流程驗證",
      "section_heading": "1. 資料蒐集"
    }
  ]
}
```

### 結果
- Redmine 中建立的子議題順序會依照 JSON 的順序
- 每個子議題仍然會找到正確的 Markdown 章節並提取 Checklist

---

## 情境 5: 新增自訂 Markdown 檔案

若要使用不同的 Markdown 檔案（例如 `robot_v2.md`）。

### Markdown 結構要求
Markdown 檔案必須有以下結構：
```markdown
## 前置條件名稱

### Checklist

- [ ] 任務 1
- [ ] 任務 2
- [ ] 任務 3
```

### JSON 配置
```json
{
  "parent_issue_id": "41800",
  "tracker": "Feature",
  "sections": [
    {
      "subject": "V2 資料蒐集",
      "section_heading": "1. 資料蒐集 v2"
    },
    {
      "subject": "V2 模型訓練",
      "section_heading": "2. 訓練 v2"
    }
  ]
}
```

### 命令執行
```powershell
python .\redmine_task_create_robot_v2.py --ID 41800 --SECTION_PLAN .\section_plans\robot_v2.json --markdown .\robot_v2\robot_v2.md --dry-run
```

---

## 常見操作總結

| 操作 | 命令 |
|------|------|
| **預覽不登入** | `--dry-run` |
| **驗證計畫** | `--plan-only` |
| **實際建立** | （不加任何 flag） |
| **自訂 Markdown** | `--markdown .\path\to\file.md` |
| **自訂輸出位置** | `--id-record .\path\to\output.md` |
| **不輸出 ID 對照** | `--no-id-record` |
| **允許重複建立** | `--allow-duplicate` |
| **改變 Tracker** | `--tracker "Bug"` |

---

## 快速參考

### 已準備的配置檔案

```
section_plans/
├── template.json          # 通用模板
├── robot_v1.json          # Robot v1（4 階段，預設）
└── robot_v1_full.json     # Robot v1（共通前置條件 + 4 階段）
```

### 快速命令

```powershell
# Robot v1 標準版（4 階段，42 個 task）
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run

# Robot v1 完整版（共通前置條件 + 4 階段，42 個 task）
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run

# 新專案（自訂配置）
python .\redmine_task_create_robot_v2.py --ID <YOUR_ID> --SECTION_PLAN .\section_plans\your_config.json --dry-run
```

---

## JSON 配置欄位說明

| 欄位 | 必須 | 說明 | 範例 |
|------|------|------|------|
| `parent_issue_id` | ✅ | Redmine 父議題 ID，命令行 `--ID` 會覆蓋 | `"41627"` |
| `tracker` | ❌ | Tracker 名稱（預設 Feature），命令行 `--tracker` 會覆蓋 | `"Feature"` |
| `sections` | ✅ | 章節陣列，每個元素必須有 `subject` 和 `section_heading` | 見下方 |
| `subject` | ✅ | 在 Redmine 中顯示的子議題名稱 | `"資料蒐集流程驗證"` |
| `section_heading` | ✅ | 在 Markdown 檔案中的章節標題（必須完全匹配）| `"1. 資料蒐集"` |

---

## 除錯技巧

### 找不到章節錯誤

```
ERROR: 找不到章節: ## 1. 資料蒐集
```

**原因**：JSON 中的 `section_heading` 與 Markdown 檔案中的標題不完全匹配

**解決**：
1. 檢查 Markdown 文件中的實際標題
2. 使用 `grep` 確認：
```powershell
Select-String "^## " .\robot_v1\robot_v1.md
```
3. 複製正確的標題到 JSON 配置

### JSON 解析錯誤

```
ERROR: JSON 缺少必要欄位: sections
```

**原因**：JSON 格式錯誤或缺少必需欄位

**解決**：
1. 驗證 JSON 格式（使用線上工具或編輯器）
2. 確保有 `parent_issue_id` 和 `sections` 欄位
3. 每個 section 都有 `subject` 和 `section_heading`

### Redmine 建立失敗

若 `--plan-only` 通過但實際建立失敗，檢查：
1. Redmine 帳號密碼（環境變數 `REDMINE_USERNAME`、`REDMINE_PASSWORD`）
2. 父議題 ID 是否存在
3. Tracker 名稱是否正確
4. 網路連接是否正常
