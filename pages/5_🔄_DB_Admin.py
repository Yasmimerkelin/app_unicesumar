import streamlit as st
import sqlite3
import pandas as pd
import os
import json
import shutil
from datetime import datetime
from utils import add_logo, apply_custom_styles, customize_button_color

# Configuração da página
st.set_page_config(
    page_title="Administração do Banco de Dados",
    page_icon="🔄",
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
st.title("🔄 Administração do Banco de Dados 🔄")

# Informações sobre a página
st.markdown("""
    Esta página permite gerenciar o banco de dados SQLite utilizado para armazenar as tarefas.
    Aqui você pode realizar operações como backup, restauração e visualização dos dados armazenados.
""")

# Criar pasta de backup se não existir
if not os.path.exists("backups"):
    os.makedirs("backups")

# Funções para manipulação do banco de dados
def get_db_connection():
    conn = sqlite3.connect('data/tarefas.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tarefas').fetchall()
    conn.close()
    return tasks

def create_backup():
    # Verificar se o banco de dados existe
    if not os.path.exists('data/tarefas.db'):
        return False, "Banco de dados não encontrado."
    
    # Criar nome para o arquivo de backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/tarefas_backup_{timestamp}.db"
    
    try:
        # Copiar o arquivo do banco de dados
        shutil.copy2('data/tarefas.db', backup_file)
        
        # Exportar os dados para um arquivo JSON para visualização fácil
        conn = get_db_connection()
        tasks = conn.execute('SELECT * FROM tarefas').fetchall()
        conn.close()
        
        tasks_list = []
        for task in tasks:
            task_dict = dict(task)
            tasks_list.append(task_dict)
        
        json_file = f"backups/tarefas_backup_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(tasks_list, f, indent=4)
        
        return True, f"Backup criado com sucesso: {backup_file}"
    except Exception as e:
        return False, f"Erro ao criar backup: {str(e)}"

def restore_backup(backup_file):
    try:
        # Verificar se o arquivo de backup existe
        if not os.path.exists(backup_file):
            return False, "Arquivo de backup não encontrado."
        
        # Criar backup do banco atual antes de restaurar
        if os.path.exists('data/tarefas.db'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2('data/tarefas.db', f"data/tarefas_pre_restore_{timestamp}.db")
        
        # Restaurar o backup
        shutil.copy2(backup_file, 'data/tarefas.db')
        
        return True, "Backup restaurado com sucesso!"
    except Exception as e:
        return False, f"Erro ao restaurar backup: {str(e)}"

def get_backup_files():
    if not os.path.exists("backups"):
        return []
    
    backup_files = [f for f in os.listdir("backups") if f.endswith(".db")]
    backup_files.sort(reverse=True)  # Mais recentes primeiro
    return backup_files

def optimize_db():
    try:
        conn = get_db_connection()
        conn.execute("VACUUM")
        conn.close()
        return True, "Banco de dados otimizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao otimizar banco de dados: {str(e)}"

# Tabs para diferentes operações
tab1, tab2, tab3, tab4 = st.tabs(["Visualizar Dados", "Backup", "Restauração", "Manutenção"])

# Tab para visualizar dados
with tab1:
    st.header("Visualizar Dados do Banco")
    
    # Botão para atualizar os dados
    if st.button("Atualizar Dados"):
        st.rerun()
    
    # Verificar se o banco de dados existe
    if not os.path.exists('data/tarefas.db'):
        st.warning("Banco de dados não encontrado. Crie tarefas primeiro.")
    else:
        # Obter e exibir os dados
        tasks = get_all_tasks()
        
        if not tasks:
            st.info("Nenhuma tarefa encontrada no banco de dados.")
        else:
            # Converter para dataframe
            tasks_list = []
            for task in tasks:
                task_dict = dict(task)
                # Converter valores para exibição
                task_dict['completed'] = "Sim" if task_dict['completed'] else "Não"
                task_dict['date'] = datetime.strptime(task_dict['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                task_dict['created_at'] = datetime.strptime(task_dict['created_at'], '%Y-%m-%d').strftime('%d/%m/%Y')
                tasks_list.append(task_dict)
            
            df = pd.DataFrame(tasks_list)
            
            # Renomear colunas para exibição
            df = df.rename(columns={
                'id': 'ID',
                'description': 'Descrição',
                'date': 'Data',
                'priority': 'Prioridade',
                'category': 'Categoria',
                'observation': 'Observação',
                'completed': 'Concluída',
                'created_at': 'Criada em'
            })
            
            # Exibir dataframe
            st.dataframe(df)
            
            # Estatísticas básicas
            st.subheader("Estatísticas")
            col1, col2, col3 = st.columns(3)
            
            col1.metric("Total de Tarefas", len(tasks))
            col2.metric("Concluídas", len([t for t in tasks if t['completed']]))
            col3.metric("Pendentes", len([t for t in tasks if not t['completed']]))

# Tab para backup
with tab2:
    st.header("Backup do Banco de Dados")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            O backup cria uma cópia do banco de dados atual. Isso é útil para:
            
            - Preservar dados importantes
            - Transferir dados entre instalações
            - Restaurar em caso de perda de dados
        """)
        
        # Botão para criar backup
        if st.button("Criar Novo Backup"):
            success, message = create_backup()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        st.subheader("Backups Existentes")
        
        backup_files = get_backup_files()
        if not backup_files:
            st.info("Nenhum backup encontrado.")
        else:
            for backup in backup_files:
                st.write(f"📁 {backup}")
        
        # Mostrar espaço usado pelos backups
        if backup_files:
            total_size = sum(os.path.getsize(os.path.join("backups", f)) for f in backup_files)
            st.write(f"Espaço utilizado: {total_size / (1024*1024):.2f} MB")

# Tab para restauração
with tab3:
    st.header("Restaurar Backup")
    
    backup_files = get_backup_files()
    if not backup_files:
        st.warning("Nenhum backup disponível para restauração.")
    else:
        st.warning("⚠️ A restauração substituirá TODOS os dados atuais. Faça um backup antes de continuar!")
        
        selected_backup = st.selectbox(
            "Selecione o backup para restaurar:",
            options=backup_files
        )
        
        # Confirmar restauração
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Restaurar Backup Selecionado"):
                confirm = st.session_state.get('confirm_restore', False)
                if confirm:
                    backup_path = os.path.join("backups", selected_backup)
                    success, message = restore_backup(backup_path)
                    if success:
                        st.success(message)
                        st.info("Recarregue a página para ver as mudanças.")
                    else:
                        st.error(message)
                else:
                    st.session_state['selected_for_restore'] = selected_backup
                    st.session_state['confirm_restore'] = True
                    st.warning("Confirme a restauração clicando novamente no botão.")
        
        with col2:
            if st.button("Cancelar"):
                st.session_state['confirm_restore'] = False
                st.rerun()
        
        # Mostrar detalhes do backup selecionado
        if selected_backup:
            backup_path = os.path.join("backups", selected_backup)
            created_time = datetime.fromtimestamp(os.path.getctime(backup_path))
            file_size = os.path.getsize(backup_path) / 1024  # KB
            
            st.subheader("Detalhes do Backup")
            st.write(f"Data de criação: {created_time.strftime('%d/%m/%Y %H:%M:%S')}")
            st.write(f"Tamanho: {file_size:.2f} KB")
            
            # Verificar se existe um arquivo JSON correspondente para mostrar conteúdo
            json_path = backup_path.replace(".db", ".json")
            if os.path.exists(json_path):
                with st.expander("Ver conteúdo do backup"):
                    try:
                        with open(json_path, 'r') as f:
                            backup_data = json.load(f)
                        
                        if backup_data:
                            # Converter para dataframe para exibição
                            df = pd.DataFrame(backup_data)
                            # Converter valores para exibição
                            if 'completed' in df.columns:
                                df['completed'] = df['completed'].apply(lambda x: "Sim" if x else "Não")
                            if 'date' in df.columns:
                                df['date'] = df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%d/%m/%Y') if x else "")
                            if 'created_at' in df.columns:
                                df['created_at'] = df['created_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%d/%m/%Y') if x else "")
                            
                            st.dataframe(df)
                        else:
                            st.info("Backup vazio (sem tarefas).")
                    except:
                        st.error("Não foi possível carregar os detalhes do backup.")

# Tab para manutenção
with tab4:
    st.header("Manutenção do Banco de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Otimizar Banco de Dados")
        st.markdown("""
            A otimização do banco de dados:
            
            - Reduz o tamanho do arquivo
            - Melhora performance de consultas
            - Limpa espaço não utilizado
        """)
        
        if st.button("Otimizar DB"):
            success, message = optimize_db()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        st.subheader("Limpeza de Backups")
        st.markdown("""
            Remover backups antigos para liberar espaço em disco.
            É recomendado manter pelo menos os 3 backups mais recentes.
        """)
        
        backup_files = get_backup_files()
        if not backup_files:
            st.info("Nenhum backup para limpar.")
        else:
            # Permitir selecionar backups para excluir
            backups_to_delete = st.multiselect(
                "Selecione os backups a serem removidos:",
                options=backup_files
            )
            
            if backups_to_delete:
                if st.button("Excluir Backups Selecionados"):
                    try:
                        for backup in backups_to_delete:
                            backup_path = os.path.join("backups", backup)
                            os.remove(backup_path)
                            
                            # Remover também o JSON se existir
                            json_path = backup_path.replace(".db", ".json")
                            if os.path.exists(json_path):
                                os.remove(json_path)
                        
                        st.success(f"{len(backups_to_delete)} backup(s) removido(s) com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao remover backups: {str(e)}")

# Informações adicionais
st.divider()
st.markdown("""
    ### Informações do Banco de Dados
    
    O sistema utiliza SQLite como banco de dados relacional leve para armazenar as tarefas.
    Os arquivos são armazenados na pasta `data/` e os backups na pasta `backups/`.
    
    **Estrutura da tabela:**
    ```sql
    CREATE TABLE tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        priority TEXT NOT NULL,
        category TEXT NOT NULL,
        observation TEXT,
        completed BOOLEAN NOT NULL,
        created_at TEXT NOT NULL
    )
    ```
""")

# Mostrar informações do arquivo do banco de dados
if os.path.exists('data/tarefas.db'):
    file_size = os.path.getsize('data/tarefas.db') / 1024  # KB
    created_time = datetime.fromtimestamp(os.path.getctime('data/tarefas.db'))
    modified_time = datetime.fromtimestamp(os.path.getmtime('data/tarefas.db'))
    
    st.write(f"**Tamanho do banco de dados:** {file_size:.2f} KB")
    st.write(f"**Criado em:** {created_time.strftime('%d/%m/%Y %H:%M:%S')}")
    st.write(f"**Última modificação:** {modified_time.strftime('%d/%m/%Y %H:%M:%S')}") 