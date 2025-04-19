import streamlit as st
import os
from utils import add_logo, apply_custom_styles, customize_button_color

# Configuração da página
st.set_page_config(
    page_title="Configurações",
    page_icon="⚙️",
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
st.title("⚙️ Configurações do Sistema ⚙️")

# Função para salvar a chave da API no secrets.toml
def save_api_key(api_key, api_type="DEEPSEEK"):
    try:
        secrets_path = os.path.join('.streamlit', 'secrets.toml')

        # Verificar se o diretório .streamlit existe
        if not os.path.exists('.streamlit'):
            os.makedirs('.streamlit')

        # Ler o conteúdo atual do arquivo se ele existir
        existing_content = ""
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                existing_content = f.read()

        # Verificar nome da chave
        key_name = f"{api_type}_API_KEY"

        # Criar um dicionário com as chaves existentes
        keys = {}
        for line in existing_content.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                keys[k.strip()] = v.strip()

        # Atualizar ou adicionar a nova chave
        keys[key_name] = f'"{api_key}"'

        # Escrever todas as chaves no arquivo
        with open(secrets_path, 'w') as f:
            for k, v in keys.items():
                f.write(f'{k} = {v}\n')

        return True
    except Exception as e:
        st.error(f"Erro ao salvar a chave da API: {e}")
        return False

# Interface principal
st.markdown("""
    Esta página permite configurar as opções do sistema, como as chaves de API 
    utilizadas para as análises de desempenho e recomendações personalizadas.
""")

# Seção de configuração da API do DeepSeek (OpenRouter)
st.subheader("Configuração da API do DeepSeek (OpenRouter)")

# Verificar se já existe uma chave salva
deepseek_api_key_exists = False
try:
    if 'DEEPSEEK_API_KEY' in st.secrets:
        deepseek_api_key_exists = True
except:
    pass

# Exibir status atual
if deepseek_api_key_exists:
    st.success("✅ Chave da API do DeepSeek configurada")
    if st.button("Atualizar Chave da API DeepSeek"):
        st.session_state['show_deepseek_api_input'] = True
else:
    st.warning("⚠️ Chave da API do DeepSeek não configurada")
    st.session_state['show_deepseek_api_input'] = True

# Exibir campo para inserir a chave
if 'show_deepseek_api_input' in st.session_state and st.session_state['show_deepseek_api_input']:
    deepseek_api_key = st.text_input("Insira sua chave da API DeepSeek (OpenRouter)", type="password", 
                              value="" if deepseek_api_key_exists else "")
    
    if st.button("Salvar Chave da API DeepSeek"):
        if deepseek_api_key:
            if save_api_key(deepseek_api_key, "DEEPSEEK"):
                st.success("Chave da API DeepSeek salva com sucesso!")
                st.session_state['show_deepseek_api_input'] = False
                st.rerun()
        else:
            st.error("Por favor, insira uma chave válida.")

# Instruções de uso
st.subheader("Instruções de Uso")
st.markdown("""
    ### Como obter uma chave da API do DeepSeek via OpenRouter:
    
    1. Acesse [OpenRouter.ai](https://openrouter.ai/)
    2. Crie uma conta ou faça login
    3. Vá até a seção "API Keys"
    4. Gere uma nova chave
    5. Copie a chave e cole no campo acima

    ### Observações importantes:
    
    - A chave da API é necessária para utilizar os recursos de IA deste sistema.
    - Sua chave é armazenada localmente e não é compartilhada com terceiros.
    - Você pode atualizar sua chave a qualquer momento nesta página.
""")

# # Outras configurações do sistema
# st.subheader("Outras Configurações")

# # Tema da interface
# st.write("Tema da Interface")
# theme_options = ["Claro", "Escuro", "Sistema"]
# selected_theme = st.selectbox("Selecione o tema da interface", theme_options, index=2)

# if st.button("Aplicar Tema"):
#     st.success(f"Tema {selected_theme} aplicado com sucesso!")
#     st.info("Esta funcionalidade será implementada em uma versão futura.")

# Informações do sistema
st.subheader("Informações do Sistema")
st.markdown("""
    **Versão do Aplicativo:** 1.0.0  
    **Desenvolvido por:** Yasmim Merklein  
    **Contato:** yasmimerklein@hotmail.com 
""")

# Feedback e sugestões
st.subheader("Feedback e Sugestões")
st.markdown("""
    Sua opinião é importante para melhorarmos continuamente este aplicativo.
    Por favor, compartilhe suas sugestões, problemas encontrados ou ideias para novos recursos.
""")

feedback = st.text_area("Deixe seu feedback", height=150)
if st.button("Enviar Feedback"):
    if feedback:
        st.success("Feedback enviado com sucesso! Agradecemos sua contribuição.")
        st.info("Esta funcionalidade será implementada em uma versão futura.")
    else:
        st.error("Por favor, escreva seu feedback antes de enviar.")
