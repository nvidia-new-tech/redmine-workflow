# redmine_task_create_robot_v2.py 快速指南

## 核心概念

`redmine_task_create_robot_v2.py` 通過 **JSON 配置** 讀取要建立的章節計畫，然後在 **Markdown** 檔案中查找對應的 `## 章節標題`，提取其下的 `### Checklist` 項目，最後在 Redmine 中建立對應的子議題與 task。

---

## 三秒快速上手

### 使用場景 A：只要 4 個主階段（7+9+9+10=35 個 task）

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run
```

### 使用場景 B：包含共通前置條件（7+7+9+9+10=42 個 task）

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run
```

---

## 檔案結構全景

```
d:\00_redmine\
│
├── redmine_task_create_robot_v2.py          # 主程式（v2 版本）
├── robot_v1\robot_v1.md                     # Markdown 來源（5 個章節）
│
├── section_plans\                           # JSON 配置目錄
│   ├── template.json                        # 通用模板
│   ├── robot_v1.json                        # 4 階段配置（預設）
│   └── robot_v1_full.json                   # 5 階段配置（含前置條件）
│
└── 文檔\
    ├── README.md                            # 總體文檔（已更新）
    ├── USAGE_SCENARIOS.md                   # 詳細情境指南
    └── CONFIG_COMPARISON.md                 # 配置對比與選擇指南
```

---

## 關鍵差異

### robot_v1.json vs robot_v1_full.json

| 配置 | 章節數 | Task 數 | 包含內容 | 適用情景 |
|------|-------|--------|---------|---------|
| `robot_v1.json` | 4 | 35 | 只有 4 個主階段 | 快速建立標準項目 |
| `robot_v1_full.json` | **5** | **42** | 共通前置條件 + 4 主階段 | 需要完整追蹤硬體前置條件 |

### robot_v1.md 中的對應章節

```
JSON section_heading            Markdown 檔案中的 ## 標題
────────────────────────────────────────────────────────
"共通前置條件"                  ## 共通前置條件
"1. 資料蒐集"                   ## 1. 資料蒐集
"2. 資料清洗"                   ## 2. 資料清洗
"3. 訓練"                       ## 3. 訓練
"4. 實機推論"                   ## 4. 實機推論
```

---

## robot_v1.md 中的共通前置條件

**位置**：`robot_v1.md` 第 39-63 行

**內容**：
```markdown
## 共通前置條件

### Checklist

- [ ] 確認機器人本體、末端工具、夾爪、相機、控制主機與網路連線可正常啟動。
- [ ] 確認安全機制可用，包含急停、限速、軟體 stop、手動接管與安全區域。
- [ ] 確認控制介面與資料介面，...
- [ ] 確認時間同步方式，...
- [ ] 定義第一版實證任務，...
- [ ] 定義資料保存位置、命名規則、版本規則與不可覆寫的原始資料區。
- [ ] 定義模型與資料的版本對應方式，...
```

**如何使用**：
- 用 `robot_v1_full.json` 讓 v2 脚本自動提取這 7 個 task
- 在 Redmine 中生成「共通前置條件驗證」子議題，包含 7 個 task

---

## 命令行速查

### 基本命令

```powershell
# 4 階段版本 - 預覽
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run

# 5 階段版本 - 預覽（含共通前置條件）
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run

# 實際建立（選擇你要的版本）
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json
```

### 常用選項

```powershell
# 列出計畫（不登入）
--plan-only

# 本地預覽（不登入）
--dry-run

# 自訂 Markdown 檔案
--markdown .\path\to\your.md

# 自訂輸出 ID 對照檔
--id-record .\path\to\output.md

# 不輸出 ID 對照檔
--no-id-record

# 改變 Tracker 類型
--tracker "Bug"

# 允許建立重複名稱的議題
--allow-duplicate
```

---

## 選擇配置的決策流程

```
問題：需要追蹤機器人前置條件嗎？
      （硬體驗證、安全確認、時間同步等）

  ├─ YES → 用 robot_v1_full.json ✓
  │        • 生成 5 個子議題（含前置條件）
  │        • 42 個 task
  │        • 完整項目管理可視化
  │
  └─ NO  → 用 robot_v1.json ✓
           • 生成 4 個子議題（只有主階段）
           • 35 個 task
           • 快速建立，專注軟體 VLA 管道
```

---

## 實際執行示例

### 示例 1：快速預覽完整版本

```powershell
cd d:\00_redmine
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --plan-only
```

