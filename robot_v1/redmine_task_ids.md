# Robot VLA v1 Redmine ID Record

Date: 2026-08-13
Parent issue: #41627
Parent subject: 新機器人 VLA 測試與實證項目 v1
Source markdown: D:/00_redmine/robot_v1/robot_v1.md

## Structure

### #41628 資料蒐集流程驗證

- Redmine: http://redmine.mirle.com.tw/issues/41628
- Tasks:
  - #41629 01. 確認 VR 或 teleoperation 工具可以控制機器人完成基本動作。
  - #41630 02. 確認錄製時包含必要 observation，例如相機影像、joint state、EEF pose、gripper state、robot mode。
  - #41631 03. 確認錄製時包含必要 action，例如 joint command、EEF delta、gripper command 或實際部署會使用的 action space。
  - #41632 04. 確認資料頻率，例如 camera FPS、state Hz、action Hz，並記錄降頻或同步策略。
  - #41633 05. 確認每筆 episode 都有任務名稱、操作者、日期、機器人版本、場景版本、成功/失敗標記，並依固定資料夾結構保存 raw data、video、metadata、logs。
  - #41634 06. 確認錄製後可立即做 smoke check，例如影片可播放、metadata 可讀取、必要 topic/message count 不為 0，且原始資料唯讀保存不直接覆寫。
  - #41635 07. 先錄製少量 pilot episodes，確認資料可轉換與可訓練後，再擴大量產資料。

### #41636 資料清洗與訓練格式轉換驗證

- Redmine: http://redmine.mirle.com.tw/issues/41636
- Tasks:
  - #41637 01. 定義目標資料格式，例如 LeRobot v2.x、OpenPI dataset、ACT HDF5 或自訂 parquet/video 結構。
  - #41638 02. 建立 raw data 到 training format 的轉換腳本，避免手動搬檔或手動改欄位。
  - #41639 03. 定義 observation schema，例如 image keys、state vector、language instruction、task id。
  - #41640 04. 定義 action schema，例如 action dimension、左右手順序、gripper range、delta/absolute 定義。
  - #41641 05. 定義 episode 過濾規則，例如失敗資料、急停資料、時間不同步資料、缺影像資料。
  - #41642 06. 定義資料切分規則，例如 train/validation split、依日期或場景切分，避免資料洩漏。
  - #41643 07. 執行轉換後資料驗證，確認 episode 數、frame 數、video 數、parquet/HDF5 數一致。
  - #41644 08. 執行可視化抽查，確認影像、state、action 在同一時間點語意一致。
  - #41645 09. 記錄轉換版本、輸入資料版本與輸出 dataset version。

### #41646 VLA 模型訓練驗證

- Redmine: http://redmine.mirle.com.tw/issues/41646
- Tasks:
  - #41647 01. 選定第一版模型路線，例如 ACT、pi0、pi05、SmolVLA，並記錄選擇原因。
  - #41648 02. 確認 train config 的 observation/action schema 與 dataset 完全一致。
  - #41649 03. 確認 action horizon、state dimension、image keys、language instruction 與部署需求一致。
  - #41650 04. 先執行 dataloader smoke test，確認單 batch 可讀取並可進模型 forward。
  - #41651 05. 先執行短步數 smoke training，確認 loss 可計算、checkpoint 可保存、log 可讀取。
  - #41652 06. 執行正式 v1 training，記錄 dataset version、config name、commit、seed、硬體與訓練時間。
  - #41653 07. 建立 checkpoint 命名規則，避免 smoke checkpoint 與正式 checkpoint 混用。
  - #41654 08. 執行離線 validation，例如 loss curve、action replay、sample rollout visualization。
  - #41655 09. 匯出或整理部署需要的 checkpoint、normalization stats、model config 與推論程式參數。

### #41656 實機推論與部署驗證

- Redmine: http://redmine.mirle.com.tw/issues/41656
- Tasks:
  - #41657 01. 確認部署平台類型，例如 x86 GPU server、Jetson/arm64、CPU-only 或分散式 policy server。
  - #41658 02. 確認 Python、CUDA、PyTorch/JAX、模型框架與依賴套件在部署平台可安裝。
  - #41659 03. 確認 checkpoint、config、normalization stats、tokenizer 或 language embedding 檔案完整。
  - #41660 04. 確認推論輸入與訓練 observation 完全一致，包含影像尺寸、相機順序、state 維度與 normalization。
  - #41661 05. 確認推論輸出與機器人 action interface 完全一致，包含 action dimension、左右手順序、delta/absolute、gripper scale。
  - #41662 06. 加入 action 安全檢查，例如 NaN/Inf 檢查、delta clamp、速度限制、workspace limit、gripper range clip。
  - #41663 07. 加入推論頻率監控，例如 policy latency、control loop Hz、丟包或 timeout 處理。
  - #41664 08. 先執行 dry-run，不發送到真實馬達，只記錄 observation 到 action 的完整路徑。
  - #41665 09. 執行低速實機測試，保留人工接管與急停人員。
  - #41666 10. 記錄每次實機推論的 checkpoint、資料版本、任務版本、成功/失敗原因與影片。

## Notes

- `#41627` 頁面顯示 39 open subtasks，該數字包含 descendant tasks。
- 抽查 `#41628` 已確認 `#41629-#41635` 是掛在 `#41628` 底下的 subtasks。
- `redmind_create_robot_v1.py` 已加入 `--id-record`，正式建立或略過既有項目後會輸出這份 ID 對照檔。
