import pandas as pd
import traceback

def execute_safely(code_str: str, df: pd.DataFrame):
    # Restrict execution access down to specific local data structures only
    local_env = {"df": df, "pd": pd}
    # Completely strip dangerous global system hooks
    global_env = {"__builtins__": {"abs": abs, "min": min, "max": max, "sum": sum, "len": len, "dict": dict, "list": list, "str": str, "int": int, "float": float}}
    
    try:
        # Pre-execution safety verification scan
        forbidden_keywords = ["import", "os", "sys", "exec", "eval", "drop", "delete", "remove", "open"]
        if any(keyword in code_str for keyword in forbidden_keywords):
            return None, "Security Exception: Forbidden operational script pattern detected."
            
        clean_code = code_str.strip().strip("`").replace("python", "").strip()
        
        # Execute dynamically in the restricted environment container
        result = eval(clean_code, global_env, local_env)
        return result, None
    except Exception as e:
        error_msg = f"Runtime Code Execution Error:\n{traceback.format_exc()}"
        return None, error_msg
