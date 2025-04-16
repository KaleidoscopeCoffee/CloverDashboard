import streamlit as st
import pandas as pd
import openai

# Load secrets
openai.api_key = st.secrets["openai"]["api_key"]
sheet_url = "https://docs.google.com/spreadsheets/d/1KX1cFei3Ltj6IQH6yT7En9FJ-T0GOjLB/edit?usp=sharing&ouid=103835595275984669357&rtpof=true&sd=true"
st.write(df_sales.columns)

st.title("☕️ Clover Weekly Sales Dashboard")

@st.cache_data
def load_sales_data(url):
    df = pd.read_csv(url)
    return df

df_sales = load_sales_data(sheet_url)

st.subheader("📈 Weekly Summary")
st.metric("Total Sales ($)", f"${df_sales['Total Sales ($)'].sum():,.2f}")
top_items = df_sales.groupby("Item Name")["Quantity Sold"].sum().sort_values(ascending=False).head(3)
st.write("**Top 3 Selling Items:**")
st.write(top_items)

st.subheader("🧃 Sales by Category")
cat_breakdown = df_sales.groupby("Category")["Total Sales ($)"].sum()
st.bar_chart(cat_breakdown)

st.subheader("💬 Ask GPT About This Week's Sales")
user_question = st.text_input("Ask a question about this week's sales:")
if user_question:
    context = df_sales.groupby("Item Name")[["Quantity Sold", "Total Sales ($)"]].sum().reset_index().to_string(index=False)
    prompt = f"""This is weekly sales data for a coffee shop:\n{context}\n\nAnswer the following question about this data:\n{user_question}"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful business analyst for a local coffee shop."},
            {"role": "user", "content": prompt}
        ]
    )

    st.markdown("**GPT Answer:**")
    st.write(response["choices"][0]["message"]["content"])
