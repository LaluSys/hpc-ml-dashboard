import posixpath

import streamlit as st

from hpc import files

st.set_page_config(page_title="Dateien", layout="wide")
st.title("Dateien")

if "ssh" not in st.session_state or not st.session_state["ssh"].is_alive():
    st.warning("Bitte zuerst verbinden (Startseite).")
    st.stop()

conn = st.session_state["ssh"]
workdir = st.session_state["workdir"]

if "current_dir" not in st.session_state:
    st.session_state["current_dir"] = workdir

current_dir = st.session_state["current_dir"]

# Breadcrumb navigation
parts = current_dir.split("/")
breadcrumb_cols = st.columns(len(parts) + 1)
path_so_far = ""
for i, part in enumerate(parts):
    if not part:
        path_so_far = "/"
        continue
    path_so_far = posixpath.join(path_so_far, part)
    if breadcrumb_cols[i].button(part, key=f"bc_{i}"):
        st.session_state["current_dir"] = path_so_far
        st.rerun()

st.caption(f"Aktueller Pfad: `{current_dir}`")
st.divider()

# Directory listing
try:
    entries = files.list_dir(conn, current_dir)
except Exception as e:
    st.error(f"Verzeichnis nicht lesbar: {e}")
    if st.button("Zum Arbeitsverzeichnis"):
        st.session_state["current_dir"] = workdir
        st.rerun()
    st.stop()

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Inhalt")
    if not entries:
        st.info("Verzeichnis ist leer.")
    for entry in entries:
        icon = "" if entry["is_dir"] else ""
        size_str = f"{entry['size']:,} bytes" if not entry["is_dir"] else ""
        row_cols = st.columns([3, 2, 1, 1])
        row_cols[0].write(f"{icon} {entry['name']}")
        row_cols[1].caption(size_str)

        if entry["is_dir"]:
            if row_cols[2].button("Öffnen", key=f"open_{entry['name']}"):
                st.session_state["current_dir"] = posixpath.join(current_dir, entry["name"])
                st.rerun()
        else:
            if row_cols[2].button("Download", key=f"dl_{entry['name']}"):
                with st.spinner("Lade herunter..."):
                    data = files.download(conn, posixpath.join(current_dir, entry["name"]))
                st.download_button(
                    label=f"Speichern: {entry['name']}",
                    data=data,
                    file_name=entry["name"],
                    key=f"save_{entry['name']}",
                )
            if row_cols[3].button("Löschen", key=f"rm_{entry['name']}", type="secondary"):
                files.delete(conn, posixpath.join(current_dir, entry["name"]))
                st.rerun()

with col2:
    st.subheader("Upload")
    uploaded_file = st.file_uploader("Datei hochladen", label_visibility="collapsed")
    if uploaded_file:
        remote_path = posixpath.join(current_dir, uploaded_file.name)
        if st.button("Hochladen", type="primary"):
            with st.spinner("Hochladen..."):
                files.upload(conn, remote_path, uploaded_file.read())
            st.success(f"Hochgeladen: {uploaded_file.name}")
            st.rerun()

    st.subheader("Neuer Ordner")
    new_folder = st.text_input("Ordnername", label_visibility="collapsed", placeholder="ordner_name")
    if st.button("Erstellen") and new_folder:
        files.makedirs(conn, posixpath.join(current_dir, new_folder))
        st.rerun()
