# Redmine Weekly Subtask Tool

建立 `Task #36463` 底下的週報 SubTask。

---

## 📚 文檔導航

**快速上手？**→ [**QUICK_START.md**](QUICK_START.md) ⚡

| 檔案 | 用途 |
|------|------|
| [README.md](README.md) | 本檔 - 工具總覽與完整參考 |
| [**QUICK_START.md**](QUICK_START.md) | 🚀 快速指南（3 秒上手） |
| [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md) | 📋 5 種使用情境詳解 |
| [CONFIG_COMPARISON.md](CONFIG_COMPARISON.md) | 🔍 配置對比與決策指南 |

---

```powershell
python -m pip install -r requirements.txt
```

## 使用

建議用環境變數提供帳密，避免把密碼寫進程式或命令歷史。

```powershell
$env:REDMINE_USERNAME = "victorlin"
$env:REDMINE_PASSWORD = "你的密碼"
python .\redmine_create_subtask.py W0803 --year 2026
```

先測試登入、表單解析與是否已有同名子任務，但不建立：

```powershell
python .\redmine_create_subtask.py W0803 --year 2026 --dry-run
```

程式會把 `W0803` 解析為 `2026-08-03`，並將 due date 設為同週週五 `2026-08-07`。
建立時會送出這些 Redmine 表單欄位：

- `Subject`: `W0803`
- `Start date`: `2026-08-03`
- `Due date`: `2026-08-07`
- `Assigned to`: `<< me >>`
- `Parent task`: `#36463`

---

# Robot VLA v1 Redmine 任務建立工具

建立新機器人 VLA 測試與實證項目 v1 的父議題、子議題與 checklist task。基於 `robot_v1/robot_v1.md` 的架構自動生成 Redmine 項目。

**檔案名稱：** `redmine_create_robot_v1.py`（注意正確拼寫，不是 `redmind`）

## 使用

建議用環境變數提供帳密，避免把密碼寫進程式或命令歷史。

```powershell
$env:REDMINE_USERNAME = "你的帳號"
$env:REDMINE_PASSWORD = "你的密碼"
```

### 本地預覽（不登入 Redmine）

列出將建立的樹狀結構，僅本地解析，不打任何 Redmine 請求：

```powershell
python .\redmine_create_robot_v1.py --dry-run
```

### 只解析 Markdown

列出各階段任務數量，不登入 Redmine，也不建立：

```powershell
python .\redmine_create_robot_v1.py --plan-only
```

### 實際建立任務

登入 Redmine 並建立或略過既有項目，最後輸出 ID 對照檔：

```powershell
python .\redmine_create_robot_v1.py
```

建立完成後會在 `robot_v1/redmine_task_ids.md` 輸出 Redmine issue ID 對照表。

### 自訂選項

指定父議題 ID（預設 `41627`）：

```powershell
python .\redmine_create_robot_v1.py --parent 41627
```

指定 Markdown 來源（預設 `robot_v1/robot_v1.md`）：

```powershell
python .\redmine_create_robot_v1.py --markdown .\robot_v1\robot_v1.md
```

指定 ID 對照檔輸出位置（預設 `robot_v1/redmine_task_ids.md`）：

```powershell
python .\redmine_create_robot_v1.py --id-record .\robot_v1\redmine_task_ids.md
```

建立後不輸出 ID 對照檔：

```powershell
python .\redmine_create_robot_v1.py --no-id-record
```

## Redmine 層級結構

預設父議題：`#41627`（新機器人 VLA 測試與實證項目 v1）

建立四個主要子議題，各自包含對應的 checklist task：

- `#41628` 資料蒐集流程驗證 → 7 個 task
- `#41636` 資料清洗與訓練格式轉換驗證 → 9 個 task
- `#41646` VLA 模型訓練驗證 → 9 個 task
- `#41656` 實機推論與部署驗證 → 10 個 task

## 預設設定

- **Project**: `9bc`
- **Tracker**: `Feature`
- **Assignee**: `<< me >>`
- **Parent issue**: `#41627`

