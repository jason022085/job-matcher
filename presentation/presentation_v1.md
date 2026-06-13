# AI 招募配對系統 | 雙模型驗證展示 (Dual-LLM Architecture)

這份文件展示了我們的「雙模型架構」如何在自動化招募信件發送的過程中，有效防止 AI 幻覺 (Hallucination) 並守護企業品牌聲譽。

---

## 1. 👨‍💻 全端工程師配對 (Full-Stack Engineer)

> [!TIP]
> **Status:** High Match (Passed Quality Guard)  
> **📨 Email Preview:** 我們發現您非常適合資深全端工程師一職，您的技能與經驗高度契合我們的職位需求。

<details>
<summary><b>📄 展開查看原始資料 (Raw Data)</b></summary>

**求職者履歷 (Original Resume)**
```text
林志明 (Zhi-Ming Lin)
聯絡電話：0911-111-111
電子郵件：zhiming.lin@example.com

【專業技能】
- 語言與框架：JavaScript/TypeScript, React.js, Vue.js, Node.js, Python (Django/FastAPI)
- 資料庫與基礎設施：PostgreSQL, MongoDB, Redis, Docker, AWS (EC2, S3, RDS)
- 工具：Git, CI/CD (GitHub Actions), JIRA

【工作經歷】
- 2020.08 - 至今 | 全端工程師 @ 雲端軟體科技
  - 負責開發與維護 SaaS 平台的企業級管理後台，前端使用 React，後端使用 Node.js。
  - 導入 Redis 快取機制，將高流量的報表頁面載入速度提升 50%。
  - 透過 Docker 容器化所有微服務，並建置自動化 CI/CD 流程，縮短部署時間。
- 2018.07 - 2020.07 | 前端工程師 @ 數位行銷公司
  - 使用 Vue.js 開發多個行銷活動網站，支援高併發流量。
```

**職缺描述 (Job Description)**
```text
資深全端工程師 (Senior Full-Stack Engineer)

【主要職責】
- 負責前端 (React.js) 與後端 (Node.js/Python) 的功能開發與 API 串接。
- 實作與維護資料庫結構 (PostgreSQL / Redis)。
- 部署與監控 AWS 雲端基礎架構，優化 CI/CD 流程。

【職位要求】
- 至少 3 年以上 Web 應用程式全端開發經驗。
- 熟悉 React.js 或 Vue.js，具備深厚的 JavaScript/TypeScript 基礎。
- 熟悉 Node.js 或 Python (Django/FastAPI) 等後端技術。
- 具備 AWS (EC2, S3, RDS) 等雲端平台操作經驗者尤佳。
```
</details>

### ⚖️ 雙模型查核對比 (Generator vs Evaluator)

紅色代表生成器寫出但被剔除的內容（幻覺/誇大），綠色或白色代表最終審查通過寄給求職者的內容。

```diff
- 您擁有豐富的全端開發經驗，熟練掌握 React.js、Node.js 與 Python 等技術，完全符合我們的職位要求。
+ 您擁有豐富的全端開發經驗，熟練掌握 React.js、Node.js 等技術，符合我們的職位要求。
- 您有優秀的雲端平台操作經驗，特別是在 AWS 上的實戰經驗，能夠幫助我們優化 CI/CD 流程。
  您曾經成功導入 Redis 快取機制優化系統性能，並建置自動化 CI/CD 流程，展現出優秀的技術實力和解決問題的能力。
```

> [!NOTE]
> **🛡️ 審查員過濾日誌 (Fact-Checker Log)**
> - 👉 第一個理由中刪除了 'Python' 與 '完全符合'，因為履歷中雖然提到 Python，但工作經歷中未明確提及使用 Python 的專案經驗。
> - 👉 第二個理由被完全刪除，原因是履歷雖提到 AWS，但並未具體說明『實戰經驗』。
> - 👉 第三個理由被保留，因為它完整反映了履歷中的經歷與成就。

---

## 2. 🗄️ 資料庫工程師配對 (Database Engineer)

> [!TIP]
> **Status:** High Match (Passed Quality Guard)  
> **📨 Email Preview:** 您深厚的資料庫效能調校經驗，正是我們資料庫管理工程師團隊所需要的關鍵人才！

<details>
<summary><b>📄 展開查看原始資料 (Raw Data)</b></summary>

**求職者履歷 (Original Resume)**
```text
陳偉強 (Wei-Qiang Chen)

【專業技能】
- 資料庫系統：MySQL, PostgreSQL, Oracle, MongoDB, Redis
- 系統環境：Linux, Shell Scripting, AWS RDS, GCP Cloud SQL

【工作經歷】
- 2019.03 - 至今 | 資深資料庫管理員 (Senior DBA) @ 大型電商集團
  - 管理超過 50 個關聯式資料庫實例，維持 99.99% 的系統可用性。
  - 執行慢查詢 (Slow Query) 分析與優化，成功將核心結帳系統的資料庫負載降低 40%。
```

