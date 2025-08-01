import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import re

# ------------------ CONFIGURAÇÕES INICIAIS ------------------
API_KEY = 'AIzaSyANI2GxhU0bMyHhns1BbEmiVMVWGLKZgZA'  # 🔁 Substitua pela sua chave da YouTube Data API
st.set_page_config(page_title="YouTube Pro Analytics", layout="wide", page_icon="🎥")
st.title("🎯 YouTube Pro Analytics")

# ------------------ ESTILO PERSONALIZADO ------------------
st.markdown("""
<style>
.custom-container {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}
input[type="text"] {
    flex-grow: 1;
}
.stButton>button {
    background: linear-gradient(90deg, #00ffe7, #00ccbb);
    color: #001219;
    font-weight: bold;
    font-size: 15px;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    box-shadow: 0 0 10px #00ffe7;
    margin-top: 4px;
}
</style>
<div class="custom-container">
""", unsafe_allow_html=True)

# ------------------ BARRA DE PESQUISA ------------------
col1, col2 = st.columns([5, 1])
with col1:
    entrada = st.text_input("🔍 Digite o nome do canal ou cole o link:", label_visibility="collapsed")
with col2:
    buscar = st.button("⏎ Buscar canal")
st.markdown("</div>", unsafe_allow_html=True)

# ------------------ FUNÇÕES DE API ------------------
def obter_id_canal(nome_ou_link):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    match = re.search(r"(?:channel/|user/|c/)?([A-Za-z0-9_-]+)", nome_ou_link)
    if "youtube.com" in nome_ou_link and match:
        query = match.group(1)
    else:
        query = nome_ou_link

    try:
        resposta = youtube.search().list(
            q=query,
            type="channel",
            part="id,snippet",
            maxResults=1
        ).execute()
        canal_id = resposta["items"][0]["id"]["channelId"]
        canal_nome = resposta["items"][0]["snippet"]["title"]
        return canal_id, canal_nome
    except:
        return None, None

def obter_videos(canal_id, max_results=10):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    resposta = youtube.search().list(
        channelId=canal_id,
        part="id,snippet",
        order="date",
        maxResults=max_results
    ).execute()
    
    videos = []
    for item in resposta["items"]:
        if item["id"]["kind"] == "youtube#video":
            video_id = item["id"]["videoId"]
            titulo = item["snippet"]["title"]
            data = item["snippet"]["publishedAt"][:10]
            videos.append({"ID": video_id, "Título": titulo, "Publicado em": data})
    return pd.DataFrame(videos)

# ------------------ AÇÃO DO BOTÃO ------------------
if buscar and entrada:
    st.info("🔄 Conectando à API do YouTube...")

    canal_id, canal_nome = obter_id_canal(entrada)

    if canal_id:
        st.success(f"✅ Canal encontrado: {canal_nome}")
        df_videos = obter_videos(canal_id, max_results=10)
        st.dataframe(df_videos)

        # Gráfico de barras
        fig = go.Figure(go.Bar(
            x=df_videos["Título"],
            y=[1]*len(df_videos),  # Placeholder de volume
            marker_color="#00ccbb"
        ))
        fig.update_layout(title="📊 Vídeos Recentes", xaxis_title="Título", yaxis_title="Qtd")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("❌ Canal não encontrado. Verifique o nome ou link.")

# ------------------ BLOCO PREMIUM ------------------
st.markdown("""
    <div style="margin-top: 15px; padding: 25px; border-radius: 12px; background: #f5f5f5; border-left: 6px solid #00ffe7; box-shadow: 0 0 12px rgba(0,0,0,0.05);">
        <h3 style="color:#000; margin-top:0;">🚀 Versão Premium disponível</h3>
        <div style="font-size: 17px; color: #333; margin-bottom: 14px;">
            Desbloqueie recursos avançados com o <strong>YouTube Pro Analytics Premium</strong>:
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; font-size: 16px; color:#111;">
            <div>📈 Até 50 vídeos por canal</div>
            <div>📊 Gráficos interativos + Excel</div>
            <div>🗓️ Filtro por período e palavras-chave</div>
            <div>💡 Métricas com insights e estimativas</div>
            <div>🔒 Suporte dedicado + acesso exclusivo</div>
        </div>
        <div style="margin-top: 20px; display: flex; flex-wrap: wrap; gap: 16px;">
            <a href="https://youtube-pro-analytics-premium-oxulwvn6ava4pbj94hzuqe.streamlit.app" target="_blank" style="text-decoration: none;">
                <div style="background: linear-gradient(90deg, #00ffe7, #00ccbb); padding: 12px 20px; border-radius: 8px; color: #001219; font-weight: bold; font-size: 15px; box-shadow: 0 0 10px #00ffe7;">
                    🚀 Acessar Premium
                </div>
            </a>
            <a href="https://wa.me/5521992156687?text=Olá! Quero a versão Premium do YouTube Pro Analytics. Pode me ajudar?" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25D366; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold; font-size: 15px; display: flex; align-items: center; gap: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/124/124034.png" alt="WhatsApp" width="18" height="18"> WhatsApp
                </div>
            </a>
            <!-- Botão da Hotmart -->
            <a href="https://readynerd3.hotmart.host/youtube-pro-analytics-acesso-premium-6c31a725-a7c4-4739-bc18-bfef106d9799" target="_blank" style="text-decoration: none;">
               <div style="background-color: #ff6f00; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold; font-size: 15px;">
                 🛒 Comprar na Hotmart
               </div>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)
