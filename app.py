import streamlit as st
import os
import json
import uuid
import datetime

DATA_FILE = "exhibitions.json"
MEDIA_DIR = "media"

os.makedirs(MEDIA_DIR, exist_ok=True)

def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_db(db):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def save_uploaded_file(uploaded_file, prefix):
    ext = os.path.splitext(uploaded_file.name)[1] or ""
    filename = f"{prefix}_{uuid.uuid4().hex}{ext}"
    path = os.path.join(MEDIA_DIR, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.read())
    return path

# Load existing data
db = load_db()

st.set_page_config(page_title="Exposiciones con audio-guía", layout="centered")
st.title("📚 Exposiciones — Audio guías")

# Sidebar: formulario para agregar
st.sidebar.header("➕ Agregar exposición")
title = st.sidebar.text_input("Título")
desc = st.sidebar.text_area("Descripción", height=140)

# 👇 Categorías predefinidas
categories = ["Cuadros", "Obras de teatro", "Espacio", "Otra"]
category = st.sidebar.selectbox("Categoría", categories)

image_up = st.sidebar.file_uploader("Imagen (opcional)", type=["png","jpg","jpeg"])
audio_up = st.sidebar.file_uploader("Audio guía (mp3, wav, ogg)", type=["mp3","wav","ogg"])

if st.sidebar.button("Guardar exposición"):
    if not title.strip():
        st.sidebar.error("El título es obligatorio.")
    elif audio_up is None:
        st.sidebar.error("La audio guía es obligatoria.")
    else:
        image_path = None
        if image_up:
            image_path = save_uploaded_file(image_up, "img")
        audio_path = save_uploaded_file(audio_up, "audio")
        item = {
            "id": uuid.uuid4().hex,
            "title": title.strip(),
            "description": desc.strip(),
            "category": category,   # 👈 guardamos la categoría
            "image": image_path,
            "audio": audio_path,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        db.append(item)
        save_db(db)
        st.sidebar.success("¡Exposición guardada!")

st.markdown("---")
st.header("Lista de exposiciones")

# 👇 Selector de categoría para filtrar
if db:
    all_categories = ["Todas"] + sorted({i["category"] for i in db})
    selected_cat = st.selectbox("Filtrar por categoría", all_categories)
else:
    selected_cat = "Todas"

# filtramos los datos
if selected_cat != "Todas":
    filtered = [i for i in db if i["category"] == selected_cat]
else:
    filtered = db

if not filtered:
    st.info("No hay exposiciones en esta categoría.")
else:
    for item in sorted(filtered, key=lambda x: x["created_at"], reverse=True):
        st.subheader(f"{item['title']} ({item['category']})")
        if item.get("image"):
            try:
                st.image(item["image"], use_container_width=True)
            except Exception:
                st.write("Imagen (no disponible).")
        if item.get("description"):
            st.write(item["description"])
        if item.get("audio"):
            try:
                with open(item["audio"], "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes)
            except Exception:
                st.warning("No se puede reproducir la audio-guía.")
        st.markdown("---")
