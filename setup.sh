#!/bin/bash

echo "==================================================="
echo " Instalación de la Plataforma Inteligente de Datos"
echo "==================================================="
echo ""

echo "Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "Configuración de claves API..."
echo ""
echo "Ingresa tu clave API de OpenAI (deja en blanco si no tienes):"
read openai_key

echo "Ingresa tu clave API de Redpill.io (deja en blanco si no tienes):"
read redpill_key

echo ""
echo "Creando directorio de configuración..."
mkdir -p .streamlit

echo ""
echo "Creando archivo de secretos..."
cat > .streamlit/secrets.toml << EOL
[openai]
api_key = "${openai_key}"

[redpill]
api_key = "${redpill_key}"
api_url = "https://api.redpill.ai/v1/chat/completions"
EOL

echo ""
echo "Configuración completada. Para iniciar la aplicación, ejecuta:"
echo "streamlit run main.py"
echo ""
echo "Presiona Enter para salir..."
read
