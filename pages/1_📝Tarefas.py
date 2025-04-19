import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from utils import add_logo, apply_custom_styles, customize_button_color

# Configuração da página
st.set_page_config(
    page_title="Gerenciador de Tarefas",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state='expanded'
)

# Configuração do banco de dados SQLite
def init_db():
    # Criar pasta de dados se não existir
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Conectar ao banco de dados (será criado se não existir)
    conn = sqlite3.connect('data/tarefas.db')
    c = conn.cursor()
    
    # Criar tabela se não existir
    c.execute('''
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        priority TEXT NOT NULL,
        category TEXT NOT NULL,
        observation TEXT,
        completed BOOLEAN NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# Função para carregar tarefas do banco de dados
def load_tasks():
    conn = sqlite3.connect('data/tarefas.db')
    # Converter resultados para dicionário
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM tarefas')
    rows = c.fetchall()
    
    tasks = []
    for row in rows:
        task = dict(row)
        # Converter strings para os tipos corretos
        task['date'] = datetime.strptime(task['date'], '%Y-%m-%d').date()
        task['created_at'] = datetime.strptime(task['created_at'], '%Y-%m-%d').date()
        task['completed'] = bool(task['completed'])
        tasks.append(task)
    
    conn.close()
    return tasks

# Função para adicionar tarefa ao banco de dados
def add_task_to_db(description, date, priority, category, observation, completed=False):
    conn = sqlite3.connect('data/tarefas.db')
    c = conn.cursor()
    
    c.execute('''
    INSERT INTO tarefas (description, date, priority, category, observation, completed, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        description,
        date.strftime('%Y-%m-%d'),
        priority,
        category,
        observation,
        completed,
        datetime.now().date().strftime('%Y-%m-%d')
    ))
    
    conn.commit()
    conn.close()

# Função para atualizar tarefa no banco de dados
def update_task_in_db(task_id, completed=None, observation=None):
    conn = sqlite3.connect('data/tarefas.db')
    c = conn.cursor()
    
    # Construir query de atualização dinamicamente baseado nos parâmetros fornecidos
    update_parts = []
    params = []
    
    if completed is not None:
        update_parts.append("completed = ?")
        params.append(completed)
    
    if observation is not None:
        update_parts.append("observation = ?")
        params.append(observation)
    
    if update_parts:
        query = f"UPDATE tarefas SET {', '.join(update_parts)} WHERE id = ?"
        params.append(task_id)
        
        c.execute(query, params)
        conn.commit()
    
    conn.close()

# Função para remover tarefa do banco de dados
def delete_task_from_db(task_id):
    conn = sqlite3.connect('data/tarefas.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM tarefas WHERE id = ?', (task_id,))
    
    conn.commit()
    conn.close()

# Inicializar o banco de dados
init_db()

# Adicionar Logo da Universidade e estilos
img_path = 'assets/logo_uni_v2.jpg'
try:
    add_logo(img_path)
except:
    st.warning("Logo não encontrada. Verifique o caminho da imagem.")
apply_custom_styles()
customize_button_color()

texto_unicesumar = """<p style='text-align: justify;'> A <strong>Unicesumar</strong> é uma instituição de ensino superior privada brasileira, com sede em Maringá, no estado do Paraná.
Fundada em 1990, a instituição oferece cursos de graduação, pós-graduação e extensão em diversas áreas do conhecimento.
Tem como missão Promover a educação de qualidade nas diferentes áreas do conhecimento, formando profissionais cidadãos que
contribuam para o desenvolvimento de uma sociedade justa e solidária. </p> """

# Carregar tarefas do banco de dados
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = load_tasks()

