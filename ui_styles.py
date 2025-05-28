"""
Estilos CSS mejorados para toda la aplicación
"""

# Estilo común para toda la aplicación
APP_STYLES = """
<style>
    /* Variables de color */
    :root {
        --primary: #FF4B4B;
        --primary-light: #FFEBEB;
        --secondary: #0068C9;
        --secondary-light: #E6F0FF;
        --success: #09AB3B;
        --success-light: #E9F9EF;
        --warning: #FFBD45;
        --warning-light: #FFF8E6;
        --info: #3366FF;
        --info-light: #EBF0FF;
        --light: #F0F2F6;
        --dark: #262730;
        --gray: #BFBFBF;
        --white: #FFFFFF;
    }
    
    /* Estilos generales */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Encabezados */
    h1.app-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 1.5rem;
    }
    
    h2.section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--secondary);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--secondary-light);
        padding-bottom: 0.5rem;
    }
    
    h3.subsection-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--dark);
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Cajas de contenido */
    .content-box {
        background-color: var(--white);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #E0E4EB;
        transition: all 0.3s ease;
    }
    
    .content-box:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Cajas de estado */
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .status-box.success {
        background-color: var(--success-light);
        border-left: 5px solid var(--success);
    }
    
    .status-box.warning {
        background-color: var(--warning-light);
        border-left: 5px solid var(--warning);
    }
    
    .status-box.info {
        background-color: var(--info-light);
        border-left: 5px solid var(--info);
    }
    
    .status-box.error {
        background-color: var(--primary-light);
        border-left: 5px solid var(--primary);
    }
    
    /* Tarjetas */
    .card {
        background-color: var(--white);
        border-radius: 0.75rem;
        padding: 1.2rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        height: 100%;
        transition: transform 0.2s ease;
        border: 1px solid #E0E4EB;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    
    .card .card-header {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        color: var(--secondary);
        border-bottom: 1px solid var(--light);
        padding-bottom: 0.5rem;
    }
    
    /* Botones */
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stButton>button:hover {
        filter: brightness(1.1);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .stButton.primary>button {
        background-color: var(--primary);
        color: var(--white);
    }
    
    .stButton.secondary>button {
        background-color: var(--secondary);
        color: var(--white);
    }
    
    .stButton.success>button {
        background-color: var(--success);
        color: var(--white);
    }
    
    /* Inputs */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea {
        border-radius: 0.5rem;
        border: 1px solid #E0E4EB;
        transition: all 0.2s ease;
    }
    
    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus {
        box-shadow: 0 0 0 2px var(--secondary-light);
        border-color: var(--secondary);
    }
    
    /* Selectores */
    .stSelectbox>div>div {
        border-radius: 0.5rem;
    }
    
    /* Tablas */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden !important;
        border: 1px solid #E0E4EB;
    }
    
    .dataframe th {
        background-color: var(--secondary-light);
        color: var(--secondary);
        font-weight: 600;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: #F8F9FA;
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .animate {
        animation: fadeIn 0.5s ease forwards;
    }
    
    /* Responsive */
    @media screen and (max-width: 768px) {
        h1.app-header {
            font-size: 1.8rem;
        }
        
        h2.section-header {
            font-size: 1.4rem;
        }
        
        .content-box {
            padding: 1rem;
        }
    }
</style>
"""

# Función para aplicar estilos a la aplicación
def apply_styles():
    import streamlit as st
    st.markdown(APP_STYLES, unsafe_allow_html=True)
    
    # Cargar fuente Inter de Google Fonts
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
