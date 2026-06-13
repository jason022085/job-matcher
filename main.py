import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# 1. 載入環境變數與設定日誌
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-maverick")

# 設定 Logging，將結果記錄到 JSONL 檔案中以供後續審核 (對應 PRD: LLM outputs are logged for external review)
LOG_FILE = "llm_match_results.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

# 預設求職者履歷範例
DEFAULT_RESUME = """
王小明
聯絡電話：0912-345-678
電子郵件：xiaoming@example.com

【專業技能】
- Python (3 年經驗)，能熟練使用 Django 與 FastAPI 開發後端 API。
- Docker (2 年經驗)，容器化部署與微服務架構。
- SQL, Git, Linux
- 溝通協調能力強，具備跨部門團隊協作經驗。

【工作經歷】
- 2023.06 - 至今 | 軟體工程師 @ 科技公司
  - 主導電子商務平台後端重構，將 API 回應時間縮短 30%。
  - 設計並維護內部 CI/CD 流程，提升團隊部署效率 40%。
- 2022.01 - 2023.05 | 助理工程師 @ 新創公司
  - 協助開發客戶關係管理系統 (CRM) 資料庫串接。

【自我介紹】
我是一個熱愛學習與挑戰的工程師。在過去的工作中，我總是以樂觀、積極的心態面對技術難題，並且非常注重程式碼的細節與品質。期望能加入貴公司，與優秀的團隊一同成長！
"""

DEFAULT_JOB_DESCRIPTION = """Software Engineer, AI/ML (Early Career)
About the job
At Google, we engineering tools and platforms that change how billions of people interact with information. As an Associate AI Engineer, you will join a team dedicated to pushing the boundaries of Artificial Intelligence and Machine Learning. You will work on integrating cutting-edge Large Language Models (LLMs) and generative technologies into Google’s ecosystem, creating intelligent systems that solve complex, real-world problems.

This role is tailored for recent graduates and early-career engineers who possess a solid foundational knowledge of computer science, data structures, and machine learning, alongside a passion for building next-generation AI agents and automation systems.

Responsibilities
Model Integration & Optimization: Assist in deploying, fine-tuning, and optimizing Large Language Models (LLMs) and open-source models using advanced inference frameworks.

Application Development: Design and develop robust backend components and APIs (e.g., using Python and modern frameworks) to power intelligent AI features and agent workflows.

Data & Evaluation Pipeline: Build scalable pipelines for data preprocessing, prompt evaluation, and performance monitoring to ensure the reliability and safety of AI outputs.

Cross-functional Collaboration: Work closely with product managers, UX designers, and senior researchers to translate user requirements into scalable, production-ready AI capabilities.

Continuous Learning: Keep up with the latest advancements in LLM tooling, framework integration (such as Model Context Protocols or evaluation monitoring systems), and infrastructure optimization.

Qualifications
Minimum qualifications:
Bachelor's degree in Computer Science, Mathematics, Data Science, a related technical field, or equivalent practical experience.

Strong proficiency in Python or C++, with a solid grasp of data structures, algorithms, and software engineering best practices.

Academic or project experience with machine learning fundamentals, deep learning, or Natural Language Processing (NLP).

Experience building and consuming RESTful APIs or working with modern backend frameworks.

Preferred qualifications:
Master's degree in a quantitative field (Computer Science, Mathematics, Statistics).

Hands-on experience with modern LLM tooling, local inference engines (e.g., llama.cpp, vLLM), or LLM observability and tracking platforms (e.g., Langfuse).

Familiarity with building autonomous AI agents, retrieval-augmented generation (RAG) workflows, or prompt engineering frameworks.

Experience working with cloud platforms (like Google Cloud Platform / Vertex AI) and containerization tools (Docker, Kubernetes).

Excellent communication skills with the ability to articulate technical tradeoffs in a collaborative environment.
"""

