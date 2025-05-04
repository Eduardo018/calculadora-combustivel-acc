import streamlit as st
import plotly.graph_objects as go

# ========== CONFIGURAÇÕES ==========

st.set_page_config(
    page_title="Estratégia de Combustível - ACC", 
    layout="wide", 
    page_icon="⛽",
    initial_sidebar_state="expanded"
)

# Cores profissionais para o dashboard
CORES_ESTRATEGIAS = {
    "Conservadora (2 voltas extras)": "#2ca02c",
    "Recomendada (1.5 voltas extras)": "#1f77b4",
    "Arriscada (0.5 volta extra)": "#d62728"
}

CORES_DASHBOARD = {
    "background": "#0E1117",
    "text": "#FAFAFA",
    "primary": "#FF4B4B",
    "secondary": "#1A1A2E",
    "card": "#1E1E2E"
}

# CSS personalizado para alinhamento perfeito
st.markdown(f"""
    <style>
    /* Configurações gerais */
    .main {{
        background-color: {CORES_DASHBOARD['background']};
        color: {CORES_DASHBOARD['text']};
    }}
    
    /* Containers e cards */
    .metric-container {{
        background-color: {CORES_DASHBOARD['card']};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }}
    
    .strategy-header {{
        background-color: {CORES_DASHBOARD['secondary']};
        border-radius: 10px 10px 0 0;
        padding: 12px;
        text-align: center;
        color: white;
        font-weight: 700;
        margin-bottom: 0;
    }}
    
    .strategy-card {{
        background-color: {CORES_DASHBOARD['card']};
        border-radius: 0 0 10px 10px;
        padding: 20px;
        height: 100%;
    }}
    
    /* Grid alignment */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        margin-top: 15px;
    }}
    
    .metric-item {{
        background-color: {CORES_DASHBOARD['secondary']};
        border-radius: 8px;
        padding: 12px;
    }}
    
    /* Elementos de texto */
    .metric-title {{
        font-size: 12px;
        font-weight: 600;
        color: #AAAAAA;
        margin-bottom: 5px;
    }}
    
    .metric-value {{
        font-size: 18px;
        font-weight: 700;
    }}
    
    /* Elementos de formulário */
    .stNumberInput, .stRadio, .stSelectbox {{
        margin-bottom: 10px;
    }}
    
    .stTextInput>div>div>input {{
        background-color: {CORES_DASHBOARD['secondary']};
        color: {CORES_DASHBOARD['text']};
    }}
    
    /* Botões */
    .stButton>button {{
        background-color: {CORES_DASHBOARD['primary']};
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
    }}
    
    /* Barras de progresso */
    .stProgress>div>div>div {{
        background-color: {CORES_DASHBOARD['primary']};
    }}
    
    .progress-label {{
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-bottom: 5px;
    }}
    
    /* Alinhamento de colunas */
    .st-emotion-cache-1v7f65g {{
        display: flex;
        align-items: stretch;
    }}
    
    /* Ajuste de expansores */
    .st-expander {{
        background-color: {CORES_DASHBOARD['card']};
        border: 1px solid #333344;
    }}
    
    .st-expander .st-expanderHeader {{
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)

# ========== FUNÇÕES ==========

def tempo_em_segundos(minutos, segundos):
    return minutos * 60 + segundos

def formatar_tempo(segundos):
    minutos = int(segundos // 60)
    segundos_rest = int(segundos % 60)
    return f"{minutos}:{segundos_rest:02d}"

def calcular_estrategia_combustivel(volta_rapida, volta_lenta, consumo, duracao_corrida, stint_max, antec_box, margem_voltas, num_pitstops, reabastecimento):
    tempo_rapido = tempo_em_segundos(*volta_rapida)
    tempo_lento = tempo_em_segundos(*volta_lenta)
    media_tempo = (tempo_rapido + tempo_lento) / 2
    duracao_total_seg = duracao_corrida * 60

    voltas_estimada = duracao_total_seg / media_tempo
    voltas_com_margem = voltas_estimada + margem_voltas
    consumo_total = voltas_com_margem * consumo

    if not reabastecimento:
        combustivel_inicial = consumo_total
        numero_de_stints = 1
        combustivel_por_stint = [consumo_total]
        combustivel_por_parada = 0
    else:
        numero_de_stints = (duracao_corrida // stint_max) + (1 if duracao_corrida % stint_max else 0)
        combustivel_por_stint = [consumo_total / numero_de_stints] * numero_de_stints
        if numero_de_stints > 1:
            combustivel_por_stint[-1] *= 0.8
        combustivel_por_parada = sum(combustivel_por_stint[1:]) / num_pitstops if num_pitstops else 0
        combustivel_inicial = combustivel_por_stint[0]

    autonomia = duracao_total_seg / consumo_total * consumo

    return {
        "voltas_estimada": int(voltas_estimada),
        "media_tempo": media_tempo,
        "voltas_com_margem": int(voltas_com_margem),
        "consumo_total": consumo_total,
        "numero_de_stints": numero_de_stints,
        "combustivel_por_stint": combustivel_por_stint,
        "combustivel_por_parada": combustivel_por_parada,
        "combustivel_inicial": combustivel_inicial,
        "autonomia": autonomia
    }

def criar_grafico_estrategia(estrategias):
    fig = go.Figure()
    
    for nome, est in estrategias.items():
        color = CORES_ESTRATEGIAS[nome]
        
        fig.add_trace(go.Bar(
            x=[nome],
            y=[est['voltas_com_margem']],
            name='Voltas + Margem',
            marker_color=color,
            opacity=0.8,
            text=[f"{est['voltas_com_margem']}"],
            textposition='auto',
            hoverinfo='text',
            hovertext=f"Voltas totais: {est['voltas_com_margem']}<br>Combustível total: {est['consumo_total']:.2f}L"
        ))
        
        fig.add_trace(go.Scatter(
            x=[nome],
            y=[est['numero_de_stints'] * (max([e['voltas_com_margem'] for e in estrategias.values()]) / 5)],
            mode='markers+text',
            marker=dict(size=15, color=color),
            text=[f"Stints: {est['numero_de_stints']}"],
            textposition="top center",
            name='Número de Stints',
            hoverinfo='none'
        ))
    
    fig.update_layout(
        title='Comparação de Estratégias',
        barmode='group',
        plot_bgcolor=CORES_DASHBOARD['card'],
        paper_bgcolor=CORES_DASHBOARD['background'],
        font=dict(color=CORES_DASHBOARD['text']),
        xaxis_title='Estratégia',
        yaxis_title='Voltas',
        showlegend=False,
        height=400
    )
    
    return fig

# ========== INTERFACE ==========

# Cabeçalho alinhado
col1, = st.columns([1])

with col1:
    st.title("Calculadora de Estratégia de Combustível")
    st.caption("Otimize sua estratégia de pitstop e combustível para o Assetto Corsa Competizione")

# Divisão em abas
tab1, = st.tabs(["📊 Calculadora"])

with tab1:
    with st.expander("⚙️ CONFIGURAÇÕES DA CORRIDA", expanded=True):
        # Seção 1: Desempenho nas Voltas
        st.subheader("🏁 DESEMPENHO NAS VOLTAS")
        col1, col2 = st.columns(2)
        with col1:
            min_rapida = st.number_input("Minutos da volta mais rápida", 0, 10, 1, key="min_rapida")
            seg_rapida = st.number_input("Segundos da volta mais rápida", 0, 59, 50, key="seg_rapida")
        with col2:
            min_lenta = st.number_input("Minutos da volta mais lenta", 0, 10, 2, key="min_lenta")
            seg_lenta = st.number_input("Segundos da volta mais lenta", 0, 59, 20, key="seg_lenta")
        
        # Seção 2: Consumo de Combustível
        st.subheader("⛽ CONSUMO DE COMBUSTÍVEL")
        col3, col4 = st.columns(2)
        with col3:
            consumo = st.number_input("Consumo médio por volta (L)", 0.1, 10.0, step=0.1, value=3.25, key="consumo")
        with col4:
            margem_litros = st.number_input("Margem de segurança por volta (L)", 0.0, 2.0, step=0.1, value=0.0, key="margem")
        consumo += margem_litros

        # Seção 3: Configurações da Estratégia
        st.subheader("🏎️ CONFIGURAÇÕES DA ESTRATÉGIA")
        col5, col6, col7 = st.columns(3)
        with col5:
            duracao_corrida = st.number_input("Duração da corrida (min)", 1, 1000, value=30, key="duracao")
        with col6:
            stint_max = st.number_input("Duração máxima de stint (min)", 1, 1000, value=15, key="stint")
        with col7:
            antec_box = st.number_input("Antecipar pit (min)", 0, stint_max - 1, 1, key="antecipar")

        col8, col9 = st.columns(2)
        with col8:
            num_pitstops = st.number_input("Nº de pitstops obrigatórios", 0, 10, value=2, key="pits")
        with col9:
            reabastecimento = st.radio("Reabastecimento permitido?", ["Sim", "Não"], index=0, horizontal=True, key="reabastecer") == "Sim"

    if st.button("📈 CALCULAR ESTRATÉGIA", use_container_width=True, type="primary"):
        estrategias = {}
        margens = [2, 1.5, 0.5]
        nomes = list(CORES_ESTRATEGIAS.keys())

        for nome, margem in zip(nomes, margens):
            estrategias[nome] = calcular_estrategia_combustivel(
                (min_rapida, seg_rapida),
                (min_lenta, seg_lenta),
                consumo,
                duracao_corrida,
                stint_max,
                antec_box,
                margem,
                num_pitstops,
                reabastecimento
            )


        # Resultados detalhados
        st.subheader("📋 DETALHES DAS ESTRATÉGIAS")
        cols = st.columns(3)

        for i, (nome, est) in enumerate(estrategias.items()):
            with cols[i]:
                # Cabeçalho da estratégia
                st.markdown(
                    f"<div class='strategy-header' style='background-color:{CORES_ESTRATEGIAS[nome]};'>"
                    f"{nome}</div>",
                    unsafe_allow_html=True
                )
                
                # Card de métricas
                with st.container():
                    st.markdown("<div class='strategy-card'>", unsafe_allow_html=True)
                    
                    # Grid de métricas perfeitamente alinhadas
                    st.markdown("<div class='metric-grid'>", unsafe_allow_html=True)
                    
                    # Métrica 1
                    st.markdown(f"""
                        <div class='metric-item'>
                            <div class='metric-title'>VOLTAS ESTIMADAS</div>
                            <div class='metric-value'>{est['voltas_estimada']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Métrica 2
                    st.markdown(f"""
                        <div class='metric-item'>
                            <div class='metric-title'>VOLTAS + MARGEM</div>
                            <div class='metric-value'>{est['voltas_com_margem']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Métrica 3
                    st.markdown(f"""
                        <div class='metric-item'>
                            <div class='metric-title'>MÉDIA POR VOLTA</div>
                            <div class='metric-value'>{formatar_tempo(est['media_tempo'])}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Métrica 4
                    st.markdown(f"""
                        <div class='metric-item'>
                            <div class='metric-title'>COMBUSTÍVEL TOTAL</div>
                            <div class='metric-value'>{est['consumo_total']:.2f} L</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Métrica 5
                    st.markdown(f"""
                        <div class='metric-item'>
                            <div class='metric-title'>STINTS</div>
                            <div class='metric-value'>{est['numero_de_stints']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Métrica 6
                    st.markdown(f"""
                        <div class='metric-item'>
                            <div class='metric-title'>AUTONOMIA</div>
                            <div class='metric-value'>{est['autonomia']:.1f} s</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if reabastecimento:
                        # Métrica 7
                        st.markdown(f"""
                            <div class='metric-item'>
                                <div class='metric-title'>COMB. POR PARADA</div>
                                <div class='metric-value'>{est['combustivel_por_parada']:.2f} L</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Métrica 8
                        st.markdown(f"""
                            <div class='metric-item'>
                                <div class='metric-title'>TANQUE INICIAL</div>
                                <div class='metric-value'>{est['combustivel_inicial']:.2f} L</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)  # Fecha metric-grid
                    
                    # Barras de progresso para stints (se aplicável)
                    if reabastecimento and est['numero_de_stints'] > 1:
                        st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
                        st.markdown("<div class='metric-title'>DISTRIBUIÇÃO POR STINT</div>", unsafe_allow_html=True)
                        for j, c in enumerate(est['combustivel_por_stint']):
                            st.progress(
                                min(c / est['consumo_total'], 1.0), 
                                text=f"Stint {j+1}: {c:.2f} L ({c/est['consumo_total']*100:.1f}%)"
                            )
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)  # Fecha strategy-card