**輸出**：
```
Parent issue: #41627
- 共通前置條件驗證: 7 tasks
- 資料蒐集流程驗證: 7 tasks
- 資料清洗與訓練格式轉換驗證: 9 tasks
- VLA 模型訓練驗證: 9 tasks
- 實機推論與部署驗證: 10 tasks
```

### 示例 2：乾運行（本地預覽不登入）

```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run
```

**輸出**（前 20 行）：
```
DRY RUN: local preview only...
Parent issue: #41627
- Section: 共通前置條件驗證
  - Task: 01. 確認機器人本體、末端工具、夾爪、相機、控制主機與網路連線可正常啟動。
  - Task: 02. 確認安全機制可用，包含急停、限速、軟體 stop、手動接管與安全區域。
  - Task: 03. 確認控制介面與資料介面，...
  ...
```

### 示例 3：實際建立到 Redmine

```powershell
# 設定帳密環境變數
$env:REDMINE_USERNAME = "your_username"
$env:REDMINE_PASSWORD = "your_password"

# 執行建立
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json
```

**結果**：
- Redmine #41627 下建立 5 個子議題
- 每個子議題下自動建立對應的 task
- 生成 `redmine_task_ids.md` 記錄所有 ID 映射

---

## 故障排除

### 錯誤 1：找不到章節

```
ERROR: 找不到章節: ## 共通前置條件
```

**原因**：JSON 中的 `section_heading` 與 Markdown 檔案不匹配

**解決**：
1. 開啟 `robot_v1.md` 檢查實際的 `##` 標題
2. 複製完整文本到 JSON（注意大小寫和空格）
3. 驗證 JSON 格式

### 錯誤 2：JSON 格式錯誤

```
ERROR: JSON 缺少必要欄位: sections
```

**原因**：JSON 結構不正確

**解決**：
1. 使用 VS Code 的 JSON 驗證
2. 對比 `template.json` 或 `robot_v1.json`
3. 確保有 `parent_issue_id` 和 `sections` 欄位

### 錯誤 3：Redmine 連線失敗

```
ERROR: Redmine 登入失敗，請確認帳號密碼或網路權限
```

**原因**：認證或網路問題

**解決**：
1. 確認環境變數設定：
   ```powershell
   $env:REDMINE_USERNAME
   $env:REDMINE_PASSWORD
   ```
2. 檢查網路連接
3. 確認帳號密碼正確

---

## 進階用法

詳見 [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md) 與 [CONFIG_COMPARISON.md](CONFIG_COMPARISON.md)

**主要主題**：
- 多個不同的 JSON 配置
- 分離前置條件到獨立父議題
- 自訂 Markdown 章節順序
- 新增自訂 Markdown 檔案

---

## 文檔導航

| 檔案 | 內容 |
|------|------|
| [README.md](README.md) | 總體介紹與基本用法 |
| **[本檔](QUICK_START.md)** | **快速上手指南** |
| [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md) | 5 個詳細情境 + 除錯技巧 |
| [CONFIG_COMPARISON.md](CONFIG_COMPARISON.md) | 配置對比與選擇指南 |

---

## 環境設定一次性記錄

在 PowerShell Profile 中設定環境變數（可選）：

```powershell
# 編輯 Profile
notepad $PROFILE

# 或用 VS Code
code $PROFILE
```

添加以下內容：
```powershell
$env:REDMINE_USERNAME = "your_username"
$env:REDMINE_PASSWORD = "your_password"
```

保存後重啟 PowerShell 無需每次重複設定。

---

## 常見問題 Q&A

**Q：v2 與 v1 的區別？**
A：v1 硬編碼 4 個階段；v2 從 JSON 配置讀取，可支援任意數量的章節。

**Q：能否混用 v1 和 v2？**
A：可以。v1 保留不動，v2 作為新項目或需要靈活配置時的選擇。

**Q：如何只建立某些階段？**
A：在 JSON 的 `sections` 陣列中只保留需要的章節。

**Q：如何改變 Redmine 中子議題的名稱？**
A：修改 JSON 中的 `subject` 欄位（不影響 `section_heading`）。

**Q：能否用於其他 Markdown 檔案？**
A：可以。用 `--markdown` 參數指定路徑。Markdown 必須有 `## 章節標題` 和 `### Checklist` 結構。

---

## 一句話總結

**robot_v1.json**（4 階段）vs **robot_v1_full.json**（5 階段 + 前置條件）：根據是否需要正式追蹤硬體/安全檢查清單選擇即可。

