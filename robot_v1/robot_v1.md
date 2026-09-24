# 新機器人 VLA 測試與實證項目 v1

## 目標

新機器人到位後，先用一套通用流程確認 VLA 從資料蒐集、資料清洗、模型訓練到實機推論的最小可行閉環。v1 版本先分成四個階段，每個階段都需要有 checklist、完成指標與查核點，方便後續拆成 Redmine 任務追蹤。

## Redmine 上傳建議

- 父議題：新機器人 VLA 測試與實證項目 v1
- 子議題 1：資料蒐集流程驗證
- 子議題 2：資料清洗與訓練格式轉換驗證
- 子議題 3：VLA 模型訓練驗證
- 子議題 4：實機推論與部署驗證
- 每個子議題描述建議包含：目的、輸入資料、執行 checklist、完成指標、查核點、產出物、風險與待釐清事項。

## Redmine ID 對照

更新日期：2026-08-13

- 父議題：#41627 新機器人 VLA 測試與實證項目 v1
- 子議題：#41628 資料蒐集流程驗證，Task ID #41629-#41635
- 子議題：#41636 資料清洗與訓練格式轉換驗證，Task ID #41637-#41645
- 子議題：#41646 VLA 模型訓練驗證，Task ID #41647-#41655
- 子議題：#41656 實機推論與部署驗證，Task ID #41657-#41666

完整 task ID 對照請見 `robot_v1/redmine_task_ids.md`。Redmine `#41627` 頁面顯示 39 個 subtasks，實際上是四個主要子議題加上其 descendant tasks；抽查 `#41628` 已確認 task #41629-#41635 掛在 `#41628` 底下。

## 整體流程

```text
新機器人硬體與控制介面確認
	-> 資料蒐集
	-> 資料清洗與格式轉換
	-> 模型訓練
	-> 實機推論
	-> 回饋到資料與訓練策略
```

## 共通前置條件

### Checklist

- [ ] 確認機器人本體、末端工具、夾爪、相機、控制主機與網路連線可正常啟動。
- [ ] 確認安全機制可用，包含急停、限速、軟體 stop、手動接管與安全區域。
- [ ] 確認控制介面與資料介面，例如 ROS/ROS2 topics、SDK API、WebSocket、RTDE 或廠商控制協定。
- [ ] 確認時間同步方式，例如 NTP、ROS time、硬體 timestamp 或錄製端 timestamp。
- [ ] 定義第一版實證任務，需包含任務名稱、起始狀態、成功條件、失敗條件與人工重置方式。
- [ ] 定義資料保存位置、命名規則、版本規則與不可覆寫的原始資料區。
- [ ] 定義模型與資料的版本對應方式，例如 dataset version、train config、checkpoint、推論程式 commit。

### 完成指標

- 機器人可在安全限制下完成手動控制或 VR teleoperation。
- 感測資料、控制命令與任務 metadata 可以被完整記錄。
- 已定義至少 1 個可重複執行的 VLA 實證任務。

### 查核點

- 安全負責人或現場操作者完成急停與接管測試。
- 研發負責人確認資料欄位與控制欄位足以支援訓練與部署。
- 專案負責人確認 v1 任務範圍，不在此階段擴張到多任務或高成功率優化。

---

## 1. 資料蒐集

### 目的

建立新機器人的第一版示範資料集。目前常見方式是使用 VR 或其他 teleoperation 方式，由人類操作機器人完成指定任務，並同步錄製影像、機器人狀態、末端姿態、夾爪狀態與控制命令。

### 輸入

- 新機器人與控制主機。
- VR/teleoperation 操作工具。
- 任務定義與場景配置。
- 錄製腳本或 rosbag/mcap/自訂 logger。

### Checklist

