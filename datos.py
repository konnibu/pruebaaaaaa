import requests
import pandas as pd
import streamlit as st
from io import BytesIO

def obtener_datos_paises():
    url = 'https://restcountries.com/v3.1/all'
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanza un error si la respuesta no es 200
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        st.error(f'Error al obtener datos: {e}')
        return []

def convertir_a_dataframe(paises):
    datos = []
    for pais in paises:
        datos.append({
            'Nombre Común': pais.get('name', {}).get('common', 'No disponible'),
            'Región Geográfica': pais.get('region', 'No disponible'),
            'Población Total': pais.get('population', 0),
            'Área en km²': pais.get('area', 0),
            'Número de Fronteras': len(pais.get('borders', [])),
            'Número de Idiomas Oficiales': len(pais.get('languages', {})) if pais.get('languages') else 0,
            'Número de Zonas Horarias': len(pais.get('timezones', []))
        })
    return pd.DataFrame(datos)

# Obtener y procesar datos
paises = obtener_datos_paises()
df = convertir_a_dataframe(paises)

# Título de la aplicación
st.title('Análisis de Datos de Países')

# Mostrar datos originales
if st.checkbox('Mostrar datos originales'):
    st.write(df)

# Selección de columna para estadísticas
columna_estadisticas = st.selectbox('Selecciona una columna para calcular estadísticas', df.columns[2:])
if columna_estadisticas:
    media = df[columna_estadisticas].mean()
    mediana = df[columna_estadisticas].median()
    desviacion_estandar = df[columna_estadisticas].std()

    st.write(f'Media: {media}')
    st.write(f'Mediana: {mediana}')
    st.write(f'Desviación Estándar: {desviacion_estandar}')

# Selección de columna para ordenar
columna_ordenar = st.selectbox('Selecciona una columna para ordenar', df.columns)
orden = st.radio('Selecciona el orden', ('Ascendente', 'Descendente'))

if columna_ordenar:
    df_ordenado = df.sort_values(by=columna_ordenar, ascending=(orden == 'Ascendente'))
    st.write(df_ordenado)

# Filtrar por población total
valor_filtro = st.slider('Selecciona un valor para filtrar la población total', 0, int(df['Población Total'].max()), 100000)
df_filtrado = df[df['Población Total'] >= valor_filtro]
st.write('Datos filtrados:')
st.write(df_filtrado)

# Función para descargar datos como Excel o CSV
def download_data(df_filtrado):
    # Descargar como CSV
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button('Descargar CSV', csv, 'datos_filtrados.csv', 'text/csv')

    # Descargar como Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Datos')
    excel_buffer.seek(0)
    st.download_button('Descargar Excel', excel_buffer, 'datos_filtrados.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Descargar datos filtrados
if st.button('Descargar datos filtrados'):
    download_data(df_filtrado)
