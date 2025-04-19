import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from utils import add_logo, apply_custom_styles, customize_button_color

# Configuração da página
st.set_page_config(
    page_title="Unicesumar - App Educativo",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Detecta o tema do Streamlit dinamicamente e injeta classe no body
components.html("""
<script>
const observer = new MutationObserver((mutations) => {
    for (let mutation of mutations) {
        if (mutation.attributeName === "data-theme") {
            const theme = document.documentElement.getAttribute("data-theme");
            document.body.classList.remove("light", "dark");
            document.body.classList.add(theme);
        }
    }
});
observer.observe(document.documentElement, { attributes: true });
const currentTheme = document.documentElement.getAttribute("data-theme");
document.body.classList.add(currentTheme);
</script>
""", height=0)


# Adicionar Logo da Universidade e estilos
img_path = 'assets/logo_uni_v2.jpg'
try:
    add_logo(img_path)
except:
    st.warning("Logo não encontrada. Verifique o caminho da imagem.")
apply_custom_styles()
customize_button_color()

# Texto sobre a Unicesumar
texto_unicesumar = """
<p style='text-align: justify;'> 
A <strong>Unicesumar</strong> é uma instituição de ensino superior privada brasileira, com sede em Maringá, no estado do Paraná. 
Fundada em 1990, a instituição oferece cursos de graduação, pós-graduação e extensão em diversas áreas do conhecimento. 
Tem como missão promover a educação de qualidade nas diferentes áreas do conhecimento, formando profissionais cidadãos que 
contribuam para o desenvolvimento de uma sociedade justa e solidária.
</p>
"""

# Sidebar com informações e navegação
with st.sidebar:
    with st.container(border=True):
        st.markdown(texto_unicesumar, unsafe_allow_html=True)

    st.subheader("Navegação Rápida")
    st.markdown("""
    - [📝 Gerenciador de Tarefas](/Tarefas)
    - [📊 Alunos/Desempenho](/Alunos)
    - [🧠 Recomendações Personalizadas](/Recomendacoes_Personalizadas)
    - [⚙️ Configurações](/Configuracoes)
    - [🔄 Administração do Banco de Dados](/DB_Admin)
    """, unsafe_allow_html=True)

# Estilo da página
st.markdown("""
<style>
/* Tema Claro */
body.light .feature-card-improved {
    background-color: #ffffff;
    border: 1px solid #f0f0f0;
}
body.light .feature-description-improved {
    color: #333;
}
body.light .feature-title-improved {
    color: #c7141a;
}
body.light .feature-card-improved:hover .feature-title-improved {
    color: #493aa0;
}
body.light .welcome-box,
body.light .rodape-box {
    background-color: #f0f2f6;
    color: #000;
}

/* Tema Escuro */
body.dark .feature-card-improved {
    background-color: #262730;
    border: 1px solid #3a3a3a;
}
body.dark .feature-description-improved {
    color: #dddddd;
}
body.dark .feature-title-improved {
    color: #c7141a;
}
body.dark .feature-card-improved:hover .feature-title-improved {
    color: #8a85ff;
}
body.dark .welcome-box,
body.dark .rodape-box {
    background-color: #333;
    color: #f2f2f2;
}

/* Comum */
.main-title {
    font-size: 3.5rem;
    text-align: center;
    margin-bottom: -4rem;

}

.subtitle {
    font-size: 1.5rem;
    text-align: center;
    margin-bottom: 2rem;
}
.feature-card-improved {
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    transition: all 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    transform: scale(1);
    border-left: 5px solid #c7141a;  /* <- Aqui está o destaque */
}

.feature-card-improved:hover {
    transform: scale(1.03);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}
.feature-icon {
    font-size: 3rem;
    margin-bottom: 20px;
    color: #c7141a;
    transition: transform 0.3s ease;
}
.feature-card-improved:hover .feature-icon {
    transform: scale(1.2);
}
.feature-description-improved {
    font-size: 1.1rem;
    text-align: center;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)




# Título principal
st.markdown('<h1 class="main-title">Sistema Educacional Unicesumar</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma integrada para gestão acadêmica e acompanhamento de desempenho</p>', unsafe_allow_html=True)

# Seção de boas-vindas
st.markdown("""
<div class="welcome-box" style="border-radius: 10px; padding: 30px; margin-bottom: 30px; text-align: center;">
    <h3>👋 Bem-vindo ao Sistema Educacional Unicesumar!</h3>
    <p>Esta plataforma foi desenvolvida para facilitar a gestão acadêmica, o acompanhamento de desempenho dos alunos e a organização de tarefas educacionais. 
    Navegue pelo menu lateral para acessar todas as funcionalidades.</p>
</div>
""", unsafe_allow_html=True)



# Principais funcionalidades
st.subheader("Principais Funcionalidades")

col1, col2 = st.columns(2)

with col1:
    st.markdown('''
    <div class="feature-card-improved">
        <div class="feature-icon">📝</div>
        <div class="feature-title-improved">Gerenciador de Tarefas</div>
        <div class="feature-description-improved">
            Organize suas atividades acadêmicas, defina prazos e acompanhe o progresso das tarefas com facilidade.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="feature-card-improved">
        <div class="feature-icon">📊</div>
        <div class="feature-title-improved">Análise de Desempenho</div>
        <div class="feature-description-improved">
            Visualize gráficos e estatísticas detalhadas sobre o desempenho dos alunos em diferentes disciplinas.
        </div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown('''
    <div class="feature-card-improved">
        <div class="feature-icon">👨‍🎓</div>
        <div class="feature-title-improved">Controle de Alunos</div>
        <div class="feature-description-improved">
            Gerencie informações dos alunos, notas, frequência e situação acadêmica de forma intuitiva.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="feature-card-improved">
        <div class="feature-icon">🧠</div>
        <div class="feature-title-improved">Recomendações Personalizadas</div>
        <div class="feature-description-improved">
            Receba sugestões de estudo personalizadas com base no desempenho individual de cada aluno usando IA.
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Novo card para administração do banco de dados
st.markdown('''
<div class="feature-card-improved">
    <div class="feature-icon">🔄</div>
    <div class="feature-title-improved">Administração do Banco de Dados</div>
    <div class="feature-description-improved">
        Faça backup, restauração e manutenção do banco de dados SQLite que armazena as informações do sistema.
    </div>
</div>
''', unsafe_allow_html=True)

# Seção de recursos disponíveis
st.subheader("Recursos Disponíveis")

with st.container(border=True):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 🔍 Funcionalidades Inclusas")
    with col2:
        st.markdown("""
        - **Integração com IA**: Sistema utiliza a API da DeepSeek (OpenRouter) para sugestões inteligentes.  
        - **Interface Aprimorada**: Design moderno, intuitivo e adaptável.  
        - **Relatórios Interativos**: Gráficos e análises para facilitar a tomada de decisão acadêmica.  
        - **Plataforma Modular**: Navegação simplificada por módulos separados.  
        - **Banco de Dados SQLite**: Armazenamento persistente de dados com funcionalidades de backup e restauração.
        """)

# Rodapé
st.markdown("""
<div class="rodape-box" style="text-align: center; margin-top: 50px; padding: 20px; border-radius: 10px;">
    <p style="font-size: 0.8rem;">Desenvolvido com ❤️ por Yasmim Merklein</p>
</div>
""", unsafe_allow_html=True)


#     <p>© 2024 Unicesumar - Sistema Educacional. Todos os direitos reservados.</p>