# 設計系統 Prompt 範本 (改為強制輸出 JSON，便於系統串接與儲存)
PROMPT_TEMPLATE = """現在時間是{current_time}，你是一位專業的求職配對與招募文案助手。
你的任務是比較求職者的【求職者履歷/個人資料】與【職缺描述】，為發送給求職者的「單一職缺配對推薦電子郵件」生成專屬的客製化內容。
這些內容只是電子郵件的補充說明，並非郵件的唯一焦點。

【生成欄位】
1. email_preview：一段簡短的預覽句（Preheader），強調此職缺與求職者資歷的高契合度（例如：「查看為什麼您的後端開發經驗與 Google 的 AI 工程師職缺完美契合！」）。
2. match_reasons：1 到 3 點字串陣列，具體點出求職者為什麼適合此職缺。

【核心生成與品質規則】
1. 真實可驗證 (Verifiable)：所有推薦理由必須 100% 真實，且能被人類審查員在履歷或職缺描述中直接驗證，嚴禁任何捏造或過度誇大。
2. 正向表述 (Positive Framing)：專注於求職者「為何是個好人選」，強調正面契合點，避免使用機械式的條件比對（例如：好的寫法：「您在 <特定技能/經歷> 的深厚背景...」，絕對避免：「您符合本職缺 5 項要求中的 4 項。」）
3. 簡潔、友善與易讀性 (Concise, Friendly, Skimmable)：使用親切、專業的語氣。文字必須精簡，方便求職者快速掃讀，以降低認知負載。
4. 品質守門員 (Quality Guard)：如果求職者履歷中明顯缺乏該職缺的核心關鍵條件，或者你無法產生高品質、具說服力的推薦理由，請嚴格停止生成推薦內容，並將 `is_high_quality_match` 設為 false。

---
【輸入區】
<Job_Description>
{job_description}
</Job_Description>

<User_Profile_Resume>
{resume_content}
</User_Profile_Resume>

---
【輸出限制】
- 絕對不要輸出任何解釋性文字。
- 請務必只輸出合法的 JSON 格式，包含以下欄位：
{{
  "is_high_quality_match": true 或 false,
  "email_preview": "預覽文字 (若配對品質不足可為空)",
  "match_reasons": ["推薦理由一", "推薦理由二"] // (若配對品質不足可為空陣列)
}}
"""

def read_file(filepath: str, default_content: str, file_type: str) -> str:
    """讀取檔案內容，若未提供或讀取失敗則回傳預設內容。"""
    if filepath:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                logging.info(f"成功載入{file_type}檔案: {filepath}")
                return content
            except Exception as e:
                logging.error(f"無法讀取{file_type}檔案 {filepath}: {e}")
                sys.exit(1)
        else:
            logging.error(f"{file_type}檔案路徑不存在: {filepath}")
            sys.exit(1)
    else:
        logging.info(f"使用預設範例{file_type}。")
        return default_content

def log_llm_output(resume: str, job_desc: str, prompt: str, llm_response: str, parsed_result: dict = None):
    """將 LLM 的輸出結果記錄為 JSONL 格式，以供非同步審核與產品改善 (Asynchronous Review & QA)"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model": OPENROUTER_MODEL,
        "input_resume_length": len(resume),
        "input_job_desc_length": len(job_desc),
        "llm_raw_response": llm_response,
        "parsed_result": parsed_result
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        logging.info(f"已將 LLM 生成結果寫入日誌檔: {LOG_FILE}")
    except Exception as e:
        logging.error(f"寫入日誌檔失敗: {e}")

def main():
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY":
        logging.error("請在專案根目錄的 .env 檔案中設定您的 OPENROUTER_API_KEY。")
        sys.exit(1)

    resume_path = ""
    job_path = ""

    if len(sys.argv) > 2:
        resume_path = sys.argv[1]
        job_path = sys.argv[2]
        logging.info("從命令列參數讀取檔案路徑...")
    else:
        try:
            resume_path = input("請輸入【求職者履歷】檔案路徑 (直接按 Enter 使用預設範例): ").strip()
            job_path = input("請輸入【職缺描述】檔案路徑 (直接按 Enter 使用預設範例): ").strip()
        except KeyboardInterrupt:
            print("\n[系統] 偵測到中斷，程式結束。")
            sys.exit(0)

    resume_content = read_file(resume_path, DEFAULT_RESUME, "履歷")
    job_description = read_file(job_path, DEFAULT_JOB_DESCRIPTION, "職缺描述")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = PROMPT_TEMPLATE.format(
        current_time=datetime.utcnow().isoformat() + "Z",
        resume_content=resume_content.strip(), 
        job_description=job_description.strip()
    )

    logging.info(f"正在呼叫 OpenRouter 模型 ({OPENROUTER_MODEL})...")
    
    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result_text = response.choices[0].message.content
        
        parsed_result = None
        try:
            parsed_result = json.loads(result_text)
            print("\n=== 解析結果 (JSON) ===")
            print(json.dumps(parsed_result, indent=2, ensure_ascii=False))
            print("=======================")
        except json.JSONDecodeError:
            print("\n=== 解析結果 (Raw) ===")
            print(result_text)
            print("======================")
            parsed_result = {"error": "Failed to parse JSON", "raw": result_text}
            
        # 記錄 LLM 輸出
        log_llm_output(resume_content, job_description, prompt, result_text, parsed_result)

    except Exception as e:
        logging.error(f"呼叫 OpenRouter 失敗！詳細資訊: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


