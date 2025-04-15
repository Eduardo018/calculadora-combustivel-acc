import streamlit as st
import plotly.graph_objects as go

# Configuração de cores para melhor distinção visual
CORES_ESTRATEGIAS = {
    "Conservadora (2 voltas extras)": "#2ca02c",  # Verde
    "Recomendada (1.5 voltas extras)": "#1f77b4",  # Azul
    "Arriscada (0.5 volta extra)": "#d62728"  # Vermelho
}

PISTAS = {
    "Monza": 5793,
    "Brands Hatch": 3908,
    "Silverstone": 5891,
    "Paul Ricard": 5842,
    "Misano": 4226,
    "Zandvoort": 4252,
    "Spa-Francorchamps": 7004,
    "Nürburgring": 5137,
    "Hungaroring": 4381,
    "Barcelona": 4655,
    "Zolder": 4011,
    "Imola": 4959,
    "Oulton Park": 4037,
    "Snetterton": 4779,
    "Donington Park": 4020,
    "Mount Panorama": 6213,
    "Laguna Seca": 3602,
    "Suzuka": 5807,
    "Kyalami": 4522,
}

def tempo_em_segundos(minutos, segundos):
    return minutos * 60 + segundos

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
        combustivel_por_stint = consumo_total
        combustivel_por_parada = 0
    else:
        numero_de_stints = (duracao_corrida // stint_max) + (1 if duracao_corrida % stint_max else 0)
        combustivel_por_stint = consumo_total / numero_de_stints
        combustivel_por_parada = combustivel_por_stint / num_pitstops if num_pitstops else 0
        combustivel_inicial = combustivel_por_stint

    return {
        "voltas_estimada": int(voltas_estimada),
        "voltas_com_margem": int(voltas_com_margem),
        "consumo_total": consumo_total,
        "numero_de_stints": numero_de_stints,
        "combustivel_por_stint": combustivel_por_stint,
        "combustivel_por_parada": combustivel_por_parada,
        "combustivel_inicial": combustivel_inicial
    }

# Interface do usuário
st.set_page_config(layout="wide")
st.title("🔧 Calculadora de Estratégia de Combustível - ACC")

# Seção de seleção de parâmetros
with st.expander("🔧 Configurações da Corrida", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        pista_escolhida = st.selectbox("Selecione o circuito da corrida:", options=list(PISTAS.keys()))
        min_rapida = st.number_input("Minutos da volta mais rápida", min_value=0, max_value=10, value=1)
        seg_rapida = st.number_input("Segundos da volta mais rápida", min_value=0, max_value=59, value=50)
        
    with col2:
        st.markdown(f"**Comprimento da pista selecionada:** {PISTAS[pista_escolhida]} metros")
        min_lenta = st.number_input("Minutos da volta mais lenta", min_value=0, max_value=10, value=2)
        seg_lenta = st.number_input("Segundos da volta mais lenta", min_value=0, max_value=59, value=20)

    col3, col4 = st.columns([2, 1])
    with col3:
        consumo = st.number_input("Consumo médio por volta (litros)", min_value=0.1, step=0.1, value=3.25)
    with col4:
        margem_litros = st.number_input("Margem de segurança (litros)", min_value=0.0, step=0.1, value=0.0, 
                                      help="Valor adicional somado ao consumo médio por volta")

    consumo += margem_litros

    col5, col6, col7 = st.columns(3)
    with col5:
        duracao_corrida = st.number_input("Duração da corrida (minutos)", min_value=1, value=30)
    with col6:
        stint_max = st.number_input("Duração máxima de cada stint (minutos)", min_value=1, value=15)
    with col7:
        antec_box = st.number_input("Entrar no box com quantos minutos restantes do stint?", 
                                  min_value=0, max_value=stint_max-1, value=1)

    col8, col9 = st.columns(2)
    with col8:
        duracao_stint_piloto = st.number_input("Duração do stint de cada piloto (minutos)", min_value=1, value=15)
    with col9:
        num_pitstops = st.number_input("Número de pitstops obrigatórios", min_value=0, value=2)

    reabastecimento_input = st.radio("A corrida permite reabastecimento?", options=["Sim", "Não"], index=0, horizontal=True)
    reabastecimento = reabastecimento_input == "Sim"

# Botão de cálculo
if st.button("🎯 Calcular Estratégia", use_container_width=True):
    estrategias = {}
    for nome, margem in zip(["Conservadora (2 voltas extras)", "Recomendada (1.5 voltas extras)", "Arriscada (0.5 volta extra)"], [2, 1.5, 0.5]):
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

    # Exibição das estratégias lado a lado
    st.subheader("🏁 Estratégias Calculadas")
    cols = st.columns(3)
    
    for i, (nome, est) in enumerate(estrategias.items()):
        with cols[i]:
            st.markdown(
                f"<div style='background-color:{CORES_ESTRATEGIAS[nome]};padding:10px;border-radius:10px;text-align:center'>"
                f"<h3 style='color:white;margin:0;'>{nome}</h3>"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.metric("🔁 Voltas totais", f"{est['voltas_com_margem']}")
            st.metric("⛽ Combustível total", f"{est['consumo_total']:.2f} L")
            st.metric("🔄 Nº de stints", est['numero_de_stints'])
            if reabastecimento:
                st.metric("⛽ Por parada", f"{est['combustivel_por_parada']:.2f} L")
            st.metric("🏁 Tanque inicial", f"{est['combustivel_inicial']:.2f} L")

    # Gráfico de Barras Agrupadas com Linhas de Referência
    st.subheader("📊 Comparação Visual das Estratégias")
    
    fig = go.Figure()
    
    # Valores máximos para as linhas de referência
    max_combustivel = max(est['consumo_total'] for est in estrategias.values())
    max_tanque = max(est['combustivel_inicial'] for est in estrategias.values())
    
    # Adicionando barras para Combustível Total
    fig.add_trace(go.Bar(
        x=list(estrategias.keys()),
        y=[est['consumo_total'] for est in estrategias.values()],
        name='Combustível Total',
        marker_color=[CORES_ESTRATEGIAS[nome] for nome in estrategias.keys()],
        opacity=0.7,
        text=[f"{est['consumo_total']:.1f}L" for est in estrategias.values()],
        textposition='outside',
        hoverinfo='text',
        textfont=dict(size=12)
    ))
    
    # Adicionando barras para Tanque Inicial
    fig.add_trace(go.Bar(
        x=list(estrategias.keys()),
        y=[est['combustivel_inicial'] for est in estrategias.values()],
        name='Tanque Inicial',
        marker_color=[CORES_ESTRATEGIAS[nome] for nome in estrategias.keys()],
        opacity=0.9,
        text=[f"{est['combustivel_inicial']:.1f}L" for est in estrategias.values()],
        textposition='inside',
        hoverinfo='text',
        textfont=dict(color='white', size=12)
    ))
    
    # Adicionando linhas de referência horizontais
    for valor in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:  # Valores de referência em litros
        if valor < max(max_combustivel, max_tanque) * 1.1:  # Só mostra linhas até pouco acima do valor máximo
            fig.add_hline(y=valor, line_dash="dot",
                         line_color="gray", line_width=0.5,
                         annotation_text=f"{valor}L", 
                         annotation_position="right",
                         annotation_font_size=10,
                         annotation_font_color="gray")
    
    fig.update_layout(
        barmode='group',
        title=dict(
            text="<b>Comparação entre Estratégias</b>",
            x=0.5,
            font=dict(size=18)
        ),
        xaxis=dict(
            title='Estratégias',
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title='Litros de Combustível',
            gridcolor='rgba(200,200,200,0.2)',
            range=[0, max(max_combustivel, max_tanque) * 1.15]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        hovermode="x unified",
        height=500,
        margin=dict(t=100, r=40)  # Margem maior no topo para o título
    )
    
    st.plotly_chart(fig, use_container_width=True)