完整文檔見 `project_arch.md`。

---

# Redmine Task Create Robot v2（通用版本）

**檔案名稱：** `redmine_task_create_robot_v2.py`

通用的 Redmine 任務建立工具，支援從 JSON 配置檔案讀取父議題 ID 與章節規劃。可重複使用於不同項目。

## 安裝

```powershell
python -m pip install -r requirements.txt
```

## 使用

基本命令格式：

```powershell
python .\redmine_task_create_robot_v2.py --ID <PARENT_ISSUE_ID> --SECTION_PLAN <CONFIG.json>
```

環境變數設定（避免硬編碼密碼）：

```powershell
$env:REDMINE_USERNAME = "你的帳號"
$env:REDMINE_PASSWORD = "你的密碼"
```

### 本地預覽（不登入 Redmine）

列出將建立的樹狀結構，僅本地解析，不打任何 Redmine 請求：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run
```

### 只解析 Markdown 並列出計畫

驗證 JSON 配置與 Markdown 匹配，列出任務數量，不登入 Redmine：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --plan-only
```

### 實際建立任務

登入 Redmine 並建立或略過既有項目，最後輸出 ID 對照檔：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json
```

## JSON 配置檔案格式

放在 `section_plans/` 目錄內，例如 `section_plans/robot_v1.json`：

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

**必須欄位：**
- `parent_issue_id`: Redmine 父議題 ID（命令行 `--ID` 會覆蓋此值）
- `sections`: 陣列，每個元素必須包含 `subject` 和 `section_heading`

**可選欄位：**
- `tracker`: Tracker 名稱（預設 `Feature`，命令行 `--tracker` 會覆蓋）

## 自訂選項

指定 Markdown 來源（預設搜尋 `./robot_v1/robot_v1.md`）：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --markdown .\path\to\custom.md
```

指定 ID 對照檔輸出位置（預設 `./redmine_task_ids.md`）：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --id-record .\path\to\output.md
```

建立後不輸出 ID 對照檔：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --no-id-record
```

指定 Tracker 名稱：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --tracker "Bug"
```

允許建立同名議題（預設會略過已存在的同名議題）：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --allow-duplicate
```

## 預設設定

- **Project**: `9bc`（硬編碼）
- **Tracker**: `Feature`（JSON 可指定，命令行可覆蓋）
- **Assignee**: `<< me >>`（自動選擇登入者）

## 使用情境與進階設定

詳細的使用情境、多種配置範例與除錯技巧請見 [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md)：

- **情境 1**：只生成 4 個主階段（預設）
- **情境 2**：包含共通前置條件（完整版本）→ **5 個階段，42 個 task**
- **情境 3**：分離共通前置條件到獨立父議題
- **情境 4**：自訂 Markdown 章節順序
- **情境 5**：新增自訂 Markdown 檔案

### 快速常用情境

#### 只生成 4 個主階段
```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run
```
結果：35 個 task（7+9+9+10）

#### 包含共通前置條件（完整版本）
```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run
```
結果：42 個 task（7+7+9+9+10）

## 配置範例

### robot_v1 項目

使用 `section_plans/robot_v1.json` 配置對應 `robot_v1/robot_v1.md`：

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run
```

### 建立新項目

1. 在 `section_plans/` 創建新 JSON 檔案，參考 `section_plans/template.json`
2. 編寫或引用 Markdown 來源檔案
3. 執行：

```powershell
python .\redmine_task_create_robot_v2.py --ID <YOUR_PARENT_ID> --SECTION_PLAN .\section_plans\your_config.json --markdown .\path\to\your.md --dry-run
```

---

## 選擇 v1 或 v2

| 需求 | 推薦使用 |
|------|---------|
| Robot VLA v1 專案（4 個固定階段）| `redmine_create_robot_v1.py` |
| 一般通用任務建立（自訂 JSON 配置）| `redmine_task_create_robot_v2.py` |
| 快速原型或實驗新項目| `redmine_task_create_robot_v2.py` |