# Sidebar com informações e filtros
with st.sidebar:
    with st.container(border=True):
        st.markdown(texto_unicesumar, unsafe_allow_html=True)
    
    st.subheader("Filtros")
    # Filtro por status
    status_filter = st.radio(
        "Status da Tarefa",
        options=["Todas", "Pendentes", "Concluídas"],
        horizontal=True
    )
    
    # Filtro por data
    date_filter = st.date_input(
        "Filtrar por data",
        value=None,
        help="Selecione uma data para filtrar as tarefas"
    )
    
    # Ordenação
    sort_by = st.selectbox(
        "Ordenar por",
        options=["Data (mais próxima)", "Data (mais distante)", "Alfabética"]
    )
    
    st.divider()
    
    # Estatísticas
    if 'tasks' in st.session_state and st.session_state['tasks']:
        pending_tasks = len([task for task in st.session_state['tasks'] 
                         if 'completed' not in task or not task['completed']])
        completed_tasks = len([task for task in st.session_state['tasks'] 
                           if 'completed' in task and task['completed']])
        
        st.subheader("Estatísticas")
        st.metric("Total de Tarefas", len(st.session_state['tasks']))
        st.metric("Tarefas Pendentes", pending_tasks)
        st.metric("Tarefas Concluídas", completed_tasks)
        
        # Gráfico de pizza para visualizar a proporção
        if pending_tasks > 0 or completed_tasks > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Pendentes', 'Concluídas'],
                values=[pending_tasks, completed_tasks],
                hole=.3,
                marker_colors=['#c7141a', '#493aa0']  # Cores da Unicesumar
            )])
            fig.update_layout(
                title="Distribuição de Tarefas",
                height=250,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

st.title("📝 Gerenciador de Tarefas 📝")

# Interface para adicionar tarefas
st.subheader("Adicionar Nova Tarefa")

with st.form(key="add_task_form"):
    col1, col2 = st.columns([3, 1])
    texto = col1.text_input("Descreva a tarefa:")
    data = col2.date_input("Selecione a data da tarefa:")
    
    # Campo para prioridade
    prioridade = st.select_slider(
        "Prioridade:",
        options=["Baixa", "Média", "Alta"],
        value="Média"
    )
    
    # Campo para categoria
    categoria = st.selectbox(
        "Categoria:",
        options=["Acadêmica", "Administrativa", "Pessoal", "Outro"],
        index=0
    )
    
    # Campo para observações
    observacao = st.text_area("Observações (opcional):", height=100)
    
    # Botão para adicionar tarefa
    submitted = st.form_submit_button("Adicionar Tarefa")
    
    if submitted:
        if texto and data:
            # Adicionar tarefa ao banco de dados
            add_task_to_db(texto, data, prioridade, categoria, observacao)
            
            # Adicionar à sessão
            new_task = {
                'id': len(st.session_state['tasks']) + 1,  # ID temporário, será substituído pelo do banco na próxima carga
                'description': texto,
                'date': data,
                'priority': prioridade,
                'category': categoria,
                'observation': observacao if observacao else None,
                'completed': False,
                'created_at': datetime.now().date()
            }
            st.session_state['tasks'].append(new_task)
            
            st.success("Tarefa adicionada com sucesso!")
            # Recarregar tarefas do banco de dados para obter IDs corretos
            st.session_state['tasks'] = load_tasks()
            st.rerun()
        else:
            st.error("Por favor, preencha a descrição e a data da tarefa.")

# Change color of st.button
customize_button_color()

# Função para calcular os dias restantes para a data da tarefa
def days_left(date):
    return (date - datetime.now().date()).days

# Criar uma barra de progresso para exibir o progresso da tarefa
def task_progress_bar(date):
    days_remaining = days_left(date)
    total_days = (date - datetime.now().date()).days

    # Normaliza a porcentagem entre 0 a 100
    if total_days <= 0:
        percentage = 100 if days_remaining >= 0 else 0
    else:
        percentage = min((days_remaining / total_days) * 100,
                         100) if days_remaining >= 0 else 0

    st.progress(int(percentage), text=f"{days_remaining} dias restantes")

# Função para marcar tarefa como concluída
def mark_as_completed(task_id):
    # Atualizar no banco de dados
    update_task_in_db(task_id, completed=True)
    
    # Atualizar na sessão
    for task in st.session_state['tasks']:
        if task['id'] == task_id:
            task['completed'] = True
            break

# Função para adicionar observação à tarefa
def add_observation_to_task(task_id, observation):
    # Atualizar no banco de dados
    update_task_in_db(task_id, observation=observation)
    
    # Atualizar na sessão
    for task in st.session_state['tasks']:
        if task['id'] == task_id:
            task['observation'] = observation
            break

# Função para remover tarefa
def remove_task(task_id):
    # Remover do banco de dados
    delete_task_from_db(task_id)
    
    # Remover da sessão
    st.session_state['tasks'] = [task for task in st.session_state['tasks'] if task['id'] != task_id]

# Função para lembrar usuário sobre tarefas próximas do prazo
def remind_near_due(date, days_threshold=1):
    days_remaining = days_left(date)
    if 0 < days_remaining <= days_threshold:
        return True
    return False

@st.dialog("Inserir Observação")
def obs_modal(task_id):
    # Encontrar a observação atual
    current_obs = ""
    for task in st.session_state['tasks']:
        if task['id'] == task_id and task.get('observation'):
            current_obs = task['observation']
            break
            
    obs = st.text_area("Insira uma observação", value=current_obs)
    if st.button("Salvar"):
        add_observation_to_task(task_id, obs)
        st.rerun()

# Popover para exibir observações
def show_observation(observation):
    with st.popover(label="👓", help="Clique para visualizar a observação"):
        st.write(observation)


# Tabs para diferentes visualizações
tab1, tab2 = st.tabs(["Lista de Tarefas", "Visualização em Calendário"])

# Tab para lista de tarefas
with tab1:
    if not st.session_state['tasks']:
        st.info("Nenhuma tarefa adicionada ainda.")
    else:
        # Aplicar filtros
        filtered_tasks = st.session_state['tasks'].copy()
        
        # Filtro por status
        if status_filter == "Pendentes":
            filtered_tasks = [task for task in filtered_tasks if not task.get('completed', False)]
        elif status_filter == "Concluídas":
            filtered_tasks = [task for task in filtered_tasks if task.get('completed', False)]
        
        # Filtro por data
        if date_filter:
            filtered_tasks = [task for task in filtered_tasks if task['date'] == date_filter]
        
        # Ordenação
        if sort_by == "Data (mais próxima)":
            filtered_tasks.sort(key=lambda x: x['date'])
        elif sort_by == "Data (mais distante)":
            filtered_tasks.sort(key=lambda x: x['date'], reverse=True)
        elif sort_by == "Alfabética":
            filtered_tasks.sort(key=lambda x: x['description'])
        
        # Exibir tarefas filtradas
        if not filtered_tasks:
            st.info("Nenhuma tarefa corresponde aos filtros selecionados.")
        else:
            # Separar tarefas pendentes e concluídas
            pending_tasks = [task for task in filtered_tasks if not task.get('completed', False)]
            completed_tasks = [task for task in filtered_tasks if task.get('completed', False)]
            
            # Exibir tarefas pendentes
            if pending_tasks:
                st.subheader("Tarefas Pendentes")
                for task in pending_tasks:
                    with st.container(border=True):
                        # Cabeçalho da tarefa
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        # Título com ícone de prioridade
                        priority_icon = "🔴" if task.get('priority') == "Alta" else "🟡" if task.get('priority') == "Média" else "🟢"
                        col1.markdown(f"{priority_icon} **{task['description']}**")
                        
                        # Data e categoria
                        col2.markdown(f"📅 **{task['date'].strftime('%d/%m/%Y')}**")
                        col3.markdown(f"📂 **{task.get('category', 'Acadêmica')}**")
                        
                        # Barra de progresso
                        task_progress_bar(task['date'])
                        
                        # Alerta para tarefas próximas do prazo
                        if remind_near_due(task['date']):
                            st.warning(f"⚠️ Esta tarefa vence em breve!")
                        
                        # Observações (se houver)
                        if task.get('observation'):
                            with st.expander("Ver observações"):
                                st.write(task['observation'])
                        
                        # Botões de ação
                        action_col1, action_col2, action_col3 = st.columns(3)
                        if action_col1.button(f"✅ Concluir", key=f"complete_{task['id']}"):
                            mark_as_completed(task['id'])
                            st.rerun()
                        if action_col2.button(f"🗑️ Remover", key=f"remove_{task['id']}"):
                            remove_task(task['id'])
                            st.rerun()
                        if action_col3.button(f"📝 Observação", key=f"obs_{task['id']}"):
                            obs_modal(task['id'])
            
            # Exibir tarefas concluídas
            if completed_tasks:
                st.subheader("Tarefas Concluídas")
                for task in completed_tasks:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        col1.markdown(f"✅ **{task['description']}**")
                        col2.markdown(f"📅 **{task['date'].strftime('%d/%m/%Y')}**")
                        
                        # Observações (se houver)
                        if task.get('observation'):
                            with st.expander("Ver observações"):
                                st.write(task['observation'])
                        
                        # Botão para remover
                        if st.button(f"🗑️ Remover", key=f"remove_completed_{task['id']}"):
                            remove_task(task['id'])
                            st.rerun()

# Tab para visualização em calendário
with tab2:
    st.subheader("Calendário de Tarefas")
    
    # Obter o mês atual
    if 'calendar_month' not in st.session_state:
        st.session_state['calendar_month'] = datetime.now().month
        st.session_state['calendar_year'] = datetime.now().year
    
    # Controles de navegação do calendário
    cal_col1, cal_col2, cal_col3 = st.columns([1, 2, 1])
    
    if cal_col1.button("◀️ Mês Anterior"):
        if st.session_state['calendar_month'] > 1:
            st.session_state['calendar_month'] -= 1
        else:
            st.session_state['calendar_month'] = 12
            st.session_state['calendar_year'] -= 1
        st.rerun()
    
    cal_col2.markdown(f"### {datetime(st.session_state['calendar_year'], st.session_state['calendar_month'], 1).strftime('%B %Y')}")
    
    if cal_col3.button("Mês Seguinte ▶️"):
        if st.session_state['calendar_month'] < 12:
            st.session_state['calendar_month'] += 1
        else:
            st.session_state['calendar_month'] = 1
            st.session_state['calendar_year'] += 1
        st.rerun()
    
    # Criar visualização de calendário
    import calendar
    cal = calendar.monthcalendar(st.session_state['calendar_year'], st.session_state['calendar_month'])
    
    # Dias da semana
    dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    
    # Criar grid para o calendário
    st.write("")
    for i, dia in enumerate(dias_semana):
        st.markdown(f"<style>.dia-semana-{i} {{text-align: center; font-weight: bold;}}</style>", unsafe_allow_html=True)
    
    # Cabeçalho do calendário
    cols_dias = st.columns(7)
    for i, col in enumerate(cols_dias):
        col.markdown(f"<div class='dia-semana-{i}'>{dias_semana[i]}</div>", unsafe_allow_html=True)
    
    # Corpo do calendário
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia != 0:
                # Verificar se há tarefas para este dia
                data_atual = datetime(st.session_state['calendar_year'], st.session_state['calendar_month'], dia).date()
                tarefas_do_dia = [task for task in st.session_state['tasks'] if task['date'] == data_atual]
                
                # Estilo para o dia atual
                estilo_dia = ""
                if data_atual == datetime.now().date():
                    estilo_dia = "background-color: rgba(199, 20, 26, 0.2); border-radius: 5px; padding: 5px;"
                
                # Exibir o dia e as tarefas
                with cols[i]:
                    st.markdown(f"<div style='{estilo_dia}'><b>{dia}</b></div>", unsafe_allow_html=True)
                    
                    # Mostrar indicadores de tarefas
                    for task in tarefas_do_dia:
                        status = "✅" if task.get('completed', False) else "⏳"
                        priority_color = "red" if task.get('priority') == "Alta" else "orange" if task.get('priority') == "Média" else "green"
                        st.markdown(f"<div style='font-size: 0.8em; color: {priority_color};'>{status} {task['description'][:15]}...</div>", unsafe_allow_html=True)


# Exibir data
# Criar cards o numero de tarefas pendentes e concluídas
pending_tasks = len([task for task in st.session_state['tasks']
                     if 'completed' not in task or not task['completed']])
completed_tasks = len([task for task in st.session_state['tasks']
                       if 'completed' in task and task['completed']])

st.subheader("**Resumo das Tarefas**")
col1, col2 = st.columns(2)
col1.metric("Tarefas Pendentes", pending_tasks)
col2.metric("Tarefas Concluídas", completed_tasks)

# Adicionar um divisor
st.divider()

# Exibir tabela de dados como dataframe
if st.session_state['tasks']:
    # Converter para dataframe para visualização
    tasks_df = pd.DataFrame(st.session_state['tasks'])
    # Converter boolean para string para melhor visualização
    tasks_df['completed'] = tasks_df['completed'].apply(lambda x: "Sim" if x else "Não")
    # Renomear colunas para português
    tasks_df = tasks_df.rename(columns={
        'id': 'ID',
        'description': 'Descrição',
        'date': 'Data',
        'priority': 'Prioridade',
        'category': 'Categoria',
        'observation': 'Observação',
        'completed': 'Concluída',
        'created_at': 'Criada em'
    })
    st.dataframe(tasks_df)
else:
    st.info("Nenhuma tarefa para exibir.")

# Opção para exportar dados
if st.session_state['tasks']:
    st.download_button(
        label="Exportar Tarefas (CSV)",
        data=pd.DataFrame(st.session_state['tasks']).to_csv(index=False).encode('utf-8'),
        file_name='tarefas_export.csv',
        mime='text/csv',
    )
