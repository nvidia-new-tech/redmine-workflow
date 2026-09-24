# 📊 redmine_task_create_robot_v2.py 完整方案總結

## 🎯 用戶問題

**在 robot_v1.md 下之前還有其他 checklist（共通前置條件），生成 subtask，這樣的情境怎麼使用 redmine_task_create_robot_v2.py？**

---

## ✅ 解決方案

**使用 `robot_v1_full.json` 配置 + v2 脚本 = 完美解決**

### 快速命令

```powershell
# 預覽（本地，不登入）
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run

# 驗證計畫
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --plan-only

# 實際建立
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json
```

### 結果

✅ 自動在 Redmine 中建立：

```
Parent Issue #41627: 新機器人 VLA 測試與實證項目 v1
├─ 共通前置條件驗證             [7 tasks]
├─ 資料蒐集流程驗證             [7 tasks]
├─ 資料清洗與訓練格式轉換驗證    [9 tasks]
├─ VLA 模型訓練驗證             [9 tasks]
└─ 實機推論與部署驗證           [10 tasks]

總計：42 個 task（7+7+9+9+10）
```

---

## 🔑 核心原理

### robot_v1.md 中的 5 個章節

```markdown
## 共通前置條件           ← 包含 7 個 checklist 項目
  ### Checklist
    - [ ] 確認機器人本體...
    - [ ] 確認安全機制...
    ...

## 1. 資料蒐集           ← 包含 7 個 checklist 項目
  ### Checklist
    - [ ] 確認 VR 或 teleoperation...
    ...

## 2. 資料清洗           ← 包含 9 個 checklist 項目
  ...

## 3. 訓練              ← 包含 9 個 checklist 項目
  ...

## 4. 實機推論          ← 包含 10 個 checklist 項目
  ...
```

### robot_v1_full.json 中的對應配置

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

### v2 脚本工作流程

```
robot_v1_full.json
    ↓
讀取 5 個 sections
    ↓
逐一在 robot_v1.md 中查找對應的 ## 章節標題
    ↓
從每個章節提取 ### Checklist 下的所有項目
    ↓
在 Redmine 中建立 5 個子議題 + 42 個 task
    ↓
輸出 redmine_task_ids.md 與 ID 對照表
```

---

## 📁 完整項目文件結構

```
d:\00_redmine\
│
├── 📜 主程式
│   ├── redmine_create_robot_v1.py       (v1，硬編碼 4 階段)
│   └── redmine_task_create_robot_v2.py  (v2，從 JSON 讀配置) ⭐
│
├── 📚 文檔 (已新增 3 個)
│   ├── README.md                        (總體介紹，已更新)
│   ├── QUICK_START.md                   (⚡ 快速上手)
│   ├── USAGE_SCENARIOS.md               (📋 5 種情境詳解)
│   ├── CONFIG_COMPARISON.md             (🔍 配置對比)
│   └── project_arch.md                  (舊版 v1 文檔)
│
├── 🗂️ JSON 配置 (section_plans/)
│   ├── template.json                    (通用模板)
│   ├── robot_v1.json                    (4 階段，預設)
│   └── robot_v1_full.json               (5 階段，含共通前置條件) ⭐
│
├── 📖 Markdown 來源
│   ├── robot_v1/robot_v1.md            (5 個章節的來源文件)
│   └── robot_v1/redmine_task_ids.md    (生成的 ID 對照表)
│
└── 其他
    ├── requirements.txt
    ├── redmine_create_subtask.py
    └── data/
```

---

## 🎨 兩種配置方案對比

### 方案 1：robot_v1.json（4 階段，35 個 task）

**用途**：快速建立標準項目，不需要前置條件驗證

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run
```

**結果**：
```
- 資料蒐集流程驗證: 7 tasks
- 資料清洗與訓練格式轉換驗證: 9 tasks
- VLA 模型訓練驗證: 9 tasks
- 實機推論與部署驗證: 10 tasks
```

### 方案 2：robot_v1_full.json（5 階段，42 個 task）⭐ 推薦

**用途**：完整項目追蹤，包含硬體前置條件

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run
```

**結果**：
```
- 共通前置條件驗證: 7 tasks                    ← 新增！
- 資料蒐集流程驗證: 7 tasks
- 資料清洗與訓練格式轉換驗證: 9 tasks
- VLA 模型訓練驗證: 9 tasks
- 實機推論與部署驗證: 10 tasks
```

---

## 🚀 常見使用情境

### 情境 1：包含共通前置條件（常見）

