import streamlit as st
import pandas as pd
from openai import OpenAI

# --- SETUP ---

# Load OpenAI key from Streamlit Secrets
client = OpenAI(api_key=st.secrets["openai"]["api_key"])


# Replace this with your actual published Google Sheet CSV URL
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTIOxcwKJY2-ejdabOGVSwIQQOC38KfTM7NmfiuXwJccDrmy0qoFSlFZPmBjckKSA/pub?gid=1488049819&single=true&output=csv"

st.set_page_config(page_title="Clover Weekly Sales", layout="wide")
st.title("☕️ Clover Weekly Sales Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_sales_data(url):
    return pd.read_csv(url)

df_sales = load_sales_data(sheet_url)

# --- BASIC METRICS ---
st.subheader("📈 Weekly Summary")
total_sales = df_sales["Total Sales ($)"].sum()
st.metric("Total Sales", f"${total_sales:,.2f}")

# --- TOP ITEMS ---
st.subheader("🏆 Top 3 Items")
top_items = df_sales.groupby("Item Name")["Quantity Sold"].sum().sort_values(ascending=False).head(3)
st.dataframe(top_items)

# --- CATEGORY BREAKDOWN ---
st.subheader("📊 Sales by Category")
cat_sales = df_sales.groupby("Category")["Total Sales ($)"].sum()
st.bar_chart(cat_sales)

# --- GPT Q&A ---
st.subheader("💬 Ask GPT About This Week's Sales")
user_question = st.text_input("Type your question about the week's sales:")

if user_question:
    with st.spinner("GPT is thinking..."):
        # Build context from data
        context_table = df_sales.groupby("Item Name")[["Quantity Sold", "Total Sales ($)"]].sum().reset_index().to_string(index=False)
        prompt = f"""
You are an insightful sales analyst for a local coffee shop. Based on this weekly sales data:

{context_table}

Answer this question from the manager:
{user_question}
"""

        # Call GPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful sales analyst."},
                {"role": "user", "content": prompt}
            ]
        )

        st.markdown("**🧠 GPT's Answer:**")
        st.write(response.choices[0].message.content)