- [ ] 確認 VR 或 teleoperation 工具可以控制機器人完成基本動作。
- [ ] 確認錄製時包含必要 observation，例如相機影像、joint state、EEF pose、gripper state、robot mode。
- [ ] 確認錄製時包含必要 action，例如 joint command、EEF delta、gripper command 或實際部署會使用的 action space。
- [ ] 確認資料頻率，例如 camera FPS、state Hz、action Hz，並記錄降頻或同步策略。
- [ ] 確認每筆 episode 都有任務名稱、操作者、日期、機器人版本、場景版本、成功/失敗標記，並依固定資料夾結構保存 raw data、video、metadata、logs。
- [ ] 確認錄製後可立即做 smoke check，例如影片可播放、metadata 可讀取、必要 topic/message count 不為 0，且原始資料唯讀保存不直接覆寫。
- [ ] 先錄製少量 pilot episodes，確認資料可轉換與可訓練後，再擴大量產資料。

### 完成指標

- 至少完成 1 個任務的 pilot dataset。
- 每個 episode 都可對應影像、狀態、action 與 metadata。
- 影像、狀態與 action 的 timestamp 可對齊，沒有明顯漏訊或長時間中斷。
- 成功/失敗 episode 都有明確標記，且可以被後續清洗流程讀取。

### 查核點

- 抽查 3 到 5 筆 episode，確認影片內容與 metadata 任務標記一致。
- 抽查必要資料欄位，確認 shape、unit、座標系與左右手定義沒有混淆。
- 抽查 action 是否符合部署預期，例如 delta pose、absolute pose、joint command 或 gripper range。
- 確認錄製資料中的安全事件、人工接管、失敗示範有被標記，不混入乾淨訓練資料。

### 產出物

- 原始資料集路徑與資料清單。
- 任務定義文件。
- 錄製欄位規格。
- pilot dataset 檢查紀錄。

### 風險與待釐清

- VR 控制座標系與機器人座標系是否一致。
- 多相機時間同步與曝光設定是否穩定。
- action space 是否與預計訓練模型相容。
- 示範品質是否足以支援 imitation learning，而不是只完成單次操作。

---

## 2. 資料清洗

### 目的

將原始錄製資料轉換成模型訓練所需格式。目前常見目標格式包含 LeRobot dataset，也可能依模型框架轉成 OpenPI、ACT 或自訂格式。此階段重點是保留原始資料、建立可重跑的轉換流程，並驗證轉換後資料的欄位、維度、頻率與 episode 對齊。

### 輸入

- 原始錄製資料。
- 任務 metadata。
- 轉換腳本與格式規格。
- 目標模型所需 observation/action schema。

### Checklist

- [ ] 定義目標資料格式，例如 LeRobot v2.x、OpenPI dataset、ACT HDF5 或自訂 parquet/video 結構。
- [ ] 建立 raw data 到 training format 的轉換腳本，避免手動搬檔或手動改欄位。
- [ ] 定義 observation schema，例如 image keys、state vector、language instruction、task id。
- [ ] 定義 action schema，例如 action dimension、左右手順序、gripper range、delta/absolute 定義。
- [ ] 定義 episode 過濾規則，例如失敗資料、急停資料、時間不同步資料、缺影像資料。
- [ ] 定義資料切分規則，例如 train/validation split、依日期或場景切分，避免資料洩漏。
- [ ] 執行轉換後資料驗證，確認 episode 數、frame 數、video 數、parquet/HDF5 數一致。
- [ ] 執行可視化抽查，確認影像、state、action 在同一時間點語意一致。
- [ ] 記錄轉換版本、輸入資料版本與輸出 dataset version。

### 完成指標

- 可從 raw data 一鍵或明確指令重建訓練資料集。
- 轉換後資料可被 dataloader 正常讀取。
- observation/action 維度與模型 train config 完全一致。
- 資料驗證報告列出 pass/fail episodes 與失敗原因。

### 查核點

- 抽查轉換後 dataset 的 metadata，確認 robot、task、fps、feature schema 正確。
- 抽查 action range，確認沒有 NaN/Inf、極端跳點或 gripper 超出預期範圍。
- 抽查左右手、相機名稱、座標軸方向，確認沒有交換或鏡像問題。
- 用最小 dataloader batch 跑一次，確認 tensor shape、dtype、device 前處理正常。

### 產出物

- 訓練格式資料集路徑。
- 轉換腳本與執行指令。
- schema 文件。
- dataset validation report。
- pass/fail episode 清單。

