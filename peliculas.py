import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# iniciar firebase
@st.cache_resource
def inicia_firestore():
    if not firebase_admin._apps:
        credenciales = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(credenciales)
    return firestore.client()

db = inicia_firestore()


# cargar datos al dataframe

@st.cache_data
def cargar_movies_desde_firestore():
    peliculas = db.collection("movies").stream()
    data = []

    for pelicula in peliculas:
        fila = pelicula.to_dict()
        fila["id"] = pelicula.id
        data.append(fila)

    return pd.DataFrame(data)

df_movies = cargar_movies_desde_firestore()

# función para filtrar por director

def filtrar_por_director(df, director):
    return df[df["director"] == director]


# dashboard

st.title("Dashboard de Películas")
st.header("Catálogo de Películas")

st.write(f"Total de películas cargadas: {len(df_movies)}")


# sidebar 

st.sidebar.header("Opciones")

# checkbox 
mostrar_todas = st.sidebar.checkbox(
    "Mostrar todas las películas",
    value=True
)

# buscar por titulo
st.sidebar.subheader("Búsqueda por título")

titulo_busqueda = st.sidebar.text_input(
    "Buscar película por título"
)

boton_buscar_titulo = st.sidebar.button(
    "Buscar por título"
)

# filtrar director
st.sidebar.subheader("Filtro por director")

lista_directores = sorted(
    df_movies["director"].dropna().unique().tolist()
)

director_seleccionado = st.sidebar.selectbox(
    "Selecciona un director",
    lista_directores
)

boton_filtrar_director = st.sidebar.button(
    "Filtrar por director"
)


# formulario de registro nueva pelicula

st.sidebar.subheader("Agregar nueva película")

with st.sidebar.form("form_nueva_pelicula", clear_on_submit=True):
    nuevo_titulo = st.text_input("Título")
    nuevo_director = st.text_input("Director")
    nuevo_genero = st.text_input("Género")
    nueva_compania = st.text_input("Compañía")

    boton_guardar = st.form_submit_button("Guardar Pelicula")

    if boton_guardar:
        if (
            nuevo_titulo.strip() == ""
            or nuevo_director.strip() == ""
            or nuevo_genero.strip() == ""
            or nueva_compania.strip() == ""
        ):
            st.warning("Todos los campos son obligatorios")
        else:
            nueva_pelicula = {
                "name": nuevo_titulo,
                "director": nuevo_director,
                "genre": nuevo_genero,
                "company": nueva_compania
            }

            db.collection("movies").add(nueva_pelicula)

            st.cache_data.clear()

            st.success("Filme agregado correctamente")

df_resultado = df_movies

# filtro por titulo
if boton_buscar_titulo and titulo_busqueda.strip() != "":
    df_resultado = df_movies[
        df_movies["name"].str.contains(
            titulo_busqueda,
            case=False,
            na=False
        )
    ]
    st.subheader(f"Resultados para el título: '{titulo_busqueda}'")

# filtro por director
elif boton_filtrar_director:
    df_resultado = filtrar_por_director(
        df_movies,
        director_seleccionado
    )
    st.subheader(f"Películas dirigidas por: {director_seleccionado}")

elif mostrar_todas:
    st.subheader("Listado completo de películas")


st.write(f"Total de filmes encontrados: {len(df_resultado)}")

if df_resultado.empty:
    st.warning("No se encontraron películas con ese criterio")
else:
    st.dataframe(df_resultado, use_container_width=True)
