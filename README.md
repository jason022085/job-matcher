# AI Job Matcher (雙模型 AI 求職配對系統)

這個專案是一個企業級的 AI 招募助理，旨在自動比對求職者履歷與職缺描述，並生成高度客製化、語氣友善且**絕對真實**的招募推薦信（Email Preview & Match Reasons）。

為了確保 AI 生成的內容不會出現「幻覺 (Hallucination)」或過度誇大，本系統領先導入了 **Dual-LLM (雙模型驗證) 架構**，透過「生成器 (Generator)」與「審查器 (Evaluator)」的兩階段防護，守護企業招募品牌的公信力。

## ✨ 核心特色 (Key Features)

- **雙模型事實查核 (Dual-LLM Fact-Checking)**：
  - **Phase 1 (生成器)**：使用快速/便宜的模型尋找契合點。
  - **Phase 2 (審查器)**：使用高智商模型進行嚴格的交叉比對，剔除任何在履歷中無法驗證的誇大說詞。
- **結構化 JSON 輸出**：方便無縫串接至後端的自動化 Email 發送系統或資料庫。
- **Quality Guard (品質守門員)**：若配對分數過低或皆為無效理由，系統會自動攔截，避免發送不合適的推薦信。
- **非同步日誌紀錄**：自動將所有 LLM 的原始輸入/輸出轉存為 JSONL 格式，利於後續的品質保證 (QA) 與 A/B 測試追蹤。

## 📁 專案架構 (Project Structure)

```text
job-matcher/
├── main.py                # 核心主程式 (包含 Dual-LLM 邏輯)
├── run_3x3_test.py        # 3x3 矩陣自動化測試腳本
├── requirements.txt       # Python 套件依賴清單
├── .env                   # 環境變數設定檔
├── presentation.html      # 雙模型成效視覺化簡報 (單頁網頁)
├── product_requirement.txt# 原始產品需求文件 (PRD)
└── test_data/             # 測試資料集
    ├── resume_*.txt       # 各職位範例履歷
    ├── job_*.txt          # 各職位範例職缺
    └── 3x3_results.json   # 測試腳本產生的最終配對結果
```

## 🚀 快速開始 (Quick Start)

### 1. 安裝環境依賴

請確保您的環境安裝了 Python 3.8+ 版本，然後執行以下指令：

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

在專案根目錄建立一個 `.env` 檔案（如果尚未存在），並填寫您的 API Key：

```env
OPENROUTER_API_KEY=your_api_key_here

# 您也可以在此自訂要使用的生成器與審查器模型 (選填)：
# GENERATOR_MODEL=meta-llama/llama-3-8b-instruct
# EVALUATOR_MODEL=meta-llama/llama-3-70b-instruct
```

### 3. 執行單一配對

您可以透過互動式介面或命令列參數執行主程式：

**方法 A：互動式輸入**
```bash
python main.py
# 程式會提示您輸入履歷與職缺的檔案路徑，直接按 Enter 則使用內建預設範本。
```

**方法 B：透過命令列參數**
```bash
python main.py "test_data/resume_fullstack.txt" "test_data/job_fullstack.txt"
```

## 🧪 執行自動化測試 (Test Suite)

專案內建了 3 種不同職位（全端工程師、資料庫工程師、UI/UX設計師）的測試集。如果您想測試雙模型在交叉配對（如：UI設計師應徵後端工程師）下的攔截精準度，請執行：

```bash
python run_3x3_test.py
```
執行完畢後，結果將儲存於 `test_data/3x3_results.json`，裡面詳細記錄了生成器原本的草稿與審查員的過濾日誌。

## 📊 視覺化展示 (Presentation)

如果您需要向團隊或主管展示「雙模型攔截幻覺」的強大威力，請直接在瀏覽器中雙擊打開 `presentation.html`。
您將看到一份高質感的深色對比簡報，明確標示出 AI 幻覺是如何被精準捕捉並修正的！
