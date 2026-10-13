import streamlit as st
import pandas as pd
from src.agent_engine import generate_pandas_query
from src.secure_sandbox import execute_safely

st.set_page_config(page_title="Zero-SQL Assistant", layout="wide", page_icon="📊")
st.title("📊 The 'Zero-SQL' Data Assistant")
st.caption("Empower business teams to extract complex analytical insights from raw data completely via local open-weights AI engines.")

uploaded_file = st.file_uploader("Upload your target analytical dataset CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("📋 Ingested Dataset Matrix Overview")
    st.dataframe(df.head(5), use_container_width=True)
    
    # Capture structural columns schema details programmatically
    schema_info = str(df.dtypes.to_dict())
    sample_head = str(df.head(3).to_dict())
    
    st.markdown("---")
    user_prompt = st.text_input("💬 Ask your database a question in plain English:", placeholder="e.g., Which product category generated the highest net total sales margin?")
    
    if user_prompt:
        with st.spinner("🤖 Local Llama 3.1 analysis engine compiling data queries..."):
            try:
                ai_response = generate_pandas_query(user_prompt, sample_head, schema_info)
                
                with st.expander("🔍 System Thought Process & Generated Code"):
                    st.write(f"**Thinking Logic:** {ai_response.thought_process}")
                    st.code(ai_response.pandas_code, language="python")
                
                result, error = execute_safely(ai_response.pandas_code, df)
                
                if error:
                    st.error(error)
                else:
                    st.subheader("🎯 Automated Analytical Insight Output")
                    if isinstance(result, (pd.DataFrame, pd.Series)):
                        st.dataframe(result)
                    else:
                        st.metric(label="Calculated Result Value", value=str(result))
                        
            except Exception as e:
                st.error(f"Engine Processing Interruption: {str(e)}")
