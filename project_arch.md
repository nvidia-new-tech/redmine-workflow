# Project Architecture Notes

Date: 2026-08-11

## Robot VLA v1 Redmine 建立流程

目前以 `robot_v1/robot_v1.md` 作為新機器人 VLA 測試與實證項目的架構來源，並用 `redmind_create_robot_v1.py` 將文件中的四個階段同步建立到 Redmine。

## 目前目標

先依據 v1 架構逐步把工作完成，確認資料蒐集、資料清洗、模型訓練、實機推論四個階段可以形成最小可行閉環。後續會依實際執行狀況，再回頭增刪改 checklist、完成指標、查核點與 Redmine 任務。

## Redmine 層級

預設父議題：`#41627`

父議題下只應有四個主要子議題：

- `資料蒐集流程驗證`
- `資料清洗與訓練格式轉換驗證`
- `VLA 模型訓練驗證`
- `實機推論與部署驗證`

每個主要子議題底下，再依該章節的 `### Checklist` 建立 task。Checklist task 不應直接掛在 `#41627` 底下。

目前已知主要子議題 ID：

- `#41628`：資料蒐集流程驗證
- `#41636`：資料清洗與訓練格式轉換驗證
- `#41646`：VLA 模型訓練驗證
- `#41656`：實機推論與部署驗證

## Script 用法

主要腳本：`redmind_create_robot_v1.py`

本地預覽，不登入 Redmine、不查詢、不建立：

```powershell
python .\redmind_create_robot_v1.py --dry-run
```

只解析 Markdown 並列出各主要子議題的 task 數量：

```powershell
python .\redmind_create_robot_v1.py --plan-only
```

實際建立 Redmine 議題：

```powershell
python .\redmind_create_robot_v1.py
```

可指定父議題：

```powershell
python .\redmind_create_robot_v1.py --parent 41627
```

可指定 Markdown 來源：

```powershell
python .\redmind_create_robot_v1.py --markdown .\robot_v1\robot_v1.md
```

正式建立或略過既有項目後，預設會輸出 Redmine ID 對照檔：

```powershell
python .\redmind_create_robot_v1.py --id-record .\robot_v1\redmine_task_ids.md
```

若只想建立 Redmine，不想更新 ID 對照檔：

```powershell
python .\redmind_create_robot_v1.py --no-id-record
```

## Redmine 設定

預設值：

- Project: `9bc`
- Tracker: `Feature`
- Assignee: `<< me >>`
- Parent issue: `#41627`

帳密建議使用環境變數，避免出現在命令歷史：

```powershell
$env:REDMINE_USERNAME = "你的帳號"
$env:REDMINE_PASSWORD = "你的密碼"
```

## 建立邏輯

`redmind_create_robot_v1.py` 會解析 `robot_v1/robot_v1.md` 中固定的四個章節：

- `## 1. 資料蒐集`
- `## 2. 資料清洗`
- `## 3. 訓練`
- `## 4. 實機推論`

每個章節會抓取 `### Checklist` 底下的 checkbox 項目，並建立為該階段子議題底下的 task。

建立 Redmine issue 後，腳本不信任 Redmine redirect URL 回傳的 issue id。因為 Redmine 可能導回 `back_url=/issues/41627`，所以腳本會重新讀取指定父議題頁面，從子議題列表回查 subject 相符的真實 issue id，再用該 id 建立下一層 task。

建立或略過既有項目時，腳本會累積實際使用的 issue id，最後寫入 `robot_v1/redmine_task_ids.md`。這份檔案作為 Redmine ID 快照，用來追蹤目前架構與 Redmine 實際任務的對應關係。

## 目前 task 數量

依目前 `robot_v1.md` 內容：

- 資料蒐集流程驗證：7 tasks
- 資料清洗與訓練格式轉換驗證：9 tasks
- VLA 模型訓練驗證：9 tasks
- 實機推論與部署驗證：10 tasks

## 維護原則

後續要增刪改 Redmine task 時，優先修改 `robot_v1/robot_v1.md` 的對應章節 checklist，再重新執行腳本。

調整原則：

- 新增 checklist 項目：會在對應子議題下新增 task。
- 修改 checklist 文字：可能被視為新的 subject，需注意 Redmine 上是否已有舊 task。
- 刪除 checklist 項目：腳本不會自動刪除 Redmine 既有 task，需人工確認後處理。
- 搬移 task parent：腳本不會自動搬移既有 Redmine task，避免誤動已建立資料。

## 已知注意事項

先前曾因 Redmine redirect URL 導回 `#41627`，造成建立後回報 id 都是 `#41627`，並讓 checklist task 錯掛在父議題底下。現在腳本已改成建立後回查父議題子清單來取得真實 id。

若 Redmine 上仍有舊的錯掛 task，需要人工刪除或調整 parent。腳本目前只負責建立與略過同名既有項目，不負責刪除或搬移。
