# 配置檔案對比與選擇指南

## 可用配置檔案一覽

| 檔案名稱 | 任務數 | 包含內容 | 用途 |
|---------|-------|---------|------|
| `section_plans/template.json` | 因選項而定 | 空模板，自訂選項 | 建立新項目時參考 |
| `section_plans/robot_v1.json` | 35 | 4 個主階段 | **標準 Robot v1 項目** |
| `section_plans/robot_v1_full.json` | 42 | 共通前置條件 + 4 主階段 | Robot v1 完整版本 |

---

## 三種配置的 Markdown 對應

### robot_v1.json（4 階段，35 個 task）

```
Markdown 章節                    → Redmine 子議題（Checklist task 數）
─────────────────────────────────────────────────────────────────
## 1. 資料蒐集                  → 資料蒐集流程驗證 (7)
## 2. 資料清洗                  → 資料清洗與訓練格式轉換驗證 (9)
## 3. 訓練                      → VLA 模型訓練驗證 (9)
## 4. 實機推論                  → 實機推論與部署驗證 (10)
────────────────────────────────────────────────────────────────
總計：35 個 task
```

**使用場景**：
- 快速建立 Robot v1 標準項目
- 不需要前置條件驗證
- 聚焦於 4 個主要研發階段

**命令**：
```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json --dry-run
```

---

### robot_v1_full.json（5 階段，42 個 task）

```
Markdown 章節                    → Redmine 子議題（Checklist task 數）
─────────────────────────────────────────────────────────────────
## 共通前置條件                  → 共通前置條件驗證 (7)
## 1. 資料蒐集                  → 資料蒐集流程驗證 (7)
## 2. 資料清洗                  → 資料清洗與訓練格式轉換驗證 (9)
## 3. 訓練                      → VLA 模型訓練驗證 (9)
## 4. 實機推論                  → 實機推論與部署驗證 (10)
────────────────────────────────────────────────────────────────
總計：42 個 task
```

**使用場景**：
- 需要驗證共通前置條件（機器人硬體、安全、時間同步等）
- 前置條件通過後再進行 4 個主階段
- 從總體項目管理角度追蹤

**命令**：
```powershell
python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1_full.json --dry-run
```

---

## 何時選用哪種配置

### 選擇 `robot_v1.json`（4 階段）

✅ 適用情況：
- 機器人硬體已驗證就緒
- 共通前置條件以其他方式追蹤（口頭、郵件、會議記錄）
- 專注於軟體 VLA 管道的 4 個階段
- 團隊規模較小，前置條件簡單

❌ 不適用：
- 需要正式追蹤前置條件檢查清單
- 硬體驗證步驟複雜，需要 Redmine 記錄
- 想要「一站式」完整項目追蹤

### 選擇 `robot_v1_full.json`（5 階段）

✅ 適用情況：
- 需要正式追蹤前置條件（機器人硬體、安全、時間同步）
- 跨團隊協作，前置條件檢查點影響後續研發
- 項目管理要求完整的檢查清單可視化
- 想要一個統一的 Redmine 專案結構

❌ 不適用：
- 前置條件已被確認且無需進一步追蹤
- 希望保持 Redmine 精簡，只記錄核心研發任務

---

## 切換或混合使用

### 情境 A：先用 robot_v1.json，後續追加前置條件

1. **第一階段**（已完成）：用 `robot_v1.json` 建立 4 個子議題
   ```powershell
   python .\redmine_task_create_robot_v2.py --ID 41627 --SECTION_PLAN .\section_plans\robot_v1.json
   ```

2. **第二階段**（新增）：用單獨的父議題建立前置條件
   ```powershell
   python .\redmine_task_create_robot_v2.py --ID 41700 --SECTION_PLAN .\section_plans\robot_v1_prerequisites.json
   ```

**Redmine 結構**：
```
#41627 新機器人 VLA 測試與實證項目 v1
├─ #41628 資料蒐集流程驗證 → tasks
├─ #41636 資料清洗與訓練格式轉換驗證 → tasks
├─ #41646 VLA 模型訓練驗證 → tasks
└─ #41656 實機推論與部署驗證 → tasks

#41700 機器人前置條件驗證
└─ #41701 共通前置條件驗證 → tasks
```

---

### 情境 B：已用 robot_v1.json，現在想加入前置條件

方案 1（推薦）：將前置條件加為獨立父議題（同上面的情境 A）

方案 2：如果想要放在同一個父議題 #41627 下，需要：
1. 手動在 Redmine 中建立一個新的子議題「共通前置條件驗證」
2. 複製 robot_v1.md 的「## 共通前置條件」章節内容到該子議題描述
3. 手動建立 7 個 task 或使用另一個指令行呼叫（見情境 3：分離前置條件）

---

## JSON 檔案結構詳解

### robot_v1.json
```json
{
  "parent_issue_id": "41627",           ← 對應 Redmine 現有父議題
  "tracker": "Feature",                 ← 所有子議題的 Tracker 類型
  "sections": [                         ← 章節陣列（順序決定 Redmine 子議題順序）
    {
      "subject": "資料蒐集流程驗證",    ← Redmine 中顯示的子議題名稱
      "section_heading": "1. 資料蒐集"  ← Markdown 檔案中的章節標題
    },
    ...
  ]
}
```

**注意**：`section_heading` 必須與 Markdown 中的 `##` 行完全相同（包含數字與空格）

---

## 快速決策樹

```
┌─ 是否需要追蹤機器人前置條件（硬體、安全、時間同步等）？
│
├─ YES → 使用 robot_v1_full.json
│        （5 階段，42 個 task）
│        └─ 包含共通前置條件驗證
│
└─ NO  → 使用 robot_v1.json
         （4 階段，35 個 task）
         └─ 只關注軟體 VLA 管道
```

---

## 修改配置檔案的常見需求

### 需求 1：改變 Tracker 類型
```json
{
  "tracker": "Bug"  // 改為 "Bug" 或其他 Tracker 類型
}
```
或用命令行覆蓋：
```powershell
--tracker "Bug"
```

### 需求 2：改變章節名稱
```json
{
  "subject": "修改後的子議題名稱"  // 自訂 Redmine 中的名稱
}
```

### 需求 3：改變章節順序
```json
{
  "sections": [
    { "subject": "...", "section_heading": "4. 實機推論" },
    { "subject": "...", "section_heading": "3. 訓練" },
    { "subject": "...", "section_heading": "2. 資料清洗" },
    { "subject": "...", "section_heading": "1. 資料蒐集" }
  ]
}
```

### 需求 4：只建立某些階段（例如只有資料蒐集和訓練）
```json
{
  "sections": [
    { "subject": "資料蒐集流程驗證", "section_heading": "1. 資料蒐集" },
    { "subject": "VLA 模型訓練驗證", "section_heading": "3. 訓練" }
  ]
}
```

---

## 命令行快速參考

| 目的 | 命令 |
|------|------|
| 預覽（不登入） | `--dry-run` |
| 驗證計畫 | `--plan-only` |
| 實際建立 | （不加任何 flag） |
| 使用完整版本（含前置條件） | `--SECTION_PLAN .\section_plans\robot_v1_full.json` |
| 自訂 Markdown 檔案 | `--markdown .\path\to\file.md` |
| 自訂輸出 ID 對照檔 | `--id-record .\path\to\output.md` |
| 不輸出 ID 對照檔 | `--no-id-record` |
| 允許重複建立同名議題 | `--allow-duplicate` |
