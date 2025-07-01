
import streamlit as st
import pandas as pd
import openai
import re

# --- App Configuration ---
st.set_page_config(page_title="Instagram DM Generator", layout="wide")
st.title("📩 Personalized Instagram DM Generator")
st.markdown("Generate high-converting DMs based on bios and last posts of public IG profiles.")

# --- Sidebar Inputs ---
openai_api_key = st.sidebar.text_input("🔑 Enter your OpenAI API Key", type="password")
dm_tone = st.sidebar.selectbox("🎨 Select DM Tone", ["Friendly", "Direct", "Humorous"])

# --- Upload or Paste Usernames ---
input_method = st.radio("Choose Input Method", ["Paste Usernames", "Upload CSV"])

usernames = []
if input_method == "Paste Usernames":
    pasted = st.text_area("Paste Instagram Usernames (comma-separated or line-by-line)")
    if pasted:
        usernames = [u.strip().lstrip("@") for u in re.split(r"[\n,]", pasted) if u.strip()]
else:
    uploaded_file = st.file_uploader("Upload CSV with Instagram usernames", type=["csv"])
    if uploaded_file:
        df_uploaded = pd.read_csv(uploaded_file)
        usernames = df_uploaded.iloc[:, 0].astype(str).str.lstrip("@").tolist()

# --- Mock Scraper Function (Replace with real logic) ---
def scrape_profile(username):
    return {
        "username": username,
        "bio": f"Sample bio from {username}",
        "caption": f"Latest post caption by {username}"
    }

# --- GPT DM Generation ---
import openai

# Initialize OpenAI client with v1.0+
client = openai.OpenAI(api_key=openai_api_key)

def generate_dm(profile, tone):
    prompt = f"""
You're a social media strategist. Write a {tone.lower()} and high-converting DM for an Instagram creator.

Bio: {profile['bio']}
Last Post: {profile['caption']}
Username: @{profile['username']}

Make it sound human, helpful, and actionable.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error generating message: {e}]"

# --- Run Bot ---
if st.button("🚀 Generate DMs") and openai_api_key and usernames:
    data = []
    for user in usernames:
        profile = scrape_profile(user)
        message = generate_dm(profile, dm_tone)
        data.append({
            "Username": f"@{user}",
            "Bio": profile["bio"],
            "Last Post": profile["caption"],
            "Generated DM": message
        })
    df_result = pd.DataFrame(data)
    st.success("✅ DMs generated below. Edit if needed and download.")
    edited_df = st.data_editor(df_result, use_container_width=True, num_rows="dynamic")
    csv = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv, "generated_dms.csv", "text/csv")
elif not openai_api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
