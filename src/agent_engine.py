import json
import urllib.request
import re

class QueryGenResponse:
    def __init__(self, thought_process: str, pandas_code: str):
        self.thought_process = thought_process
        self.pandas_code = pandas_code

def generate_pandas_query(user_query: str, sample_df_head: str, columns_metadata: str) -> QueryGenResponse:
    # Target the local Ollama native chat completion endpoint 
    url = "http://localhost:11434/api/chat"
    
    system_prompt = f"""
    You are an expert Senior Data Engineer. Your job is to convert natural language questions into secure Pandas code.
    You will operate strictly on a target DataFrame named 'df'.
    
    DATAFRAME SCHEMA METADATA:
    {columns_metadata}
    
    SAMPLE DATA ROWS (df.head()):
    {sample_df_head}
    
    CRITICAL SECURITY GUARDRAILS:
    - You must ONLY use read-only operations (e.g., groupby, sum, mean, loc, iloc, sort_values).
    - NEVER generate code that alters, drops, deletes, or overwrites rows, columns, or data files.
    
    OUTPUT FORMAT CONSTRAINTS:
    You must respond ONLY with a raw valid JSON object. The JSON must match this structure exactly:
    {{
        "thought_process": "Step-by-step reasoning logic explaining how to answer the question using the schema headers.",
        "pandas_code": "The executable single-line Pandas Python code snippet."
    }}
    """
    
    # Structure the network payload for your local Llama 3.1 setup
    payload = {
        "model": "llama3.1",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Request: {user_query}"}
        ],
        "stream": False,
        "options": {
            "temperature": 0.0  # Forces deterministic and concise analytical code generation
        }
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        
        # 1. PROXIES GUARDRAIL: Forces local loopback execution by bypassing active system environment proxy servers
        proxy_handler = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
        
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )
        
        # 2. TIMEOUT GUARDRAIL: Restricted with a strict 120-second execution wall to prevent thread hanging on CPUs
        with opener.open(req, timeout=120) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            
            raw_content = res_json["message"]["content"].strip()
            
            # Robust RegEx parsing: Isolates valid JSON characters inside curly brackets
            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if json_match:
                raw_content = json_match.group(0)
            
            parsed_content = json.loads(raw_content)
            
            # Flexible dictionary lookups to handle irregular LLM structural formatting variants cleanly
            thought = parsed_content.get("thought_process", parsed_content.get("thought", "Processed successfully."))
            code = parsed_content.get("pandas_code", parsed_content.get("code", "df.head()"))
            
            return QueryGenResponse(thought_process=thought, pandas_code=code)
            
    except Exception as e:
        print(f"[ENGINE RUNTIME ERROR]: {str(e)}")
        return QueryGenResponse(
            thought_process=f"Pipeline network interaction/parsing fallback exception: {str(e)}",
            pandas_code="df.head()"
        )
