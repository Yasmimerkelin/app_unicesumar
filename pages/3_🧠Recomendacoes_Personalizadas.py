import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
from utils import add_logo, apply_custom_styles, customize_button_color

# Configuração da página
st.set_page_config(
    page_title="Recomendações Personalizadas",
    page_icon="🧠",
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
st.title("🧠 Recomendações Personalizadas de Estudo 🧠")

# Texto explicativo
st.markdown("""
    Esta ferramenta utiliza o modelo de linguagem DeepSeek para gerar recomendações personalizadas 
    de estudo com base no desempenho do aluno e no conteúdo programático da disciplina.
    
    Carregue a planilha com as notas dos alunos e forneça informações sobre o conteúdo 
    da disciplina para obter recomendações detalhadas.
""")

# Função para conectar com a API do DeepSeek através do OpenRouter
def get_deepseek_recommendations(prompt):
    try:
        # URL da API do OpenRouter
        API_URL = "https://openrouter.ai/api/v1/chat/completions"
        
        # Verificar se a chave da API está configurada
        if 'DEEPSEEK_API_KEY' in st.secrets:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
        else:
            # Se não estiver nas secrets, usar o valor padrão
            api_key = "sua-chave-API"
        
        # Configurar os headers para a requisição
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Preparar o payload para o modelo DeepSeek
        payload = {
            "model": "deepseek/deepseek-chat:free",
            "messages": [
                {"role": "system", "content": "Você é um assistente educacional especializado em criar planos de estudo personalizados."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
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

# Função para conectar com a API do DeepSeek para assistente em português
def get_deepseek_assistant_response(prompt):
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
                {"role": "system", "content": "Você é um assistente educacional especializado em criar conteúdo didático em português. Responda sempre em português do Brasil."},
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

# Função para identificar áreas de dificuldade
def identify_weak_areas(student_data, selected_columns):
    weak_areas = []
    for col in selected_columns:
        if student_data[col] < 6.0:  # Considerando nota mínima de aprovação como 6.0
            weak_areas.append(col)
    return weak_areas

# Função para gerar prompt para a IA
def generate_recommendation_prompt(student_name, student_data, weak_areas, course_content, learning_style):
    prompt = f"Recomendações de estudo personalizadas para o aluno {student_name}:\n\n"
    
    # Adicionar dados de desempenho
    prompt += "Desempenho nas avaliações:\n"
    for col in student_data.index:
        if col.startswith('Nota'):
            prompt += f"- {col}: {student_data[col]:.2f}\n"
    
    # Adicionar áreas de dificuldade
    if weak_areas:
        prompt += "\nÁreas que precisam de atenção especial:\n"
        for area in weak_areas:
            prompt += f"- {area}\n"
    
    # Adicionar conteúdo programático
    prompt += "\nConteúdo programático da disciplina:\n"
    prompt += course_content
    
    # Adicionar estilo de aprendizagem
    prompt += f"\nEstilo de aprendizagem preferido do aluno: {learning_style}\n"
    
    # Solicitar recomendações específicas
    prompt += "\nCom base nesses dados, por favor forneça:\n"
    prompt += "1. Um plano de estudos personalizado para as próximas 2 semanas\n"
    prompt += "2. Recomendações de materiais de estudo específicos (livros, artigos, vídeos, etc.)\n"
    prompt += "3. Exercícios práticos focados nas áreas de dificuldade\n"
    prompt += "4. Estratégias de aprendizado que se adequem ao estilo de aprendizagem do aluno\n"
    prompt += "5. Sugestões de como monitorar o progresso e avaliar a eficácia do plano de estudos\n"
    
    return prompt

# Função para gerar prompt para comentário geral de desempenho
def generate_performance_comment_prompt(student_name, student_data, selected_columns):
    prompt = f"Análise de desempenho para o aluno {student_name}:\n\n"
    
    # Adicionar dados de desempenho
    prompt += "Desempenho nas avaliações:\n"
    for col in student_data.index:
        if col.startswith('Nota'):
            prompt += f"- {col}: {student_data[col]:.2f}\n"
    
    # Calcular média geral
    notas = []
    for col in selected_columns:
        notas.append(student_data[col])
    
    media_geral = sum(notas) / len(notas) if notas else 0
    prompt += f"\nMédia geral: {media_geral:.2f}\n"
    
    # Solicitar análise específica
    prompt += "\nCom base nesses dados, por favor forneça:\n"
    prompt += "1. Uma análise geral do desempenho deste aluno\n"
    prompt += "2. Identificação dos pontos fortes e fracos\n"
    prompt += "3. Recomendações específicas para melhorar o desempenho\n"
    prompt += "4. Sugestões de estratégias de estudo que podem beneficiar este aluno\n"
    prompt += "5. Uma avaliação do progresso atual e potencial futuro\n"
    
    return prompt

# Interface principal

# Sidebar para informações da disciplina
with st.sidebar:
    st.header("Informações da Disciplina")
    discipline_name = st.text_input("Nome da Disciplina")
    
    st.subheader("Conteúdo Programático")
    course_content = st.text_area("Descreva os principais tópicos abordados na disciplina", 
                                height=200,
                                placeholder="Ex: 1. Introdução à Álgebra Linear\n2. Matrizes e Operações\n3. Sistemas Lineares...")
    
    # Informações sobre o modelo DeepSeek
    st.divider()
    st.subheader("Sobre o Modelo DeepSeek")
    st.markdown("""
        **Modelo:** deepseek/deepseek-chat
        
        **Descrição:** Um modelo de linguagem avançado capaz de gerar texto natural e coerente em múltiplos idiomas.
        
        **Capacidades:**
        - Geração de texto em português e outros idiomas
        - Criação de conteúdo educacional personalizado
        - Explicação detalhada de conceitos
        - Elaboração de materiais didáticos adaptados
        - Análise de desempenho e recomendações personalizadas
    """)

# Tabs para diferentes funcionalidades
tab1, tab2, tab3 = st.tabs(["Recomendações Personalizadas", "Geração de Texto", "Assistente Educacional"])

# Tab para recomendações personalizadas
with tab1:
    # Upload de arquivo
    st.subheader("Dados dos Alunos")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV ou Excel com as notas dos alunos", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            # Determinar o tipo de arquivo e carregar
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Exibir os dados carregados
            st.dataframe(df)
            
            # Verificar se há uma coluna 'Nome' para identificar os alunos
            if 'Nome' not in df.columns:
                st.warning("A planilha deve conter uma coluna 'Nome' para identificar os alunos.")
            else:
                # Identificar colunas numéricas (possíveis notas)
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                
                # Permitir ao usuário selecionar quais colunas são notas
                selected_columns = st.multiselect("Selecione as colunas que representam notas", 
                                                 numeric_columns, 
                                                 default=numeric_columns)
            
            if selected_columns:
                # Seleção de aluno
                selected_student = st.selectbox("Selecione um aluno para gerar recomendações", 
                                              df['Nome'].tolist())
                
                # Estilo de aprendizagem
                learning_styles = [
                    "Visual (aprende melhor com imagens, diagramas)",
                    "Auditivo (aprende melhor ouvindo explicações)",
                    "Leitura/Escrita (aprende melhor lendo e escrevendo)",
                    "Cinestésico (aprende melhor fazendo, experimentando)",
                    "Multimodal (combina vários estilos)"
                ]
                
                learning_style = st.selectbox("Selecione o estilo de aprendizagem predominante do aluno", 
                                           learning_styles)
                
                # Botão para gerar recomendações
                if st.button("Gerar Recomendações Personalizadas"):
                    if not discipline_name or not course_content:
                        st.warning("Por favor, preencha as informações da disciplina na barra lateral.")
                    else:
                        with st.spinner("Gerando recomendações personalizadas..."):
                            # Obter dados do aluno selecionado
                            student_data = df[df['Nome'] == selected_student].iloc[0]
                            
                            # Identificar áreas de dificuldade
                            weak_areas = identify_weak_areas(student_data, selected_columns)
                            
                            # Gerar prompt para a IA
                            prompt = generate_recommendation_prompt(
                                selected_student, 
                                student_data, 
                                weak_areas, 
                                course_content, 
                                learning_style
                            )
                            
                            # Obter recomendações da IA usando o modelo DeepSeek
                            recommendations = get_deepseek_recommendations(prompt)
                            
                            if recommendations:
                                st.subheader(f"Plano de Estudos Personalizado para {selected_student}")
                                st.markdown(recommendations)
                                
                                # Opção para salvar as recomendações
                                if st.button("Salvar Recomendações"):
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"recomendacoes_{selected_student.replace(' ', '_')}_{timestamp}.txt"
                                    
                                    with open(filename, "w", encoding="utf-8") as f:
                                        f.write(f"Recomendações para {selected_student} - {discipline_name}\n")
                                        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                                        f.write(recommendations)
                                    
                                    st.success(f"Recomendações salvas como {filename}")
                                    
                                    # Botão para download
                                    with open(filename, "r", encoding="utf-8") as f:
                                        st.download_button(
                                            label="Baixar Recomendações",
                                            data=f.read(),
                                            file_name=filename,
                                            mime="text/plain"
                                        )
                            else:
                                st.error("Não foi possível gerar as recomendações. Verifique a chave da API.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
            st.info("Verifique se o arquivo está no formato correto e tente novamente.")
    else:
        # Exibir instruções quando nenhum arquivo for carregado
        st.info("Carregue um arquivo CSV ou Excel com os dados dos alunos para começar a gerar recomendações.")
    
    # Exemplo de formato esperado
    # Inserir um botao para exibir o formato esperado
    if st.checkbox("Exibir formato esperado do arquivo"):
        st.subheader("Formato esperado do arquivo")
        example_data = {
            'Nome': ['Aluno 1', 'Aluno 2', 'Aluno 3'],
            'Nota 1': [7.5, 6.0, 8.5],
            'Nota 2': [8.0, 5.5, 9.0],
            'Nota 3': [6.5, 7.0, 7.5]
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df)
    
    st.markdown("""
    ### Como usar esta ferramenta:
    
    1. Preencha as informações da disciplina na barra lateral
    2. Carregue um arquivo CSV ou Excel com as notas dos alunos
    3. Selecione as colunas que representam notas
    4. Escolha um aluno para gerar recomendações
    5. Selecione o estilo de aprendizagem predominante do aluno
    6. Clique em "Gerar Recomendações Personalizadas"
    
    As recomendações geradas incluirão um plano de estudos personalizado, materiais de estudo 
    recomendados, exercícios práticos e estratégias de aprendizado adaptadas ao estilo do aluno.
    """)

# Tab para geração de texto com o modelo DeepSeek
# Tab para geração de texto com o modelo DeepSeek
with tab2:
    st.subheader("Geração de Texto com Modelo DeepSeek")
    
    st.markdown("""
        Esta ferramenta utiliza o modelo de linguagem Deepseek para gerar textos em português 
        sobre temas educacionais. Você pode usar esta funcionalidade para criar materiais didáticos, 
        explicações de conceitos, resumos de conteúdo e muito mais.
    """)
    
    # Área para entrada do prompt
    text_prompt = st.text_area(
        "Digite o tema ou assunto para geração de texto:",
        height=150,
        placeholder="Ex: Explique o conceito de fotossíntese de forma simples para alunos do ensino fundamental..."
    )
    
    # Opções de configuração
    st.subheader("Configurações de Geração")
    
    text_style = st.selectbox(
        "Estilo do texto:",
        options=[
            "Explicativo",
            "Resumo",
            "Material didático",
            "Exercícios",
            "Plano de aula"
        ],
        index=0
    )
    
    # Botão para gerar texto
    if st.button("Gerar Texto"):
        if not text_prompt:
            st.warning("Por favor, digite um tema ou assunto para gerar o texto.")
        else:
            with st.spinner("Gerando texto com o modelo DeepSeek..."):
                # Preparar o prompt completo
                full_prompt = f"Você é um assistente educacional especializado em criar conteúdo didático. "                
                full_prompt += f"Gere um texto no estilo {text_style} sobre o seguinte tema: {text_prompt}. "
                
                # Obter resposta do modelo DeepSeek
                generated_text = get_deepseek_assistant_response(full_prompt)
                
                if generated_text:
                    st.subheader("Texto Gerado")
                    st.markdown(generated_text)
                    
                    # Opção para salvar o texto
                    if st.button("Salvar Texto"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"texto_gerado_{timestamp}.txt"
                        
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(f"Texto gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                            f.write(f"Tema: {text_prompt}\n")
                            f.write(f"Estilo: {text_style}\n\n")
                            f.write(generated_text)
                        
                        st.success(f"Texto salvo como {filename}")
                        
                        # Botão para download
                        with open(filename, "r", encoding="utf-8") as f:
                            st.download_button(
                                label="Baixar Texto",
                                data=f.read(),
                                file_name=filename,
                                mime="text/plain"
                            )
                else:
                    st.error("Não foi possível gerar o texto. Tente novamente mais tarde.")

# Tab para assistente educacional
with tab3:
    st.subheader("Assistente Educacional Inteligente")
    
    st.markdown("""
        Este assistente educacional utiliza o modelo de linguagem DeepSeek para responder perguntas, 
        explicar conceitos e fornecer suporte pedagógico. Você pode fazer perguntas sobre conteúdos 
        didáticos, solicitar explicações ou pedir sugestões de atividades.
    """)
    
    # Inicializar histórico de conversa se não existir
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Exibir histórico de conversa
    for i, message in enumerate(st.session_state['chat_history']):
        if message['role'] == 'user':
            st.chat_message('user').write(message['content'])
        else:
            st.chat_message('assistant').write(message['content'])
    
    # Campo para entrada da pergunta
    user_question = st.chat_input("Digite sua pergunta ou solicitação...")
    
    if user_question:
        # Adicionar pergunta ao histórico
        st.session_state['chat_history'].append({"role": "user", "content": user_question})
        
        # Exibir pergunta do usuário
        st.chat_message("user").write(user_question)
        
        # Preparar contexto com base no histórico (últimas 3 interações)
        context = ""
        recent_history = st.session_state['chat_history'][-6:] if len(st.session_state['chat_history']) > 6 else st.session_state['chat_history']
        for msg in recent_history:
            prefix = "Usuário: " if msg['role'] == 'user' else "Assistente: "
            context += prefix + msg['content'] + "\n"
        
        # Preparar o prompt para o modelo
        prompt = f"Você é um assistente educacional especializado em ajudar professores e alunos. "
        prompt += f"Contexto da conversa:\n{context}\n"
        prompt += f"Responda à última pergunta do usuário de forma clara, educativa e útil. "
        prompt += f"Se for uma pergunta sobre conteúdo, forneça explicações detalhadas. "
        prompt += f"Se for um pedido de sugestão de atividade, ofereça ideias práticas e aplicáveis."
        
        # Obter resposta do modelo
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = get_deepseek_assistant_response(prompt)
                
                if response:
                    st.write(response)
                    # Adicionar resposta ao histórico
                    st.session_state['chat_history'].append({"role": "assistant", "content": response})
                else:
                    st.error("Não foi possível gerar uma resposta. Tente novamente mais tarde.")
    
    # Opção para limpar o histórico
    if st.session_state['chat_history'] and st.button("Limpar Conversa"):
        st.session_state['chat_history'] = []
        st.rerun()