**職缺描述 (Job Description)**
```text
資料庫管理工程師 (Database Administrator / Engineer)

【主要職責】
- 負責公司內部 MySQL/PostgreSQL 資料庫的日常維運、備份還原與監控。
- 進行資料庫效能調校 (Performance Tuning)，分析與優化慢查詢 (Slow Queries)。

【職位要求】
- 至少 3 年以上 DBA 或資料庫工程師經驗。
- 精通 MySQL 或 PostgreSQL 等關聯式資料庫，熟練掌握各種效能調校技巧。
- 熟悉 Linux 作業系統，能編寫 Shell Script 進行自動化維運。
```
</details>

### ⚖️ 雙模型查核對比 (Generator vs Evaluator)

```diff
- 您擁有超過五年的 DBA 經驗，精通 MySQL、PostgreSQL 以及 Oracle，能完美駕馭我們所有的資料庫系統。
+ 您在大型電商集團擔任資深 DBA，具備管理超過 50 個實例的經驗，精通 MySQL 與 PostgreSQL。
- 您曾將核心系統的資料庫負載降低 40%，且熟悉 AWS RDS 與 GCP Cloud SQL 的跨雲架構部署。
+ 您具備優秀的效能調校能力，曾將核心結帳系統的資料庫負載降低 40%，與我們對優化慢查詢的需求高度契合。
- 您熟悉 Linux 與 Shell Scripting，能獨立完成自動化維運與所有開發團隊的 Schema 設計審查。
+ 您熟悉 Linux 作業環境與 Shell Scripting，具備開發自動化維運流程的能力。
```

> [!NOTE]
> **🛡️ 審查員過濾日誌 (Fact-Checker Log)**
> - 👉 修改第一個理由：移除 '完美駕馭' 等誇大用語，替換為履歷中真實具備的「超過 50 個實例管理經驗」。
> - 👉 修改第二個理由：履歷未明確提及『跨雲架構部署』，故剔除該無根據之推論，防止幻覺。
> - 👉 修改第三個理由：移除『所有開發團隊』等過度延伸字眼，專注並保留其自動化維運的真實經驗。

---

## 3. 🎨 UI/UX 設計師配對 (UI/UX Designer)

> [!TIP]
> **Status:** High Match (Passed Quality Guard)  
> **📨 Email Preview:** 您建立 Design System 的實戰經驗與對使用者研究的熱忱，與我們尋找產品 UI/UX 設計師的目標完美契合！

<details>
<summary><b>📄 展開查看原始資料 (Raw Data)</b></summary>

**求職者履歷 (Original Resume)**
```text
張雅婷 (Ya-Ting Chang)

【專業技能】
- 設計工具：Figma, Sketch, Adobe XD, Illustrator, Photoshop
- 專業領域：使用者研究 (User Research)、易用性測試、Wireframing、Design System
- 跨團隊協作：熟悉基本 HTML/CSS，能與前端工程師順暢溝通。

【工作經歷】
- 2021.05 - 至今 | UI/UX 設計師 @ 網路科技平台
  - 主導公司旗艦 App 的改版設計，透過使用者訪談與 A/B 測試，讓使用者留存率提升 15%。
  - 從零到一建置且維護團隊的 Design System (Figma Components)，將設計交付效率提升 30%。
```

**職缺描述 (Job Description)**
```text
產品 UI/UX 設計師 (Product UI/UX Designer)

【主要職責】
- 進行使用者研究、競品分析與可用性測試，並將洞察轉化為設計方案。
- 建立並維護產品的 Design System，確保跨平台設計的一致性。

【職位要求】
- 至少 2 年以上軟體或網路產品介面設計經驗。
- 精通 Figma 等現代化設計工具，熟悉 Component 與 Auto Layout 運用。
- 具備基本的前端知識 (HTML/CSS)，能理解工程實作的限制與可能性。
```
</details>

### ⚖️ 雙模型查核對比 (Generator vs Evaluator)

```diff
- 您精通前端程式碼 (HTML/CSS/JS)，能夠直接接手工程師的開發工作，大幅提升產品交付速度。
- 您曾主導旗艦 App 改版，透過研究與 A/B 測試讓留存率提升 15%，完全符合我們對數據洞察的期待。
+ 您曾主導旗艦 App 改版，透過使用者研究與 A/B 測試讓使用者留存率提升 15%，展現了優秀的數據洞察力。
- 您具備從零到一建置 Design System 的經驗，將交付效率提升 30%，是帶領我們團隊設計系統的最佳人選。
+ 您具備從零到一建置且維護 Design System 的經驗，將設計交付效率提升 30%，符合我們的跨平台設計需求。
```

> [!WARNING]
> **🛡️ 審查員過濾日誌 (Fact-Checker Log)**
> - 👉 **完全刪除第一個理由**：履歷中只提到『熟悉基本 HTML/CSS，能與前端順暢溝通』，並未表示『精通 JS 並能接手開發』，生成器產生了**嚴重幻覺**。
> - 👉 其餘兩點為履歷中的真實數據與成就，予以保留，但強制刪除過度吹捧的用詞（如『最佳人選』、『完全符合』），使信件語氣更專業且客觀。
