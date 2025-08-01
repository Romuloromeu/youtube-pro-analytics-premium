import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import re
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
import socket

st.set_page_config(page_title="YouTube Pro Analytics Premium", layout="wide", page_icon="🔓")
st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #333;
        text-align: center;
        margin-bottom: 25px;
    }
    .button-row {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 30px;
    }
    .custom-button {
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 14px;
        font-weight: bold;
        color: #333;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    .custom-button:hover {
        background-color: #e0e0e0;
    }
    .highlight-box {
        border: 2px solid #0066cc;
        border-radius: 8px;
        padding: 20px;
        background-color: #f9f9ff;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔓 YouTube Pro Analytics – Premium</div>', unsafe_allow_html=True)

param_ref = st.query_params.get("ref", [None])[0]
if param_ref:
    st.session_state['ref_user'] = param_ref
    st.session_state['bonus_ativo'] = True
    if 'bonus_inicio' not in st.session_state:
        st.session_state['bonus_inicio'] = datetime.now()

bonus_valido = False
if st.session_state.get('bonus_ativo'):
    dias_passados = (datetime.now() - st.session_state['bonus_inicio']).days
    if dias_passados <= 3:
        bonus_valido = True
    else:
        st.session_state['bonus_ativo'] = False
        bonus_valido = False

def get_device_id():
    return socket.gethostname()

def conectar_planilha():
    dados_credenciais = {
        "type": "service_account",
        "project_id": "mindful-acre-465615-m4",
        "private_key_id": "bf3d0d98e9d9ff017b0d59c05c3540d15c195fcf",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCvbJskJ9B+VrOI
ZXElGVU/fVX8wIDUDCuOqHeh6drvZiMfnTvNZb3UsQ1ySAgeD5/F77DDf9BX9hc0
OHsXADXo8qR3+8ca3s0rxXbH/kPcgMDX3mcXXCkShDafslj+3XccFvHvzhfQ+vIT
xTFlA0QuGrNQ8OM6aR6KCgk9JPh7sOvQYbUq09dX6IsITJULyp/XS72P9qc8qwpj
KIcjX9lOcSdoVAbSzNOKOO+6ILjwMQaG0R/fpvy00LNIeHm0FB13BGEzgy3VFkEA
iX1Oie8DRPc5qNpV+I5Cn/Z/4/J16IM3hK3SZoijGiOJNy0E1FVUDEAQGu+EhoKV
yNL7hpL3AgMBAAECggEAA+nSVC4nMopQmvxYV9GG21G6d1b8CL70wcv0T0JeRfTr
V6s0SFK6t2HzwNbmh3UlxU6hjNrvFOdCgUG5TTwN99Jh5ONS/8B0p0NScQe1D9g3
dRlbB2Rg7i7Q4SMjZRwfqhrA7u6UDW9rsxE1FuHJxZWG5olZKFZr/fxXVGvctzWj
uJJ837mAy/jSJJPXIn9+ID/YEofb1h13/EQAcL0rM7BbiTuBUOAA/48SzskzqT8V
dX2eejjETq9hESe/2fxD4OzuakzLOofxewmgdLUuffBLUJ2wcVxo7+qDeEIyjYrk
fsaejHaicDl9iAvi6zsQp/T5Myd65RK96/k/CSqPsQKBgQDU2XgXqZOFJ87wQiSR
6iskbf4r/57yUErKo8NmvYRTR+2905wvWOmABpF4k0yeMOTx68ygqfK2CZiJcHPo
+4YSMmKYjy+8mseFilZ6vTeF74qfQct/QxIQjgRnc8+VTTkl608QHlFCfejjWrbW
z+J19hr/2W2KXa8GouLxzvFe2wKBgQDS/NRZhyODTvwq0FCvuSbm+DElSOmtktha
Dz56+Kl0XXD8vSjcqaKPedX6gNRgXA8FcjR7CQKhHiQ+wzZ35xyZ8X3T+6pgL5if
n64FT4v795LmsUwvdujj6IjBV26TItQhHtZ6fktl3RAGIPH8Air5zbkD9Lg+Lpwg
EdyY9avRFQKBgBR9fu8gNwBZjbVZWLXnShHuuMo5iG6hRiHt0/C/C88MnJlqlp2E
PK5Dc5uc6oJMCK41WfSZh7D4iYOpnK7wD78OtKklF55bdBup7ptQPdkZ70lXhySQ
K1wGn+vpnTEtRvQci/bsRDxXbKT+ZZ2WU6GxeHXq032/eQr1gU1v85KDAoGAWA2K
Nd7vVEKnfNq5gcy8zpHwOMZIN9dcEaHhCoMyfUzt9ZygLA9jt4s6YTRY7eodnsE9
48cr4L/qkoL3/WxnhFvDjq+uODxE7wE+KBs9qad2GG8QA5MVuN/4CvCJRkC31SbA
jhidMOLkaBphwzHIa76Oo3cDWXgsUjoCHZgR380CgYEAuN3VxBHHhUnEht22UNeH
a7f6FXBDkf7XvJF4dQI34MEYMxt5F4vlMFZWUf8wZIyciGxj+Yl+kGj6kp8MlHD2
DsJJQMLr0OifCEOvDLkJSyDeR4Rf351WyDoWaBNBBwTKJb7vcVBopHcLgZSLzeDT
c8IAYzLK+WseArNcbWVh740=
-----END PRIVATE KEY-----""",
        "client_email": "chave-validacao-bot@mindful-acre-465615-m4.iam.gserviceaccount.com",
        "client_id": "108446453747344915328",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/chave-validacao-bot%40mindful-acre-465615-m4.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    escopo = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciais = Credentials.from_service_account_info(dados_credenciais, scopes=escopo)
    gc = gspread.authorize(credenciais)
    planilha = gc.open_by_key("1kg-cRRB-iyagEpJF4CuXLm53ahiJ1g5DowmDFPZkIww").worksheet("Sheet1")
    return planilha

# Continuação da lógica do app com os elementos visuais integrados


def validar_chave(email_input, chave_input, planilha):
    registros = planilha.get_all_records(expected_headers=["Email", "Chave", "Status", "Nome ", "WhatsApp", "ID do Dispositivo"])
    device_id = get_device_id()
    for i, row in enumerate(registros):
        if row["Email"] == email_input and row["Chave"] == chave_input:
            if str(row["Status"]).strip().lower() != "ativo":
                return False, "❌ Sua chave está inativa ou bloqueada."
            if str(row["ID do Dispositivo"]).strip() == "":
                planilha.update_cell(i + 2, 6, device_id)
                return True, "✅ Chave validada e dispositivo vinculado com sucesso."
            elif row["ID do Dispositivo"] == device_id:
                return True, "✅ Acesso autorizado para este dispositivo."
            else:
                return False, "❌ Esta chave já está vinculada a outro dispositivo."
    return False, "❌ Chave ou e-mail inválido."

email_usuario = st.text_input("Digite seu e-mail:")
chave_digitada = st.text_input("Digite sua chave de ativação:", type="password")
chave_valida = False
msg_chave = ""

if chave_digitada and email_usuario:
    try:
        planilha = conectar_planilha()
        chave_valida, msg_chave = validar_chave(email_usuario.strip(), chave_digitada.strip(), planilha)
    except Exception as e:
        st.error(f"❌ Erro ao validar chave: {e}")
        st.stop()

if not chave_valida and not bonus_valido:
    nome_pre = st.text_input("Digite seu nome para agilizar o atendimento (opcional):", value="")
    nome_formatado = nome_pre.strip() if nome_pre.strip() else "Cliente"
    hotmart_url = f"https://hotmart.com/seu-produto?cliente={urllib.parse.quote(nome_formatado)}"
    suporte_url = "https://wa.me/5521992156687?text=Olá! Quero a versão Premium do YouTube Pro Analytics. Pode me ajudar?"

    st.markdown(f"""
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
            <a href="https://youtube-pro-analytics-premium-nvw3q4bkbnajgxtcxclhiy.streamlit.app/" target="_blank" style="text-decoration: none;">
                <div style="background: linear-gradient(90deg, #00ffe7, #00ccbb); padding: 12px 20px; border-radius: 8px; color: #001219; font-weight: bold; font-size: 15px; box-shadow: 0 0 10px #00ffe7;">
                    🚀 Acesso Gratuito
                </div>
            </a>
            <a href="https://wa.me/5521992156687" target="_blank" style="text-decoration: none;">
              <div style="background-color: #25D366; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold; font-size: 15px; display: flex; align-items: center; gap: 10px;">
                 <img src="https://cdn-icons-png.flaticon.com/512/124/124034.png" alt="WhatsApp" width="18" height="18">
                  WhatsApp
              </div>
            </a>
            <a href="https://readynerd3.hotmart.host/youtube-pro-analytics-acesso-premium-6c31a725-a7c4-4739-bc18-bfef106d9799" target="_blank" style="text-decoration: none;">
               <div style="background-color: #ff6f00; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold; font-size: 15px;">
                 🛒 Comprar na Hotmart
              </div>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

   
st.markdown("""
<div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 10px; border: 2px solid #007BFF;">
    <h3 style="color: #007BFF;">🔍 Pesquise o canal do YouTube para análise:</h3>
</div>
""", unsafe_allow_html=True)

entrada = st.text_input("🔍 Digite o nome do canal ou cole o link:")
if not entrada:
    st.info("⭐ O YouTube Pro Analytics ajuda você a descobrir quais conteúdos realmente valem monetizar.")
    st.stop()

def conectar_youtube():
    return build('youtube', 'v3', developerKey='AIzaSyANI2GxhU0bMyHhns1BbEmiVMVWGLKZgZA')

def extrair_channel_id(texto):
    match = re.search(r'(?:channel/|c/|user/)?([A-Za-z0-9_-]{24,})', texto)
    return match.group(1) if match else texto.strip()

def buscar_channel_id(input_usuario):
    youtube = conectar_youtube()
    chan_id = extrair_channel_id(input_usuario)
    try:
        resposta = youtube.channels().list(id=chan_id, part="snippet").execute()
        if resposta.get('items'):
            return chan_id
    except Exception:
        pass
    try:
        resposta = youtube.search().list(q=input_usuario, part='snippet', type='channel', maxResults=1).execute()
        if resposta.get('items'):
            return resposta['items'][0]['snippet']['channelId']
    except Exception:
        pass
    return None

with st.spinner("🔄 Conectando ao YouTube..."):
    chan_id = buscar_channel_id(entrada)

if not chan_id:
    st.error("❌ Canal não encontrado. Verifique o nome ou link.")
    st.stop()

def buscar_nome_canal(channel_id):
    youtube = conectar_youtube()
    resposta = youtube.channels().list(id=channel_id, part="snippet").execute()
    return resposta['items'][0]['snippet']['title'] if resposta.get('items') else "Canal YouTube"

def buscar_estatisticas_em_lotes(youtube, video_ids, lote=50):
    view_map = {}
    for i in range(0, len(video_ids), lote):
        ids_lote = video_ids[i:i + lote]
        resposta = youtube.videos().list(id=",".join(ids_lote), part='statistics').execute()
        for item in resposta.get('items', []):
            stats = item['statistics']
            view_map[item['id']] = {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'dislikes': int(stats.get('dislikeCount', 0)) if 'dislikeCount' in stats else 0
            }
    return view_map

def coletar_videos(channel_id, max_videos=50):
    youtube = conectar_youtube()
    uploads_id = youtube.channels().list(id=channel_id, part='contentDetails').execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    videos, token = [], None
    while len(videos) < max_videos:
        resp = youtube.playlistItems().list(playlistId=uploads_id, part='snippet', maxResults=50, pageToken=token).execute()
        for i in resp.get('items', []):
            try:
                vid_id = i['snippet']['resourceId']['videoId']
                pub_utc = i['snippet']['publishedAt']
                dt_br = datetime.strptime(pub_utc, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
                videos.append((vid_id, i['snippet']['title'], dt_br))
            except KeyError:
                continue
        token = resp.get('nextPageToken')
        if not token:
            break
    df = pd.DataFrame(videos, columns=['video_id','Título','DataHora'])
    view_map = buscar_estatisticas_em_lotes(youtube, df['video_id'].tolist())
    df['Visualizações'] = df['video_id'].map(lambda x: view_map[x]['views'])
    df['Likes'] = df['video_id'].map(lambda x: view_map[x]['likes'])
    df['Dislikes'] = df['video_id'].map(lambda x: view_map[x]['dislikes'])
    df['Data'] = df['DataHora'].dt.date.astype(str)
    df['Hora'] = df['DataHora'].dt.time.astype(str)
    df['Dia da Semana'] = df['DataHora'].dt.day_name()
    return df

def gerar_excel(df):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Vídeos")
    out.seek(0)
    return out.getvalue()

df = coletar_videos(chan_id)
nome_canal = buscar_nome_canal(chan_id)

st.success(f"✅ {len(df)} vídeos carregados do canal **{nome_canal}**")

st.markdown("### 🗓️ Filtro por Período")
data_inicio = st.date_input("De:", df['DataHora'].min().date())
data_fim = st.date_input("Até:", df['DataHora'].max().date())

# Garante que as datas estejam no intervalo correto
if data_inicio > data_fim:
    st.warning("⚠️ A data inicial não pode ser maior que a final.")
    st.stop()

# Conversão de DataHora para Data (date puro)
df['Data'] = df['DataHora'].dt.date

# Filtro de período
df_filtrado = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]

# Protege contra DataFrame vazio
if df_filtrado.empty:
    st.warning("⚠️ Nenhum vídeo encontrado no período selecionado.")
    st.stop()

# Top 5 do mês com base no mês e ano inicial do filtro
mes_filtro = data_inicio.month
ano_filtro = data_inicio.year
df_mes = df_filtrado[(df_filtrado['DataHora'].dt.month == mes_filtro) & (df_filtrado['DataHora'].dt.year == ano_filtro)]
df_ano = df_filtrado[df_filtrado['DataHora'].dt.year == ano_filtro]

top5_mes = df_mes.nlargest(5, 'Visualizações')
top5_ano = df_ano.nlargest(5, 'Visualizações')
df20 = df_filtrado.nlargest(20, 'DataHora')

st.markdown("## 📊 Visão Geral")
col1, col2, col3 = st.columns(3)

total_videos = len(df_filtrado)
media_views = df_filtrado['Visualizações'].mean()
media_views = int(media_views) if pd.notnull(media_views) else 0
videos_mes = len(df_mes)

col1.metric("🎮 Total de vídeos", total_videos)
col2.metric("📈 Média de views", media_views)
col3.metric("🗓️ Vídeos neste mês/intervalo", videos_mes)

if not top5_ano.empty:
    st.subheader("🥧 Top 5 Vídeos do Ano")
    fig1 = go.Figure(data=[go.Pie(labels=top5_ano['Título'], values=top5_ano['Visualizações'], hole=0.3)])
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("ℹ️ Nenhum vídeo do ano encontrado no intervalo selecionado.")

if not top5_mes.empty:
    # GRÁFICO BARRAS MELHORADO
    st.subheader("📈 Top 5 Vídeos do Mês")
    fig_bar = px.bar(
        top5_mes,
        x='Visualizações',
        y='Título',
        orientation='h',
        color='Visualizações',
        color_continuous_scale='Teal',
        title='Top 5 Vídeos do Mês',
        labels={'Título': 'Título do Vídeo', 'Visualizações': 'Views'}
    )
    fig_bar.update_layout(
        yaxis=dict(autorange="reversed"),
        height=400  # Define uma altura proporcional ao conteúdo
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("ℹ️ Nenhum vídeo do mês encontrado no intervalo selecionado.")

st.subheader("🌟 20 Vídeos Mais Recentes")
st.dataframe(df20[['Título','Data','Hora','Dia da Semana','Visualizações','Likes','Dislikes']])

st.markdown("## 🔍 Buscar Vídeo Específico")
video_busca = st.text_input("Digite parte do título do vídeo que deseja buscar:")
if video_busca:
    resultados = df_filtrado[df_filtrado['Título'].str.contains(video_busca, case=False, na=False)]
    if not resultados.empty:
        st.success(f"{len(resultados)} vídeo(s) encontrado(s):")
        for idx, row in resultados.iterrows():
            with st.expander(f"📹 {row['Título']}"):
                st.write(f"**Data:** {row['Data']}")
                st.write(f"**Hora:** {row['Hora']}")
                st.write(f"**Dia da Semana:** {row['Dia da Semana']}")
                st.write(f"**Visualizações:** {row['Visualizações']:,}")
                st.write(f"**Likes:** {row['Likes']:,}")
                st.write(f"**Dislikes:** {row['Dislikes']:,}")
                st.markdown(f"[🔗 Assistir no YouTube](https://www.youtube.com/watch?v={row['video_id']})")
    else:
        st.warning("🔍 Nenhum vídeo encontrado com esse título no período filtrado.")

st.download_button("📅 Baixar Relatório em Excel", data=gerar_excel(df_filtrado), file_name="relatorio_pro_youtube.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


