import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import re
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
import socket

# Configurações da página
st.set_page_config(page_title="YouTube Pro Analytics Premium", layout="wide", page_icon="🔓")

# ------------------ CONTROLE DE LINK DE INDICAÇÃO ------------------
param_ref = st.experimental_get_query_params().get("ref", [None])[0]
if param_ref:
    st.session_state['ref_user'] = param_ref
    st.session_state['bonus_ativo'] = True
    if 'bonus_inicio' not in st.session_state:
        st.session_state['bonus_inicio'] = datetime.now()

# Verificar validade dos 3 dias de bônus
bonus_valido = False
if st.session_state.get('bonus_ativo'):
    dias_passados = (datetime.now() - st.session_state['bonus_inicio']).days
    if dias_passados <= 3:
        bonus_valido = True
    else:
        st.session_state['bonus_ativo'] = False
        bonus_valido = False

# ------------------ FUNÇÕES ------------------

def get_device_id():
    return socket.gethostname()

def conectar_planilha():
    escopo = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    secret = st.secrets["google_service_account"]

    info = {
        "type": secret["type"],
        "project_id": secret["project_id"],
        "private_key_id": secret["private_key_id"],
        "private_key": secret["private_key"].replace("\\n", "\n"),
        "client_email": secret["client_email"],
        "client_id": secret["client_id"],
        "auth_uri": secret["auth_uri"],
        "token_uri": secret["token_uri"],
        "auth_provider_x509_cert_url": secret["auth_provider_x509_cert_url"],
        "client_x509_cert_url": secret["client_x509_cert_url"],
    }

    credenciais = Credentials.from_service_account_info(info, scopes=escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key("13bdoTVkneLEAlcvShsYAP0ajsegN0csVUTf_nK9Plfk").worksheet("Sheet1")
    
    return planilha

def validar_chave(email_input, chave_input, planilha):
    registros = planilha.get_all_records()
    device_id = get_device_id()

    for i, row in enumerate(registros):
        email_planilha = str(row["Email"]).strip()
        chave_planilha = str(row["Chave"]).strip()
        status = str(row["Status"]).strip().lower()
        dispositivo = str(row["ID do Dispositivo"]).strip()

        if email_input == email_planilha and chave_input == chave_planilha:
            if status != "ativo":
                return False, "❌ Sua chave está inativa ou bloqueada."

            if dispositivo == "":
                planilha.update_cell(i + 2, 6, device_id)
                return True, "✅ Chave validada e dispositivo vinculado com sucesso."

            elif dispositivo == device_id:
                return True, "✅ Acesso autorizado para este dispositivo."

            else:
                return False, "🔒 Esta chave já foi usada em outro dispositivo."

    return False, "❌ Chave ou e-mail inválido."

# ------------------ INTERFACE DE LOGIN ------------------

st.title("🔓 YouTube Pro Analytics – Premium")
st.markdown("---")

st.header("🔐 Validação de Acesso Premium")

email_usuario = st.text_input("Digite seu e-mail:")
chave_digitada = st.text_input("Digite sua chave de ativação:", type="password")

chave_valida = False
msg_chave = ""

if chave_digitada and email_usuario:
    try:
        planilha = conectar_planilha()
        chave_valida, msg_chave = validar_chave(email_usuario.strip(), chave_digitada.strip(), planilha)
        if chave_valida:
            st.success(msg_chave)
        else:
            st.error(msg_chave)
    except Exception as e:
        st.error(f"❌ Erro ao validar chave: {e}")
        st.stop()
else:
    st.info("🔑 Preencha o e-mail e a chave de ativação para continuar.")
    st.stop()

# Se não validou a chave, mas tem bônus, libera pelo convite
if not chave_valida and bonus_valido:
    chave_valida = True
    msg_chave = "🎁 Acesso liberado por convite – expira em até 3 dias"
    st.success(msg_chave)

# Se chave inválida e sem bônus, bloqueia acesso e mostra opções
if not chave_valida:
    st.markdown("<hr style='margin-top: 15px; margin-bottom: 10px;'>", unsafe_allow_html=True)
    st.markdown("## 🔑 Ainda não tem sua chave de ativação?")

    nome_pre = st.text_input("Digite seu nome para agilizar o atendimento (opcional):", value="")
    nome_formatado = nome_pre.strip() if nome_pre.strip() else "Cliente"
    mensagem = f"Olá! Me chamo {nome_formatado} e quero adquirir a chave de acesso Premium do YouTube Pro Analytics. Pode me ajudar?"
    mensagem_url = urllib.parse.quote(mensagem)
    whatsapp_url = f"https://wa.me/5521992156687?text={mensagem_url}"
    hotmart_url = f"https://hotmart.com/seu-produto?cliente={urllib.parse.quote(nome_formatado)}"

    st.markdown(f"""
    <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 1rem;">
        <a href="{hotmart_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #e67e22; padding: 12px 24px; border-radius: 8px; color: white; font-weight: bold; font-size: 16px;">
                🛒 Adquirir na Hotmart
            </div>
        </a>
        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; padding: 12px 24px; border-radius: 8px; color: white; font-weight: bold; font-size: 16px; display: flex; align-items: center; gap: 10px;">
                <img src="https://cdn-icons-png.flaticon.com/512/124/124034.png" alt="WhatsApp" width="20" height="20">
                Falar com Suporte no WhatsApp
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.warning("🔐 Acesso restrito. Insira a chave correta para acessar o conteúdo Premium.")
    st.stop()

# ------------------ SE CHEGOU AQUI, ACESSO LIBERADO ------------------

st.markdown("---")
st.success(msg_chave)

# ----------------------------------------------------
# A partir daqui seu código original do YouTube Analytics começa
# ----------------------------------------------------

API_KEY = 'AIzaSyANI2GxhU0bMyHhns1BbEmiVMVWGLKZgZA'
MAX_VIDEOS = 50

def conectar_youtube():
    return build('youtube', 'v3', developerKey=API_KEY)

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

def buscar_nome_canal(channel_id):
    try:
        youtube = conectar_youtube()
        resposta = youtube.channels().list(id=channel_id, part="snippet").execute()
        if resposta.get('items'):
            return resposta['items'][0]['snippet']['title']
    except Exception:
        return "Canal YouTube"

def buscar_estatisticas_em_lotes(youtube, video_ids, lote=50):
    view_map = {}
    for i in range(0, len(video_ids), lote):
        ids_lote = video_ids[i:i + lote]
        resposta = youtube.videos().list(id=",".join(ids_lote), part='statistics').execute()
        for item in resposta.get('items', []):
            vid = item['id']
            stats = item['statistics']
            view_map[vid] = {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'dislikes': int(stats.get('dislikeCount', 0)) if 'dislikeCount' in stats else 0
            }
    return view_map

def coletar_videos(channel_id, max_videos=MAX_VIDEOS):
    youtube = conectar_youtube()
    uploads_id = youtube.channels().list(id=channel_id, part='contentDetails').execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    videos, token = [], None
    while len(videos) < max_videos:
        resp = youtube.playlistItems().list(
            playlistId=uploads_id,
            part='snippet', maxResults=50, pageToken=token).execute()
        for i in resp.get('items', []):
            try:
                vid_id = i['snippet']['resourceId']['videoId']
                pub_utc = i['snippet']['publishedAt']
                dt_br = datetime.strptime(pub_utc, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
                videos.append((vid_id, i['snippet']['title'], dt_br))
            except KeyError:
                continue
        token = resp.get('nextPageToken')
        if not token or len(videos) >= max_videos:
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

entrada = st.text_input("🔍 Digite o nome do canal ou cole o link:")
if not entrada:
    st.info("⭐ O YouTube Pro Analytics ajuda você a descobrir quais conteúdos realmente valem monetizar.")
    st.stop()

with st.spinner("🔄 Conectando ao YouTube..."):
    chan_id = buscar_channel_id(entrada)

if not chan_id:
    st.error("❌ Canal não encontrado. Verifique o nome ou link.")
    st.stop()

df = coletar_videos(chan_id)
if df.empty:
    st.warning("⚠ Não foi possível carregar os vídeos desse canal.")
    st.stop()

nome_canal = buscar_nome_canal(chan_id)
st.header(f"📊 Análise do canal: {nome_canal}")
st.write(f"Número de vídeos analisados: {len(df)}")

st.markdown("---")

# Visualização gráfica
fig_views = px.bar(df.sort_values('DataHora', ascending=True), x='DataHora', y='Visualizações', labels={'DataHora':'Data', 'Visualizações':'Visualizações'}, title='Visualizações por vídeo (mais recentes)')
st.plotly_chart(fig_views, use_container_width=True)

st.markdown("---")
st.subheader("📋 Dados detalhados dos vídeos")
st.dataframe(df[['Título','Data','Hora','Visualizações','Likes','Dislikes']].sort_values('DataHora', ascending=False))

# Download Excel
excel_data = gerar_excel(df)
st.download_button(
    label="📥 Baixar dados em Excel",
    data=excel_data,
    file_name=f"{nome_canal}_youtube_analytics.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
