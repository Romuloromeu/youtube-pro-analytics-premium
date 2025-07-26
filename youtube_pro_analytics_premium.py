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
st.title("🔓 YouTube Pro Analytics – Premium")

# ------------------ CONTROLE DE LINK DE INDICAÇÃO ------------------
param_ref = st.query_params.get("ref", [None])[0]
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

# ------------------ VALIDAÇÃO DE CHAVE VIA PLANILHA ------------------

# Função para obter nome do dispositivo (hostname)
def get_device_id():
    return socket.gethostname()

# Função para conectar na planilha Google Sheets
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

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
    
    registros = planilha.get_all_records()
    st.write(registros)  # Exibe os registros da planilha no app Streamlit

    return planilha


    caminho_credenciais = os.path.join(os.path.dirname(__file__), 'secrets', 'credenciais.json')
    credenciais = Credentials.from_service_account_file(caminho_credenciais, scopes=escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key("13bdoTVkneLEAlcvShsYAP0ajsegN0csVUTf_nK9Plfk").worksheet("Sheet1")
    return planilha


# Função para validar chave e e-mail na planilha
def validar_chave(email_input, chave_input, planilha):
    registros = planilha.get_all_records()
    device_id = get_device_id()
    for i, row in enumerate(registros):
        email_planilha = row.get("Email", "").strip().lower()
        chave_planilha = row.get("Chave", "").strip()
        status_planilha = row.get("Status", "").strip().lower()
        dispositivo_planilha = row.get("ID do Dispositivo", "").strip()

        if email_planilha == email_input.strip().lower() and chave_planilha == chave_input.strip():
            if status_planilha != "ativo":
                return False, "❌ Sua chave está inativa ou bloqueada."

            if dispositivo_planilha == "":
                planilha.update_cell(i + 2, 6, device_id)  # Atualiza coluna F (6)
                return True, "✅ Chave validada e dispositivo vinculado com sucesso."

            elif dispositivo_planilha == device_id:
                return True, "✅ Acesso autorizado para este dispositivo."

            else:
                return False, "❌ Esta chave já está vinculada a outro dispositivo."
    return False, "❌ Chave ou e-mail inválido."


            if str(row["ID do Dispositivo"]).strip() == "":
                planilha.update_cell(i + 2, 6, device_id)  # Coluna F = ID do Dispositivo
                return True, "✅ Chave validada e dispositivo vinculado com sucesso."

            elif row["ID do Dispositivo"] == device_id:
                return True, "✅ Acesso autorizado para este dispositivo."

            else:
                return False, "❌ Esta chave já está vinculada a outro dispositivo."
    return False, "❌ Chave ou e-mail inválido."

# Entrada para email e chave
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
else:
    # Se não digitou, considera bônus ou gratuito só para avançar na UI (sem liberar premium)
    chave_valida = False

# ------------------ CONTROLE DE ACESSO ------------------

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

st.markdown("""
<div style="margin-top: 20px; display: flex; justify-content: flex-start;">
    <a href="https://youtube-pro-analytics-premium-oxulwvn6ava4pbj94hzuqe.streamlit.app" target="_blank" style="text-decoration: none;">
        <div style="background: linear-gradient(90deg, #00ffe7, #00ccbb); 
                    padding: 12px 20px; 
                    border-radius: 8px; 
                    color: #001219; 
                    font-weight: bold; 
                    font-size: 15px; 
                    box-shadow: 0 0 10px #00ffe7;
                    max-width: 280px;
                    text-align: center;">
            👀 Usar Versão Pública (Limitada)
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

st.stop()

st.success(msg_chave)

if chave_valida:
    st.success(msg_chave)
elif bonus_valido:
    st.success("🎁 Acesso liberado por convite – expira em até 3 dias")
else:
    st.success("✅ Acesso Gratuito liberado")

# ----------------------------------------------------
# Aqui continua todo o seu código original para YouTube Analytics
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
st.success(f"✅ {len(df)} vídeos carregados do canal **{nome_canal}**")

# Filtro por data personalizada
st.markdown("### 📆 Filtro por Período")
data_inicio = st.date_input("De:", df['DataHora'].min().date())
data_fim = st.date_input("Até:", df['DataHora'].max().date())

df_filtrado = df[(df['DataHora'].dt.date >= data_inicio) & (df['DataHora'].dt.date <= data_fim)]

# VISÃO GERAL
df_mes = df_filtrado[df_filtrado['DataHora'].dt.month == datetime.now().month]
df_ano = df_filtrado[df_filtrado['DataHora'].dt.year == datetime.now().year]
top5_mes = df_mes.nlargest(5, 'Visualizações')
top5_ano = df_ano.nlargest(5, 'Visualizações')
df20 = df_filtrado.nlargest(20, 'DataHora')

st.markdown("## 📊 Visão Geral")
col1, col2, col3 = st.columns(3)
col1.metric("🎮 Total de vídeos", len(df_filtrado))
col2.metric("📈 Média de views", int(df_filtrado['Visualizações'].mean()))
col3.metric("🗓 Vídeos este mês", len(df_mes))

# GRÁFICO PIZZA
st.subheader("🥧 Top 5 Vídeos do Ano")
fig1 = go.Figure(data=[go.Pie(
    labels=top5_ano['Título'],
    values=top5_ano['Visualizações'],
    hole=0.3,
    pull=[0.05]*len(top5_ano),
    hoverinfo='label+percent+value',
    textinfo='percent+label',
    marker=dict(line=dict(color='gray', width=1))
)])
st.plotly_chart(fig1, use_container_width=True)

# GRÁFICO BARRAS MELHORADO
st.subheader("📊 Top 5 Vídeos do Mês")
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
fig_bar.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_bar, use_container_width=True)

# TABELA DE VÍDEOS RECENTES
st.subheader("🌟 20 Vídeos Mais Recentes")
st.dataframe(df20[['Título','Data','Hora','Dia da Semana','Visualizações','Likes','Dislikes']])

# BUSCA POR VÍDEO ESPECÍFICO
st.markdown("## 🔍 Buscar Vídeo Específico")
video_busca = st.text_input("Digite parte do título do vídeo que deseja buscar:")
if video_busca:
    resultados = df[df['Título'].str.contains(video_busca, case=False, na=False)]
    if not resultados.empty:
        st.success(f"{len(resultados)} vídeo(s) encontrado(s):")
        for idx, row in resultados.iterrows():
            with st.expander(f"📹 {row['Título']}"):
                st.write(f"**Título:** {row['Título']}")
                st.write(f"**Data:** {row['Data']}")
                st.write(f"**Hora:** {row['Hora']}")
                st.write(f"**Dia da Semana:** {row['Dia da Semana']}")
                st.write(f"**Visualizações:** {row['Visualizações']:,}")
                st.write(f"**Likes:** {row['Likes']:,}")
                st.write(f"**Dislikes:** {row['Dislikes']:,}")
                video_url = f"https://www.youtube.com/watch?v={row['video_id']}"
                st.markdown(f"[🔗 Assistir no YouTube]({video_url})")
    else:
        st.warning("🔍 Nenhum vídeo encontrado com esse título.")

# DOWNLOAD EXCEL
st.download_button("📅 Baixar Relatório em Excel", data=gerar_excel(df), file_name="relatorio_pro_youtube.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