```powershell
# 本地預覽
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run

# 實際建立
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json
```

### 情境 2：只要 4 個主階段

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run
```

### 情境 3：自訂新項目

1. 在 `section_plans/` 建立新 JSON（參考 `template.json`）
2. 準備 Markdown 文件
3. 執行：
```powershell
python .\redmine_task_create_robot_v2.py --ID <YOUR_ID> --SECTION_PLAN .\section_plans\your_config.json --markdown .\your.md --dry-run
```

---

## 📖 文檔導航

| 文檔 | 內容 | 讀者 |
|------|------|------|
| [README.md](README.md) | 總體介紹與完整參考 | 所有人 |
| [**QUICK_START.md**](QUICK_START.md) | ⚡ 3 秒快速上手 | **新用戶必讀** |
| [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md) | 📋 5 種詳細情境 + 除錯 | 進階用戶 |
| [CONFIG_COMPARISON.md](CONFIG_COMPARISON.md) | 🔍 配置對比與決策指南 | 需要選擇配置 |

---

## 💡 快速決策樹

```
是否需要追蹤機器人硬體前置條件？
│
├─ YES（需要正式記錄前置檢查）
│  └─ 使用 robot_v1_full.json
│     └─ 生成 5 個子議題，42 個 task
│
└─ NO（前置條件已驗證或另外追蹤）
   └─ 使用 robot_v1.json
      └─ 生成 4 個子議題，35 個 task
```

---

## 🔧 快速命令速查

```powershell
# 預覽 - 本地不登入
--dry-run

# 驗證計畫 - 列出任務數量
--plan-only

# 實際建立到 Redmine
（無需添加 flag）

# 自訂 Markdown 檔案
--markdown .\path\to\your.md

# 自訂輸出 ID 對照檔
--id-record .\path\to\output.md

# 不輸出 ID 對照檔
--no-id-record

# 改變 Tracker 類型
--tracker "Bug"

# 允許重複建立同名議題
--allow-duplicate
```

---

## ⚙️ 環境設定

```powershell
$env:REDMINE_USERNAME = "your_username"
$env:REDMINE_PASSWORD = "your_password"
```

---

## ✨ 核心優勢

✅ **無需硬編碼**：所有配置在 JSON，易於版本控制  
✅ **可重用性**：同一腳本支援多個項目和配置  
✅ **靈活性**：輕易添加、移除或改變章節順序  
✅ **安全性**：--dry-run 預覽，確認無誤再建立  
✅ **完整追蹤**：自動生成 ID 對照檔，便於後續查詢  

---

## 🎓 學習路線

**第 1 步**：閱讀 [QUICK_START.md](QUICK_START.md)（5 分鐘）  
**第 2 步**：執行 `--dry-run` 預覽（1 分鐘）  
**第 3 步**：執行 `--plan-only` 驗證（1 分鐘）  
**第 4 步**：實際建立（需登入）  
**進階**：參考 [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md) 學習其他情境  

---

## 📞 常見問題

**Q：我已經用 robot_v1.json 建立了 4 個階段，現在想加共通前置條件怎麼辦？**

A：方案 A（推薦）：
- 為前置條件建立新的父議題（例如 #41700）
- 用新 JSON 配置單獨建立：
  ```powershell
  python .\redmine_task_create_robot_v2.py --ID 41700 --SECTION_PLAN .\section_plans\robot_v1_prerequisites.json
  ```

方案 B：
- 手動在 #41627 下建立「共通前置條件驗證」子議題
- 手動複製 Markdown 中的 Checklist 項目

**Q：v2 和 v1 的區別是什麼？**

A：
- **v1**：硬編碼 4 個階段，快速但不靈活
- **v2**：從 JSON 讀配置，支援任意數量章節，可重用於多個項目

**Q：能否同時建立多個 JSON 配置？**

A：是的，可以：
```powershell
# 先建立前置條件
python .\redmine_task_create_robot_v2.py --ID 41700 --SECTION_PLAN .\section_plans\robot_v1_prerequisites.json

# 再建立主階段
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json
```

---

## 🎉 總結

**現在你可以：**

1. ✅ 用 `robot_v1_full.json` 一次建立包含共通前置條件的完整項目
2. ✅ 用 `--dry-run` 預覽不登入 Redmine
3. ✅ 用 `--plan-only` 驗證計畫
4. ✅ 用靈活的 JSON 配置支援多個項目
5. ✅ 自動生成 ID 對照檔便於後續查詢

**下一步**：打開 [QUICK_START.md](QUICK_START.md) 開始使用！

