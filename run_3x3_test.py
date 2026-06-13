import os
import json
import logging
import time
from dotenv import load_dotenv
from openai import OpenAI

# 載入主程式的模組
from main import read_file, OPENROUTER_API_KEY, process_dual_llm_match

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

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
            
            resume_content = read_file(r_path, "", "履歷")
            job_description = read_file(j_path, "", "職缺描述")
            
            # 使用雙模型架構進行測試
            match_data = process_dual_llm_match(resume_content, job_description, client)
            
            # 將結果記錄到陣列中
            results.append({
                "resume_type": r_name,
                "job_type": j_name,
                "is_high_quality_match": match_data.get("is_high_quality_match", False),
                "email_preview": match_data.get("email_preview", ""),
                "match_reasons": match_data.get("match_reasons", []),
                "generator_original_reasons": match_data.get("generator_original_reasons", []),
                "evaluator_comments": match_data.get("evaluator_comments", "")
            })
            
            # 避免觸發 API Rate Limit，每次呼叫後暫停 2 秒
            time.sleep(2)
            
    # 將最終 3x3 測試結果輸出為 JSON 檔案
    output_file = "test_data/3x3_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    logging.info(f"✅ 3x3 雙模型驗證矩陣測試完成！結果已儲存至 {output_file}")

if __name__ == "__main__":
    main()
