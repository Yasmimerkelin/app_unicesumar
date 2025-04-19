import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import os
from datetime import datetime


def add_logo(path):
    st.logo(image=path, icon_image=path)
    st.html("""
    <style>
        [alt=Logo] {
        height: 8rem;
        width: 8rem;
        display: block;
        margin-left: auto;
        margin-right: auto;
            
        }
    </style>
            """)


def apply_custom_styles():
    css_styles = """
    <style>
        h1 {
            margin-top: -3rem;
        }
    </style>
    """
    st.html(css_styles)


def customize_button_color():
    # Change color of st.button
    st.html("""
    <style>
            .row-widget.stButton > button {
            background-color: #c7141a;
            color: white;
            padding: -2.5rem -2rem;
            
        }
        .row-widget.stButton > button:hover {
            background-color: #493aa0;
            color: white;
        }
    </style>
    """)

# Configuração da página
st.set_page_config(
    page_title="Gestão de Alunos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar Logo e estilos
img_path = './assets/logo_uni_v2.jpg'
try:
    add_logo(img_path)
except:
    st.warning("Logo não encontrada. Verifique o caminho da imagem.")
apply_custom_styles()
customize_button_color()

# Título da página
st.title("📊 Gestão e Análise de Desempenho dos Alunos 📊")

# Função para conectar com a API do DeepSeek através do OpenRouter
def get_deepseek_response(prompt):
    try:
        # URL da API do OpenRouter
        API_URL = "https://openrouter.ai/api/v1/chat/completions"
        
        # Verificar se a chave da API está configurada
        if 'DEEPSEEK_API_KEY' in st.secrets:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
        else:
            # Se não estiver nas secrets, usar o valor padrão
            api_key = "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"
        
        # Configurar os headers para a requisição
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Preparar o payload para o modelo DeepSeek
        payload = {
            "model": "deepseek/deepseek-chat:free",
            "messages": [
                {"role": "system", "content": "Você é um assistente educacional especializado em análise de desempenho acadêmico."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Fazer a requisição para a API
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Verificar se a resposta foi bem-sucedida
        if response.status_code == 200:
            # Extrair o texto gerado
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"Erro na API do DeepSeek: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar com a API do DeepSeek: {e}")
        return None

# Função para calcular a média das notas
def calcular_media(row, colunas_notas):
    notas = [row[col] for col in colunas_notas if pd.notna(row[col])]
    if notas:
        return round(sum(notas) / len(notas), 2)
    return np.nan

# Função para determinar a situação do aluno
def determinar_situacao(media, nota_corte=6.0):
    if pd.isna(media):
        return "Sem notas"
    elif media >= nota_corte:
        return "Aprovado"
    elif media >= nota_corte - 2.0:  # Considerando recuperação para notas entre 4.0 e 6.0
        return "Recuperação"
    else:
        return "Reprovado"

# Função para gerar gráfico de desempenho individual
def gerar_grafico_individual(aluno_data, colunas_notas):
    # Preparar dados para o gráfico
    notas = [aluno_data[col] for col in colunas_notas if col in aluno_data]
    
    # Criar gráfico de radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=notas,
        theta=colunas_notas,
        fill='toself',
        name=aluno_data['Nome'],
        line=dict(color='#c7141a'),  # Cor da Unicesumar
        fillcolor='rgba(199, 20, 26, 0.2)'  # Versão transparente da cor
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]  # Assumindo notas de 0 a 10
            )
        ),
        showlegend=False,
        title=f"Desempenho de {aluno_data['Nome']}",
        height=400
    )
    
    return fig

