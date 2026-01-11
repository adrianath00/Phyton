<<<<<<< HEAD
# Phyton
echo "# Phyton" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/adrianath00/Phyton.git
git push -u origin main

=======
# PROYECTO_ETL_GANG_FUENLA — DevOps / Automatización (Semana 2)

## Objetivo (rol DevOps)
Preparar la base del pipeline ETL: orquestador único, logging, estructura reproducible y carga automática a BD. El código incluye la lógica básica de limpieza y anonimización para Clientes y Tarjetas.

## Estructura
data/
source/ # ficheros originales (Clientes-YYYY-MM-DD.csv, Tarjetas-YYYY-MM-DD.csv)
output/ # ficheros *.cleaned.csv (generados por ETL)
errors/ # filas rechazadas
logs/
src/utils/logger.py
etl_logic.py
db_handler.py
run_pipeline.py

## Requisitos
- Python 3.8+
- pip

## Instalación rápida
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# editar .env para cambiar SALT y DATABASE_URL si se quiere
>>>>>>> 4efe45c (Proyecto ETL Fuenlabrada - pipeline completo)