### 風險與待釐清

- LeRobot 或目標框架版本不同，可能造成 metadata/schema 不相容。
- 原始資料頻率不同步時，補值或降頻策略會影響 action label 品質。
- 訓練 action 與部署 action 不一致會導致模型可訓練但不可部署。
- 資料清洗過度可能移除重要失敗情境；資料清洗不足可能污染訓練。

---

## 3. 訓練

### 目的

用清洗後資料完成第一版 VLA 模型訓練與離線驗證。常見候選模型包含 ACT、pi0、pi05、SmolVLA 或其他 imitation learning/VLA 架構。v1 目標不是最佳成功率，而是確認資料格式、訓練設定、checkpoint 與推論介面可以形成閉環。

### 輸入

- 訓練格式資料集。
- 模型 train config。
- 訓練環境，例如 GPU server、CUDA/PyTorch/JAX/uv/conda 版本。
- 評估腳本或 validation dataloader。

### Checklist

- [ ] 選定第一版模型路線，例如 ACT、pi0、pi05、SmolVLA，並記錄選擇原因。
- [ ] 確認 train config 的 observation/action schema 與 dataset 完全一致。
- [ ] 確認 action horizon、state dimension、image keys、language instruction 與部署需求一致。
- [ ] 先執行 dataloader smoke test，確認單 batch 可讀取並可進模型 forward。
- [ ] 先執行短步數 smoke training，確認 loss 可計算、checkpoint 可保存、log 可讀取。
- [ ] 執行正式 v1 training，記錄 dataset version、config name、commit、seed、硬體與訓練時間。
- [ ] 建立 checkpoint 命名規則，避免 smoke checkpoint 與正式 checkpoint 混用。
- [ ] 執行離線 validation，例如 loss curve、action replay、sample rollout visualization。
- [ ] 匯出或整理部署需要的 checkpoint、normalization stats、model config 與推論程式參數。

### 完成指標

- smoke training 可以在短時間內完成並產生可載入 checkpoint。
- 正式 v1 training 完成，且 loss/log 沒有 NaN、爆炸或長時間不收斂異常。
- checkpoint 可以被推論 server 或 inference script 成功載入。
- 離線抽樣輸出的 action dimension、range、左右手順序與部署規格一致。

### 查核點

- 訓練前查核 dataset schema 與 train config，不允許 action dim 或 state dim 靜默不一致。
- 訓練中查核 log，確認資料讀取速度、GPU utilization、loss、checkpoint interval 正常。
- 訓練後查核 checkpoint 對應的 dataset version 與 commit，避免不可重現。
- 部署前查核 normalization stats 是否與訓練資料一致，不使用錯誤任務或舊機器人的 stats。

### 產出物

- train config。
- training log。
- checkpoint。
- validation report。
- deployment package 清單。

### 風險與待釐清

- 不同模型對資料格式與 action horizon 要求不同，需避免只轉格式但語意不相容。
- 小資料集可能只能驗證 pipeline，不能代表實機成功率。
- GPU 訓練環境與實機推論環境不同，可能造成匯出或載入問題。
- smoke checkpoint 不應直接用於高風險實機測試。

---

## 4. 實機推論

### 目的

將訓練完成的模型部署到實機推論環境，驗證模型可以在 x86 或 arm64 平台上穩定接收 observation、輸出 action，並透過安全限制送到機器人控制介面。此階段重點是先低速、短時間、可接管地完成閉環，再逐步提高任務難度。

### 輸入

- 已驗證 checkpoint。
- inference server/client 或部署腳本。
- x86 或 arm64 實機推論主機。
- 機器人控制橋接程式。
- 安全參數與測試場景。

### Checklist