# Função para gerar gráfico comparativo da turma
def gerar_grafico_turma(df, colunas_notas):
    # Calcular médias por avaliação
    medias = {col: df[col].mean() for col in colunas_notas}
    
    # Criar gráfico de barras
    fig = px.bar(
        x=list(medias.keys()),
        y=list(medias.values()),
        labels={'x': 'Avaliação', 'y': 'Média da Turma'},
        title='Médias da Turma por Avaliação',
        color_discrete_sequence=['#c7141a']  # Cor da Unicesumar
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    
    return fig

# Função para calcular estatísticas básicas
def calculate_stats(df, numeric_columns):
    stats = {}
    for col in numeric_columns:
        stats[col] = {
            'média': df[col].mean(),
            'mediana': df[col].median(),
            'mínimo': df[col].min(),
            'máximo': df[col].max(),
            'desvio padrão': df[col].std()
        }
    return stats

# Função para gerar gráficos interativos com Plotly
def generate_charts(df, numeric_columns):
    # Inicializar todas as variáveis que serão retornadas
    histograms = []
    boxplots = []
    violin_plots = []
    fig_corr = None
    fig_radar = None
    fig_trend = None
    fig_comparison = None
    fig_gauge = None
    
    # Verificar se o DataFrame está vazio
    if df.empty:
        st.warning("Não há dados para gerar gráficos.")
        # Retornar todos os gráficos gerados
        return histograms, fig_corr, boxplots, fig_radar, fig_trend, fig_comparison, fig_gauge, violin_plots
    
    # Verificar se as colunas numéricas existem no DataFrame
    valid_columns = [col for col in numeric_columns if col in df.columns]
    if not valid_columns:
        st.warning("Nenhuma coluna numérica válida encontrada para gerar gráficos.")
        # Retornar todos os gráficos gerados
        return histograms, fig_corr, boxplots, fig_radar, fig_trend, fig_comparison, fig_gauge, violin_plots
    
    # Criar histogramas interativos para cada coluna numérica
    histograms = []
    boxplots = []
    violin_plots = []
    for col in valid_columns:
        # Verificar se a coluna contém dados numéricos válidos
        if df[col].count() == 0 or not pd.api.types.is_numeric_dtype(df[col]):
            st.warning(f"A coluna '{col}' não contém dados numéricos válidos para gerar visualizações.")
            continue
        
        try:
            # Verificar se há valores válidos suficientes para criar visualizações
            valid_data = df[col].dropna()
            if len(valid_data) < 2:
                st.warning(f"A coluna '{col}' não possui dados suficientes para gerar visualizações (mínimo de 2 valores necessários).")
                continue
                
            # Histograma com curva de densidade (sem marginal kde para evitar erros)
            try:
                fig_hist = px.histogram(
                    df, x=col,
                    title=f'Distribuição de {col}',
                    labels={col: col, 'count': 'Frequência'},
                    opacity=0.7,
                    color_discrete_sequence=['#c7141a']  # Cor da Unicesumar
                    # Removido marginal='kde' para evitar erros
                )
                fig_hist.update_layout(
                    template='plotly_white',
                    hoverlabel=dict(bgcolor="white", font_size=12),
                    height=400
                )
                histograms.append(fig_hist)
            except Exception as e:
                st.warning(f"Erro ao gerar histograma para '{col}': {e}")
            
            # Boxplot para visualizar a distribuição
            try:
                fig_box = px.box(
                    df, y=col,
                    title=f'Boxplot de {col}',
                    labels={col: 'Valor'},
                    color_discrete_sequence=['#c7141a'],  # Cor da Unicesumar
                    points="all"  # Mostra todos os pontos
                )
                fig_box.update_layout(
                    template='plotly_white',
                    hoverlabel=dict(bgcolor="white", font_size=12),
                    height=400
                )
                boxplots.append(fig_box)
            except Exception as e:
                st.warning(f"Erro ao gerar boxplot para '{col}': {e}")
            
            # Gráfico de violino para distribuição detalhada
            try:
                fig_violin = px.violin(
                    df, y=col,
                    title=f'Distribuição Detalhada de {col}',
                    labels={col: 'Valor'},
                    color_discrete_sequence=['#c7141a'],  # Cor da Unicesumar
                    box=True,  # Mostra boxplot dentro do violino
                    points="all"  # Mostra todos os pontos
                )
                fig_violin.update_layout(
                    template='plotly_white',
                    hoverlabel=dict(bgcolor="white", font_size=12),
                    height=400
                )
                violin_plots.append(fig_violin)
            except Exception as e:
                st.warning(f"Erro ao gerar gráfico de violino para '{col}': {e}")
        except Exception as e:
            st.warning(f"Erro ao gerar visualizações para '{col}': {e}")
    
    # Verificar se foi possível criar algum histograma
    if not histograms:
        st.warning("Não foi possível gerar nenhuma visualização com os dados fornecidos.")
        # Retornar todos os gráficos gerados
        return histograms, fig_corr, boxplots, fig_radar, fig_trend, fig_comparison, fig_gauge, violin_plots
    
    # Criar gráfico de correlação se houver mais de uma coluna numérica válida
    fig_corr = None
    if len(valid_columns) > 1:
        try:
            # Verificar se há dados suficientes para calcular correlação
            numeric_data = df[valid_columns].select_dtypes(include=[np.number])
            if numeric_data.empty or numeric_data.dropna().empty:
                st.warning("Dados insuficientes para calcular a matriz de correlação.")
            else:
                # Calcular matriz de correlação apenas com colunas numéricas válidas
                # Usar método pearson que é mais robusto para pequenos conjuntos de dados
                corr_matrix = numeric_data.corr(method='pearson', min_periods=2)
                
                # Verificar se a matriz de correlação foi calculada corretamente
                if corr_matrix.isnull().all().all():
                    st.warning("Não foi possível calcular correlações válidas entre as colunas.")
                else:
                    # Criar visualização da matriz de correlação
                    fig_corr = px.imshow(
                        corr_matrix,
                        text_auto=True,
                        color_continuous_scale='RdBu_r',
                        title='Matriz de Correlação',
                        labels=dict(color='Correlação')
                    )
                    fig_corr.update_layout(
                        template='plotly_white',
                        height=500,
                        width=600
                    )
        except Exception as e:
            st.warning(f"Erro ao gerar matriz de correlação: {e}")
            fig_corr = None
    
    # Criar gráfico de radar para comparar desempenho entre alunos
    fig_radar = None
    if len(valid_columns) > 1 and 'Nome' in df.columns:
        try:
            # Verificar se há dados suficientes
            if df['Nome'].count() == 0:
                st.warning("Não há nomes de alunos válidos para gerar o gráfico de radar.")
            else:
                # Filtrar apenas linhas com dados completos para as colunas numéricas
                complete_data = df.dropna(subset=valid_columns)
                
                if len(complete_data) == 0:
                    st.warning("Não há dados completos suficientes para gerar o gráfico de radar.")
                else:
                    # Selecionar até 5 alunos para o gráfico de radar (para não ficar poluído)
                    sample_size = min(5, len(complete_data))
                    sample_df = complete_data.sample(n=sample_size) if len(complete_data) > sample_size else complete_data
                    
                    # Criar figura com tratamento de erro
                    try:
                        fig_radar = go.Figure()
                        
                        for i, row in sample_df.iterrows():
                            # Verificar se todos os valores são numéricos
                            values = []
                            for col in valid_columns:
                                try:
                                    val = float(row[col])
                                    values.append(val)
                                except (ValueError, TypeError):
                                    values.append(0)  # Usar 0 como valor padrão para dados inválidos
                            
                            # Adicionar traço apenas se houver valores válidos
                            if any(v > 0 for v in values):
                                fig_radar.add_trace(go.Scatterpolar(
                                    r=values,
                                    theta=valid_columns,
                                    fill='toself',
                                    name=str(row['Nome'])  # Converter para string para evitar erros
                                ))
                        
                        # Verificar se algum traço foi adicionado
                        if len(fig_radar.data) > 0:
                            fig_radar.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, 10]  # Assumindo notas de 0 a 10
                                    )
                                ),
                                title="Comparação de Desempenho entre Alunos",
                                height=500
                            )
                        else:
                            st.warning("Não foi possível criar o gráfico de radar com os dados disponíveis.")
                            fig_radar = None
                    except Exception as e:
                        st.warning(f"Erro ao criar gráfico de radar: {e}")
                        fig_radar = None
        except Exception as e:
            st.warning(f"Erro ao processar dados para gráfico de radar: {e}")
            fig_radar = None
    
    # Criar gráfico de tendência se houver mais de uma coluna numérica
    fig_trend = None
    if len(valid_columns) > 1:
        try:
            # Calcular médias da turma para cada avaliação
            means = {col: df[col].mean() for col in valid_columns}
            trend_df = pd.DataFrame({
                'Avaliação': list(means.keys()),
                'Média': list(means.values())
            })
            
            fig_trend = px.line(
                trend_df, x='Avaliação', y='Média',
                title='Tendência de Desempenho da Turma',
                markers=True,
                line_shape='spline',  # Linha suavizada
                color_discrete_sequence=['#c7141a']  # Cor da Unicesumar
            )
            
            fig_trend.update_layout(
                template='plotly_white',
                height=400,
                xaxis_title="Avaliação",
                yaxis_title="Média da Turma",
                yaxis=dict(range=[0, 10])  # Assumindo notas de 0 a 10
            )
        except Exception as e:
            st.warning(f"Erro ao gerar gráfico de tendência: {e}")
    
    # Criar gráfico de comparação entre avaliações (boxplot múltiplo)
    fig_comparison = None
    if len(valid_columns) > 1:
        try:
            # Preparar dados para o boxplot múltiplo
            comparison_data = pd.melt(df, id_vars=['Nome'] if 'Nome' in df.columns else None, 
                                     value_vars=valid_columns, 
                                     var_name='Avaliação', value_name='Nota')
            
            fig_comparison = px.box(
                comparison_data, x='Avaliação', y='Nota',
                title='Comparação entre Avaliações',
                color='Avaliação',
                notched=True,  # Adiciona entalhe para intervalo de confiança
                points="all"  # Mostra todos os pontos
            )
            
            fig_comparison.update_layout(
                template='plotly_white',
                height=500,
                xaxis_title="Avaliação",
                yaxis_title="Nota",
                yaxis=dict(range=[0, 10]),  # Assumindo notas de 0 a 10
                showlegend=False
            )
        except Exception as e:
            st.warning(f"Erro ao gerar gráfico de comparação entre avaliações: {e}")
    
    # Criar gráfico de desempenho geral da turma (gauge chart)
    fig_gauge = None
    if 'Média' in df.columns:
        try:
            # Verificar se há valores válidos na coluna Média
            valid_media = df['Média'].dropna()
            if len(valid_media) == 0:
                st.warning("Não há valores válidos na coluna 'Média' para gerar o gráfico de desempenho geral.")
            else:
                # Calcular média geral da turma
                media_geral = valid_media.mean()
                
                # Criar gauge chart com tratamento de erro
                try:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=media_geral,
                        title={'text': "Média Geral da Turma"},
                        gauge={
                            'axis': {'range': [0, 10], 'tickwidth': 1},
                            'bar': {'color': "#c7141a"},
                            'steps': [
                                {'range': [0, 4], 'color': "#ff6961"},  # Vermelho claro
                                {'range': [4, 6], 'color': "#fdfd96"},  # Amarelo
                                {'range': [6, 10], 'color': "#77dd77"}   # Verde
                            ],
                            'threshold': {
                                'line': {'color': "#493aa0", 'width': 4},
                                'thickness': 0.75,
                                'value': 6  # Nota de corte
                            }
                        }
                    ))
                    
                    fig_gauge.update_layout(
                        height=300,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                except Exception as e:
                    st.warning(f"Erro ao criar gráfico de desempenho geral: {e}")
                    fig_gauge = None
        except Exception as e:
            st.warning(f"Erro ao processar dados para gráfico de desempenho geral: {e}")
            fig_gauge = None
    
    # Retornar todos os gráficos gerados
    return histograms, fig_corr, boxplots, fig_radar, fig_trend, fig_comparison, fig_gauge, violin_plots

# Função para analisar o desempenho individual
def analyze_student_performance(student_data, class_avg):
    analysis = {}
    
    # Comparar com a média da turma
    for col in student_data.index:
        if col.startswith('Nota'):
            student_score = student_data[col]
            avg_score = class_avg[col]
            
            if student_score > avg_score:
                performance = "acima da média"
            elif student_score < avg_score:
                performance = "abaixo da média"
            else:
                performance = "na média"
                
            analysis[col] = {
                'valor': student_score,
                'média_turma': avg_score,
                'desempenho': performance,
                'diferença': student_score - avg_score
            }
    
    return analysis

# Modal para inserir observações
@st.dialog("Inserir Observações do Aluno")
def obs_modal(student_name):
    st.write(f"Adicione observações sobre o aluno {student_name} para enriquecer a análise com IA.")
    obs = st.text_area("Observações (comportamento em sala, participação, dificuldades específicas, etc.):", height=200)
    if st.button("Salvar"):
        # Armazenar a observação no session state
        if 'student_observations' not in st.session_state:
            st.session_state['student_observations'] = {}
        
        st.session_state['student_observations'][student_name] = obs
        st.rerun()

# Função para gerar prompt para a IA
def generate_ai_prompt(student_name, performance_data, class_stats):
    prompt = f"Análise de desempenho para o aluno {student_name}:\n\n"
    
    # Adicionar dados de desempenho
    prompt += "Desempenho nas avaliações:\n"
    for assessment, data in performance_data.items():
        prompt += f"- {assessment}: {data['valor']:.2f} ({data['desempenho']}, {data['diferença']:.2f} pontos em relação à média da turma}})\n"
    
    # Adicionar estatísticas da turma
    prompt += "\nEstatísticas da turma:\n"
    for assessment, stats in class_stats.items():
        if assessment.startswith('Nota'):
            prompt += f"- {assessment}: Média = {stats['média']:.2f}, Mínimo = {stats['mínimo']:.2f}, Máximo = {stats['máximo']:.2f}\n"
    
    # Adicionar observações do professor, se existirem
    if 'student_observations' in st.session_state and student_name in st.session_state['student_observations']:
        observation = st.session_state['student_observations'][student_name]
        if observation.strip():
            prompt += "\nObservações do professor sobre o aluno:\n"
            prompt += f"{observation}\n"
    
    # Solicitar análise específica
    prompt += "\nCom base nesses dados, por favor forneça:\n"
    prompt += "1. Uma análise detalhada do desempenho deste aluno\n"
    prompt += "2. Identificação dos pontos fortes e fracos\n"
    prompt += "3. Recomendações específicas para melhorar o desempenho\n"
    prompt += "4. Sugestões de recursos e materiais de estudo personalizados\n"
    prompt += "5. Estratégias de aprendizado que podem beneficiar este aluno\n"
    
    return prompt

# Sidebar com opções
with st.sidebar:
    st.header("Opções")
    nota_corte = st.slider("Nota mínima para aprovação", 0.0, 10.0, 6.0, 0.1)
    st.divider()
    
    # Informações sobre o sistema
    st.subheader("Sobre o Sistema")
    st.markdown("""
    Este módulo permite gerenciar e analisar o desempenho dos alunos.
    
    **Funcionalidades:**
    - Importação de dados de alunos
    - Cálculo automático de médias
    - Determinação da situação acadêmica
    - Visualização de desempenho individual
    - Análise comparativa da turma
    - Análise com IA
    - Exportação de relatórios
    """)

# Criar abas para as diferentes funcionalidades
tab1, tab2, tab3 = st.tabs(["Gestão de Alunos", "Análise de Desempenho", "Análise com IA"])

# Tab 1: Gestão de Alunos (baseado em 2_Alunos.py)
with tab1:
    st.write("Carregue a planilha com os dados dos alunos ou adicione manualmente")
    
    # Subtabs para diferentes modos de entrada
    subtab1, subtab2 = st.tabs(["Importar Dados", "Adicionar Manualmente"])
    
    # Subtab para importar dados
    with subtab1:
        uploaded_file = st.file_uploader("Escolha um arquivo CSV ou Excel", type=["csv", "xlsx"], key="upload_tab1")
        
        if uploaded_file is not None:
            try:
                # Determinar o tipo de arquivo e carregar
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Verificar e processar os dados
                if 'Nome' not in df.columns:
                    st.warning("O arquivo deve conter uma coluna 'Nome' para identificar os alunos.")
                else:
                    # Identificar colunas numéricas (possíveis notas)
                    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                    
                    # Permitir ao usuário selecionar quais colunas são notas
                    st.subheader("Selecione as colunas que representam notas")
                    colunas_notas = st.multiselect("Colunas de notas", numeric_columns, default=numeric_columns, key="notas_tab1")
                    
                    if colunas_notas:
                        # Calcular médias e situação
                        if 'Média' not in df.columns:
                            df['Média'] = df.apply(lambda row: calcular_media(row, colunas_notas), axis=1)
                        
                        if 'Situação' not in df.columns:
                            df['Situação'] = df['Média'].apply(lambda x: determinar_situacao(x, nota_corte))
                        
                        # Salvar no session state para uso em outras partes do app
                        st.session_state['alunos_df'] = df
                        st.session_state['colunas_notas'] = colunas_notas
                        
                        # Exibir os dados processados
                        st.subheader("Dados dos Alunos")
                        st.dataframe(
                            df,
                            column_config={
                                "Média": st.column_config.NumberColumn(
                                    "Média",
                                    format="%.2f",
                                    help="Média das notas"
                                ),
                                "Situação": st.column_config.TextColumn(
                                    "Situação",
                                    help="Situação acadêmica do aluno"
                                )
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                        
                        # Estatísticas da turma
                        st.subheader("Estatísticas da Turma")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Média Geral", f"{df['Média'].mean():.2f}")
                        col2.metric("Aprovados", len(df[df['Situação'] == 'Aprovado']))
                        col3.metric("Reprovados", len(df[df['Situação'] == 'Reprovado']))
                        
                        # Gráficos
                        st.subheader("Visualização dos Dados")
                        
                        # Gráfico comparativo da turma
                        grafico_turma = gerar_grafico_turma(df, colunas_notas)
                        st.plotly_chart(grafico_turma, use_container_width=True)
                        
                        # Seleção de aluno para visualização individual
                        st.subheader("Desempenho Individual")
                        aluno_selecionado = st.selectbox("Selecione um aluno", df['Nome'].tolist(), key="aluno_tab1")
                        
                        if aluno_selecionado:
                            aluno_data = df[df['Nome'] == aluno_selecionado].iloc[0]
                            
                            # Exibir informações do aluno
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.info(f"**Aluno:** {aluno_data['Nome']}")
                                st.info(f"**Média:** {aluno_data['Média']:.2f}")
                                
                                # Colorir a situação de acordo com o resultado
                                if aluno_data['Situação'] == 'Aprovado':
                                    st.success(f"**Situação:** {aluno_data['Situação']}")
                                elif aluno_data['Situação'] == 'Reprovado':
                                    st.error(f"**Situação:** {aluno_data['Situação']}")
                                elif aluno_data['Situação'] == 'Recuperação':
                                    st.warning(f"**Situação:** {aluno_data['Situação']}")
                                else:
                                    st.warning(f"**Situação:** {aluno_data['Situação']}")
                            
                            with col2:
                                # Gráfico individual
                                grafico_individual = gerar_grafico_individual(aluno_data, colunas_notas)
                                st.plotly_chart(grafico_individual, use_container_width=True)
                        
                        # Opção para exportar relatório
                        if st.button("Exportar Relatório", key="export_tab1"):
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Baixar Relatório CSV",
                                data=csv,
                                file_name=f"relatorio_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")
    
    # Subtab para adicionar manualmente
    with subtab2:
        st.subheader("Adicionar Novo Aluno")
        
        # Formulário para adicionar aluno
        with st.form("form_novo_aluno"):
            nome = st.text_input("Nome do Aluno")
            
            # Campos para notas
            col1, col2, col3 = st.columns(3)
            nota1 = col1.number_input("Nota 1", 0.0, 10.0, step=0.1)
            nota2 = col2.number_input("Nota 2", 0.0, 10.0, step=0.1)
            nota3 = col3.number_input("Nota 3", 0.0, 10.0, step=0.1)
            
            # Botão para adicionar
            submitted = st.form_submit_button("Adicionar Aluno")
            
            if submitted:
                if nome:
                    # Calcular média
                    media = round((nota1 + nota2 + nota3) / 3, 2)
                    situacao = determinar_situacao(media, nota_corte)
                    
                    # Criar ou atualizar DataFrame
                    novo_aluno = pd.DataFrame({
                        "Nome": [nome],
                        "Nota 1": [nota1],
                        "Nota 2": [nota2],
                        "Nota 3": [nota3],
                        "Média": [media],
                        "Situação": [situacao]
                    })
                    
                    if 'alunos_df' not in st.session_state:
                        st.session_state['alunos_df'] = novo_aluno
                        st.session_state['colunas_notas'] = ["Nota 1", "Nota 2", "Nota 3"]
                    else:
                        st.session_state['alunos_df'] = pd.concat([st.session_state['alunos_df'], novo_aluno], ignore_index=True)
                    
                    st.success(f"Aluno {nome} adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, informe o nome do aluno.")
        
        # Exibir dados se existirem
        if 'alunos_df' in st.session_state:
            st.subheader("Alunos Cadastrados")
            st.dataframe(
                st.session_state['alunos_df'],
                column_config={
                    "Média": st.column_config.NumberColumn(
                        "Média",
                        format="%.2f"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Opção para limpar dados
            if st.button("Limpar Todos os Dados", key="clear_tab1"):
                del st.session_state['alunos_df']
                st.rerun()

# Tab 2: Análise de Desempenho (baseado em 3_Analise_Desempenho.py)
with tab2:
    st.write("Carregue a planilha com os dados dos alunos para análise ou use os dados já carregados")
    
    # Verificar se já existem dados carregados
    if 'alunos_df' in st.session_state:
        st.success("Usando dados já carregados na aba 'Gestão de Alunos'")
        df = st.session_state['alunos_df']
        colunas_notas = st.session_state['colunas_notas']
        
        # Exibir os dados carregados
        st.subheader("Dados Carregados")
        st.dataframe(df, use_container_width=True)
        
        # Calcular estatísticas
        stats = calculate_stats(df, colunas_notas)
        
        # Exibir estatísticas gerais
        st.subheader("Estatísticas Gerais da Turma")
        stats_df = pd.DataFrame({col: {k: f"{v:.2f}" if isinstance(v, float) else v for k, v in col_stats.items()} 
                                for col, col_stats in stats.items()})
        st.dataframe(stats_df)
        
        # Exibir métricas gerais da turma
        st.subheader("Métricas Gerais da Turma")
        col1, col2, col3, col4 = st.columns(4)
        
        # Calcular métricas
        media_geral = df['Média'].mean()
        taxa_aprovacao = len(df[df['Situação'] == 'Aprovado']) / len(df) * 100 if len(df) > 0 else 0
        taxa_recuperacao = len(df[df['Situação'] == 'Recuperação']) / len(df) * 100 if len(df) > 0 else 0
        taxa_reprovacao = len(df[df['Situação'] == 'Reprovado']) / len(df) * 100 if len(df) > 0 else 0
        
        # Exibir métricas com cores apropriadas
        col1.metric("Média Geral", f"{media_geral:.2f}")
        col2.metric("Taxa de Aprovação", f"{taxa_aprovacao:.1f}%", delta=f"{taxa_aprovacao-60:.1f}%" if taxa_aprovacao != 60 else None)
        col3.metric("Taxa de Recuperação", f"{taxa_recuperacao:.1f}%")
        col4.metric("Taxa de Reprovação", f"{taxa_reprovacao:.1f}%", delta=f"{-taxa_reprovacao:.1f}%", delta_color="inverse")
        
        # Gerar e exibir gráficos interativos
        st.subheader("Visualização dos Dados")
        histograms, fig_corr, boxplots, fig_radar, fig_trend, fig_comparison, fig_gauge, violin_plots = generate_charts(df, colunas_notas)
        
        # Exibir gauge chart de desempenho geral
        if fig_gauge:
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Criar abas para diferentes tipos de visualizações
        viz_tabs = st.tabs(["Distribuição", "Distribuição Detalhada", "Comparação Entre Avaliações", "Correlação", "Comparação Entre Alunos", "Tendências"])
        
        # Aba de Distribuição (Histogramas)
        with viz_tabs[0]:
            st.info("📊 Os histogramas mostram a distribuição das notas em cada avaliação, permitindo identificar padrões e concentrações de valores.")
            if histograms:  # Verificar se a lista de histogramas não está vazia
                cols = st.columns(min(2, len(histograms)))
                for i, fig_hist in enumerate(histograms):
                    with cols[i % len(cols)]:
                        st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.warning("Não foi possível gerar histogramas com os dados fornecidos.")
        
        # Aba de Distribuição Detalhada (Violin plots)
        with viz_tabs[1]:
            st.info("🎻 Os gráficos de violino mostram a distribuição detalhada das notas, combinando boxplot com densidade, revelando a forma completa da distribuição.")
            if violin_plots:  # Verificar se a lista de violin plots não está vazia
                cols = st.columns(min(2, len(violin_plots)))
                for i, fig_violin in enumerate(violin_plots):
                    with cols[i % len(cols)]:
                        st.plotly_chart(fig_violin, use_container_width=True)
            else:
                st.warning("Não foi possível gerar gráficos de violino com os dados fornecidos.")
        
        # Aba de Comparação Entre Avaliações
        with viz_tabs[2]:
            st.info("📏 Este gráfico permite comparar diretamente a distribuição das notas entre diferentes avaliações, facilitando a identificação de avaliações mais difíceis ou mais fáceis.")
            if fig_comparison:
                st.plotly_chart(fig_comparison, use_container_width=True)
            else:
                st.warning("Não foi possível gerar o gráfico de comparação entre avaliações.")
        
        # Aba de Correlação
        with viz_tabs[3]:
            st.info("🔄 A matriz de correlação mostra a relação entre as diferentes avaliações. Valores próximos a 1 indicam forte correlação positiva.")
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Adicionar explicação sobre correlação
                st.markdown("""**Interpretação da Correlação:**
                - **Correlação próxima de 1**: Forte relação positiva (alunos com boas notas em uma avaliação tendem a ter boas notas na outra)
                - **Correlação próxima de 0**: Pouca ou nenhuma relação
                - **Correlação próxima de -1**: Forte relação negativa (alunos com boas notas em uma avaliação tendem a ter notas baixas na outra)
                """)
            else:
                st.warning("Não foi possível gerar a matriz de correlação com os dados fornecidos.")
        
        # Aba de Comparação Entre Alunos (Radar)
        with viz_tabs[4]:
            st.info("📡 O gráfico de radar permite comparar o desempenho de diferentes alunos em todas as avaliações simultaneamente, identificando padrões de força e fraqueza.")
            if fig_radar:
                st.plotly_chart(fig_radar, use_container_width=True)
                st.caption("Nota: Apenas uma amostra de alunos é exibida para melhor visualização.")
            else:
                st.warning("Não foi possível gerar o gráfico de radar com os dados fornecidos.")
        
        # Aba de Tendências
        with viz_tabs[5]:
            st.info("📈 O gráfico de tendência mostra a evolução das médias da turma ao longo das diferentes avaliações, permitindo identificar progressos ou dificuldades.")
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Adicionar análise de tendência
                if len(colunas_notas) > 1:
                    # Calcular médias da turma para cada avaliação
                    means = {col: df[col].mean() for col in colunas_notas}
                    means_list = list(means.values())
                    
                    # Verificar tendência
                    if means_list[-1] > means_list[0]:
                        st.success("📈 **Tendência Positiva**: A turma está apresentando melhoria no desempenho ao longo das avaliações.")
                    elif means_list[-1] < means_list[0]:
                        st.error("📉 **Tendência Negativa**: A turma está apresentando queda no desempenho ao longo das avaliações.")
                    else:
                        st.info("📊 **Desempenho Estável**: A turma está mantendo um desempenho constante ao longo das avaliações.")
            else:
                st.warning("Não foi possível gerar o gráfico de tendência com os dados fornecidos.")
        
        # Análise individual por aluno
        st.subheader("Análise Individual")
        selected_student = st.selectbox("Selecione um aluno para análise detalhada", df['Nome'].tolist(), key="aluno_tab2")
        
        if selected_student:
            # Obter dados do aluno selecionado
            student_data = df[df['Nome'] == selected_student].iloc[0]
            
            # Calcular médias da turma
            class_avg = df[colunas_notas + ['Média']].mean()
            
            # Analisar desempenho individual
            performance_analysis = analyze_student_performance(student_data, class_avg)
            
            # Exibir análise básica
            st.write(f"### Análise de {selected_student}")
            
            # Criar colunas para métricas
            cols = st.columns(len(performance_analysis))
            
            for i, (assessment, data) in enumerate(performance_analysis.items()):
                with cols[i]:
                    delta = data['diferença']
                    st.metric(
                        label=assessment,
                        value=f"{data['valor']:.2f}",
                        delta=f"{delta:.2f}",
                        delta_color="normal" if delta >= 0 else "inverse"
                    )
            
            # Adicionar média geral
            st.metric(
                label="Média Geral",
                value=f"{student_data['Média']:.2f}",
                delta=f"{student_data['Média'] - class_avg['Média']:.2f}",
                delta_color="normal" if student_data['Média'] >= class_avg['Média'] else "inverse"
            )
            
            with tab3:
                st.subheader("Análise com Inteligência Artificial")

                # Selecionar aluno
                selected_student = st.selectbox("Selecione um aluno para análise detalhada", df['Nome'].tolist(), key="aluno_tab3")

                # Botões para adicionar observações e gerar análise
                col1, col2 = st.columns(2)
                if col1.button("📝 Adicionar Observações", key="btn_obs"):
                    obs_modal(selected_student)
                    
                # Exibir observações existentes, se houver
                if 'student_observations' in st.session_state and selected_student in st.session_state['student_observations']:
                    observation = st.session_state['student_observations'][selected_student]
                    if observation.strip():
                        with st.expander("📋 Observações Adicionadas", expanded=True):
                            st.info(observation)
                
                # Botão para gerar análise
                if col2.button("🧠 Gerar Análise Detalhada com IA", key="btn_ia"):
                    with st.spinner("Gerando análise com IA..."):
                        # Gerar prompt para a IA
                        prompt = generate_ai_prompt(selected_student, performance_analysis, stats)
                        
                        # Obter análise da IA
                        ai_analysis = get_deepseek_response(prompt)
                        
                        if ai_analysis:
                            # Armazenar a análise no session state para persistência
                            if 'ai_analyses' not in st.session_state:
                                st.session_state['ai_analyses'] = {}
                            
                            st.session_state['ai_analyses'][selected_student] = ai_analysis
                            
                            # Exibir a análise formatada
                            st.markdown(ai_analysis)
                            
                            # Salvar a análise
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"analise_{selected_student.replace(' ', '_')}_{timestamp}.txt"
                            
                            # Botão para download
                            st.download_button(
                                label="Baixar Análise",
                                data=f"Análise de {selected_student} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n{ai_analysis}",
                                file_name=filename,
                                mime="text/plain"
                            )
                        else:
                            st.error("Não foi possível gerar a análise. Verifique a chave da API.")
                
                # Exibir análise salva anteriormente, se existir
                elif 'ai_analyses' in st.session_state and selected_student in st.session_state['ai_analyses']:
                    st.info("Análise gerada anteriormente:")
                    st.markdown(st.session_state['ai_analyses'][selected_student])
                    
                    # Botão para download da análise salva
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"analise_{selected_student.replace(' ', '_')}_{timestamp}.txt"
                    
                    st.download_button(
                        label="Baixar Análise",
                        data=f"Análise de {selected_student} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n{st.session_state['ai_analyses'][selected_student]}",
                        file_name=filename,
                        mime="text/plain"
                    )
        else:
            st.info("Carregue os dados dos alunos na aba 'Gestão de Alunos' primeiro.")
            
            # Exemplo de formato esperado
            st.subheader("Exemplo de análise com IA")
            st.markdown("""
            A análise com IA fornece insights detalhados sobre o desempenho do aluno, incluindo:
            
            1. **Análise detalhada do desempenho**
            2. **Identificação de pontos fortes e fracos**
            3. **Recomendações específicas para melhorar**
            4. **Sugestões de recursos e materiais de estudo**
            5. **Estratégias de aprendizado personalizadas**
            
            Carregue os dados dos alunos para experimentar esta funcionalidade.
            """)