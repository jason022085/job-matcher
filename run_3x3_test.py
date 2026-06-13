import os
import json
import logging
import time
from dotenv import load_dotenv
from openai import OpenAI

# 載入主程式的模組
from main import PROMPT_TEMPLATE, read_file, OPENROUTER_API_KEY, OPENROUTER_MODEL

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def evaluate_match(resume_path, job_path, client):
    """執行單一配對測試"""
    resume_content = read_file(resume_path, "", "履歷")
    job_description = read_file(job_path, "", "職缺描述")
    
    prompt = PROMPT_TEMPLATE.format(
        resume_content=resume_content.strip(), 
        job_description=job_description.strip()
    )
    
    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

def main():
    if not OPENROUTER_API_KEY:
        logging.error("請確認 .env 檔案中有設定 OPENROUTER_API_KEY")
        return
        
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
    
    # 定義要測試的 3 個履歷與 3 個職缺
    resumes = {
        "Full-Stack Engineer": "test_data/resume_fullstack.txt",
        "Database Engineer": "test_data/resume_database.txt",
        "UI/UX Designer": "test_data/resume_uiux.txt"
    }
    
    jobs = {
        "Full-Stack Job": "test_data/job_fullstack.txt",
        "Database Job": "test_data/job_database.txt",
        "UI/UX Job": "test_data/job_uiux.txt"
    }
    
    results = []
    
    # 進行 3x3 矩陣測試
    for r_name, r_path in resumes.items():
        for j_name, j_path in jobs.items():
            logging.info(f"正在測試: [履歷] {r_name} -> [職缺] {j_name}")
            match_data = evaluate_match(r_path, j_path, client)
            
            # 將結果記錄到陣列中
            results.append({
                "resume_type": r_name,
                "job_type": j_name,
                "is_high_quality_match": match_data.get("is_high_quality_match", False),
                "email_preview": match_data.get("email_preview", ""),
                "match_reasons": match_data.get("match_reasons", [])
            })
            
            # 避免觸發 API Rate Limit，每次呼叫後暫停 2 秒
            time.sleep(2)
            
    # 將最終 3x3 測試結果輸出為 JSON 檔案
    output_file = "test_data/3x3_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    logging.info(f"✅ 3x3 矩陣測試完成！結果已儲存至 {output_file}")

if __name__ == "__main__":
    main()