- [ ] 確認部署平台類型，例如 x86 GPU server、Jetson/arm64、CPU-only 或分散式 policy server。
- [ ] 確認 Python、CUDA、PyTorch/JAX、模型框架與依賴套件在部署平台可安裝。
- [ ] 確認 checkpoint、config、normalization stats、tokenizer 或 language embedding 檔案完整。
- [ ] 確認推論輸入與訓練 observation 完全一致，包含影像尺寸、相機順序、state 維度與 normalization。
- [ ] 確認推論輸出與機器人 action interface 完全一致，包含 action dimension、左右手順序、delta/absolute、gripper scale。
- [ ] 加入 action 安全檢查，例如 NaN/Inf 檢查、delta clamp、速度限制、workspace limit、gripper range clip。
- [ ] 加入推論頻率監控，例如 policy latency、control loop Hz、丟包或 timeout 處理。
- [ ] 先執行 dry-run，不發送到真實馬達，只記錄 observation 到 action 的完整路徑。
- [ ] 執行低速實機測試，保留人工接管與急停人員。
- [ ] 記錄每次實機推論的 checkpoint、資料版本、任務版本、成功/失敗原因與影片。

### 完成指標

- 模型可在目標平台載入並完成單步 inference。
- dry-run 可連續執行，沒有 shape mismatch、device error、timeout 或 memory error。
- 實機低速閉環可執行，且所有 action 都通過安全檢查。
- 至少完成 1 次可重現的任務嘗試，無論成功或失敗都有完整 log 與影片可回放。

### 查核點

- x86 與 arm64 平台分別確認依賴套件、模型載入與推論速度；若只支援其中一種，需明確記錄限制。
- 查核推論主機與機器人控制主機的網路延遲、timeout 與斷線安全行為。
- 查核 action safety layer 是否在非有限值、過大 delta、gripper 超界時拒絕或裁切命令。
- 查核實機輸出是否與離線 action replay 一致，避免部署端重新排序或縮放。
- 查核每次測試後是否有保存 log、影片、模型版本與現場備註。

### 產出物

- 部署步驟文件。
- 推論環境版本清單。
- safety layer 設定。
- dry-run log。
- 實機測試紀錄與影片。
- 問題清單與下一輪資料補強建議。

### 風險與待釐清

- arm64 平台可能缺少 GPU wheel、Triton、torch.compile 或特定模型加速支援。
- 推論 latency 過高會造成控制落後，需要降頻、縮小模型或改成遠端 policy server。
- 訓練時 action scaling 與部署時 action scaling 不一致會造成危險動作。
- 實機測試若缺少 action clamp 與 timeout fallback，模型異常輸出可能直接進入硬體控制。

---

## v1 階段關卡

### Gate 1：資料可用

- [ ] raw data 可讀取。
- [ ] 影片、state、action、metadata 可對齊。
- [ ] pilot episodes 已完成抽查。

### Gate 2：資料可訓練

- [ ] 轉換後 dataset 可被 dataloader 讀取。
- [ ] schema 與 train config 一致。
- [ ] pass/fail episode 清單完成。

### Gate 3：模型可部署

- [ ] smoke training 成功。
- [ ] checkpoint 可載入。
- [ ] 離線 action 輸出符合部署規格。

### Gate 4：實機可閉環

- [ ] dry-run 成功。
- [ ] safety layer 啟用。
- [ ] 低速實機測試完成並有 log/影片。

## Redmine 描述範本

```text
目的：
建立新機器人 VLA v1 測試與實證流程，確認資料蒐集、資料清洗、模型訓練、實機推論四階段可以形成最小可行閉環。

範圍：
1. 資料蒐集：以 VR/teleoperation 蒐集 pilot dataset。
2. 資料清洗：轉換為訓練格式，例如 LeRobot，並驗證 schema。
3. 訓練：以 ACT/pi0/pi05/SmolVLA 等模型完成 smoke training 與 v1 checkpoint。
4. 實機推論：將模型部署到 x86 或 arm64，完成 dry-run 與低速實機閉環。

完成指標：
- raw data、training dataset、checkpoint、deployment log 均可追溯版本。
- 至少一個任務完成從資料蒐集到實機推論的閉環紀錄。
- 每階段都有 checklist、完成指標、查核點與產出物。

查核點：
- Gate 1 資料可用。
- Gate 2 資料可訓練。
- Gate 3 模型可部署。
- Gate 4 實機可閉環。
```
