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
# 定義雙模型架構：生成器 (快速/便宜) 與 審查器 (聰明/準確)
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "meta-llama/llama-4-scout")  # 較輕量的模型用於初步生成
EVALUATOR_MODEL = os.getenv("EVALUATOR_MODEL", "meta-llama/llama-4-maverick")  # 可以選擇更強大的模型來當審查器

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

# 設計系統 Prompt 範本
GENERATOR_PROMPT_TEMPLATE = """你是一位專業的求職配對與招募文案助手。
你的任務是比較求職者的【求職者履歷/個人資料】與【職缺描述】，為發送給求職者的「單一職缺配對推薦電子郵件」生成專屬的客製化內容。
這些內容只是電子郵件的補充說明，並非郵件的唯一焦點。

【生成欄位】
1. email_preview：一段簡短的預覽句（Preheader），強調此職缺與求職者資歷的高契合度。
2. match_reasons：1 到 3 點字串陣列，具體點出求職者為什麼適合此職缺。

【核心生成規則】
1. 正向表述 (Positive Framing)：專注於求職者「為何是個好人選」，強調正面契合點。
2. 簡潔、友善與易讀性 (Concise, Friendly, Skimmable)：使用親切、專業的語氣。文字必須精簡，方便求職者快速掃讀，以降低認知負載。

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
  "match_reasons": ["推薦理由一", "推薦理由二"]
}}
"""

EVALUATOR_PROMPT_TEMPLATE = """你是一位嚴格的 AI 審查員 (Fact-checker) 與品管專家。
剛才另一個 AI 針對求職者履歷和職缺生成了配對推薦理由。
你的任務是「抓漏」與「防止幻覺 (Hallucination)」，保護公司的品牌聲譽。

【審核規則】
1. 真實可驗證 (Verifiable)：每個推薦理由都必須能從【履歷】中明確找到對應的事實。如果有任何誇大或捏造（例如：履歷只寫熟悉 Python，生成理由卻說擁有 AI/ML 專家級經驗），請將該理由剔除。
2. 防偏見：確保理由專注於技能與經驗，不可涉及無關的個人特質或歧視性推論。
3. 品質守門員：如果求職者明顯缺乏該職缺的核心條件，或是所有生成的理由都有誇大嫌疑，請將整體評估視為不合格。

【輸入資料】
<Job_Description>
{job_description}
</Job_Description>

<User_Profile_Resume>
{resume_content}
</User_Profile_Resume>

<Generated_Reasons_To_Evaluate>
{generated_reasons}
</Generated_Reasons_To_Evaluate>

【輸出限制】
請根據嚴格審查結果，僅輸出合法的 JSON 格式。如果所有理由都被剔除，請將 `passed_quality_guard` 設為 false：
{{
  "passed_quality_guard": true 或 false,
  "corrected_match_reasons": ["僅保留 100% 真實可驗證的理由，有必要可微調文字。如果都不合格，請保持空陣列"],
  "evaluator_comments": "簡短的內部審查日誌，說明你為什麼剔除某些理由，或為什麼判定為合格。"
}}
"""

def read_file(filepath: str, default_content: str, file_type: str) -> str:
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

def log_llm_output(resume: str, job_desc: str, flow_name: str, llm_response: str, parsed_result: dict = None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "flow": flow_name,
        "input_resume_length": len(resume),
        "input_job_desc_length": len(job_desc),
        "llm_raw_response": llm_response,
        "parsed_result": parsed_result
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"寫入日誌檔失敗: {e}")

def process_dual_llm_match(resume_content: str, job_description: str, client: OpenAI) -> dict:
    """執行雙模型 (Dual-LLM) 配對與審核邏輯"""
    
    # === Phase 1: Generator ===
    gen_prompt = GENERATOR_PROMPT_TEMPLATE.format(
        resume_content=resume_content.strip(), 
        job_description=job_description.strip()
    )
    
    logging.info(f"👉 [Phase 1] 啟動生成器模型 ({GENERATOR_MODEL})")
    try:
        gen_response = client.chat.completions.create(
            model=GENERATOR_MODEL,
            messages=[{"role": "user", "content": gen_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        gen_result_text = gen_response.choices[0].message.content
        gen_data = json.loads(gen_result_text)
    except Exception as e:
        logging.error(f"生成器發生錯誤: {e}")
        return {"error": str(e), "phase": "generator"}

    # 如果生成器認為配對不佳，直接結束，不用浪費資源給 Evaluator
    if not gen_data.get("is_high_quality_match", False) or not gen_data.get("match_reasons"):
        logging.info("ℹ️ 生成器判定配對品質不足，提早結束審核流程。")
        final_result = {
            "is_high_quality_match": False,
            "email_preview": "",
            "match_reasons": [],
            "evaluator_comments": "Generator skipped evaluation due to low match quality.",
            "generator_original_reasons": []
        }
        log_llm_output(resume_content, job_description, "Dual-LLM (Generator Only)", gen_result_text, final_result)
        return final_result

    # === Phase 2: Evaluator ===
    logging.info(f"🔍 [Phase 2] 啟動審查器模型 ({EVALUATOR_MODEL}) 進行事實查核")
    eval_prompt = EVALUATOR_PROMPT_TEMPLATE.format(
        resume_content=resume_content.strip(),
        job_description=job_description.strip(),
        generated_reasons=json.dumps(gen_data["match_reasons"], ensure_ascii=False)
    )
    
    try:
        eval_response = client.chat.completions.create(
            model=EVALUATOR_MODEL,
            messages=[{"role": "user", "content": eval_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        eval_result_text = eval_response.choices[0].message.content
        eval_data = json.loads(eval_result_text)
    except Exception as e:
        logging.error(f"審查器發生錯誤: {e}")
        return {"error": str(e), "phase": "evaluator"}

    # === 合併結果 ===
    final_result = {
        "is_high_quality_match": eval_data.get("passed_quality_guard", False),
        "email_preview": gen_data.get("email_preview", ""),
        "match_reasons": eval_data.get("corrected_match_reasons", []),
        "evaluator_comments": eval_data.get("evaluator_comments", ""),
        "generator_original_reasons": gen_data.get("match_reasons", [])
    }
    
    log_info = f"【Generator】\n{gen_result_text}\n\n【Evaluator】\n{eval_result_text}"
    log_llm_output(resume_content, job_description, "Dual-LLM (Full)", log_info, final_result)
    
    return final_result

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

    result = process_dual_llm_match(resume_content, job_description, client)
    
    print("\n=== 雙模型驗證結果 (Dual-LLM Result) ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("========================================")

if __name__ == "__main__":
    main()
