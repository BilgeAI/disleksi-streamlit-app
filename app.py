
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

st.set_page_config(page_title="Disleksi Destek Paneli", layout="wide")
st.title("🧠 Disleksi Öğrenme Takibi ve Zihin Haritası")

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, parse_dates=["date"])
        return df
    return None

st.sidebar.header("📤 Veri Yükle")
uploaded_file = st.sidebar.file_uploader("CSV Dosyasını Yükle", type=["csv"])
if uploaded_file is None:
    st.warning("Lütfen bir CSV dosyası yükleyin.")
    st.stop()

df = load_data(uploaded_file)

st.sidebar.header("🔍 Filtreleme")
selected_user = st.sidebar.selectbox("Kullanıcı Seç", df["user_id"].unique())
user_df = df[df["user_id"] == selected_user]

st.subheader("📊 Günlük Başarı Puanları")
daily_scores = user_df.groupby("date")["correct"].sum()
fig1, ax1 = plt.subplots(figsize=(10, 3))
sns.lineplot(x=daily_scores.index, y=daily_scores.values, marker="o", ax=ax1)
ax1.set_ylabel("Puan (0-10)")
ax1.set_title("Günlük Test Başarıları")
ax1.tick_params(axis='x', rotation=45)
st.pyplot(fig1)

st.subheader("📅 Haftanın Günlerine Göre Başarı Ortalaması")
day_avg = user_df.groupby("day_of_week")["correct"].mean().sort_values()
fig2, ax2 = plt.subplots(figsize=(10, 3))
sns.barplot(x=day_avg.index, y=day_avg.values, ax=ax2, palette="Blues_d")
ax2.set_ylabel("Ortalama Doğru Cevap")
ax2.set_title("Günlük Performans Karşılaştırması")
st.pyplot(fig2)

st.subheader("📝 Kullanıcı Günlük Notları")
if "notes" in user_df.columns:
    notes_counts = user_df["notes"].value_counts().head(10)
    st.write("En Sık Girilen Notlar:")
    st.bar_chart(notes_counts)
else:
    st.info("Notlar sütunu bulunamadı.")

st.subheader("🔊 Geri Bildirim")
def generate_feedback(daily_score, previous_score, day, holiday):
    messages = []
    if holiday:
        messages.append("Bugün tatildi, yine de katıldığın için harika! 🎉")
    if daily_score > previous_score:
        messages.append("Bugünkü testin önceki günden daha iyi! Gelişim gösteriyorsun 💪")
    elif daily_score < previous_score:
        messages.append("Bugün biraz zorlanmışsın. Dinlenmek iyi gelebilir 🧘‍♀️")
    else:
        messages.append("Bugün skorun sabit. İstikrar da başarıdır! 👏")
    if day in ["Monday", "Wednesday"]:
        messages.append(f"{day} günlerinde performansın düşüyor olabilir. Dikkatini toparlaman zor mu?")
    return " ".join(messages)

last_day = daily_scores.index[-1]
prev_day = daily_scores.index[-2] if len(daily_scores) > 1 else last_day
feedback = generate_feedback(
    daily_score=daily_scores[last_day],
    previous_score=daily_scores[prev_day],
    day=last_day.day_name(),
    holiday=bool(user_df[user_df['date'] == last_day]['holiday'].iloc[0])
)
st.success(feedback)

st.subheader("🧠 Zihin Haritası")
concepts = {
    "Okuma": ["Harf tanıma", "Kelime takibi", "Anlam çıkarımı"],
    "Zorlanma": ["b-d karışıklığı", "harf atlama", "hızlı okuma hatası"],
    "Gelişim": ["Haftalık test", "Sesli tekrar", "Görsel destek"]
}
G = nx.Graph()
for parent, children in concepts.items():
    for child in children:
        G.add_edge(parent, child)
fig3, ax3 = plt.subplots(figsize=(8, 5))
nx.draw(G, with_labels=True, node_color="lightgreen", node_size=2000, font_size=10, ax=ax3)
st.pyplot(fig3)

st.info("📌 Verinizi yükleyin, ilerlemeyi takip edin ve zihin haritasıyla öğrenmeyi destekleyin!")
