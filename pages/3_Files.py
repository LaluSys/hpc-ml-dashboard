import posixpath
from datetime import datetime

import streamlit as st

from hpc import files


def _fmt_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

st.set_page_config(page_title="Dateien & Datensätze", layout="wide")
st.title("📁 Dateien & Datensätze")

if "ssh" not in st.session_state or not st.session_state["ssh"].is_alive():
    st.warning("Bitte zuerst verbinden (Startseite).")
    st.stop()

conn = st.session_state["ssh"]
workdir = st.session_state["workdir"]
username = st.session_state["username"]

tab_browser, tab_upload, tab_download = st.tabs(["📂 Dateibrowser", "⬆️ Datensatz hochladen", "⬇️ Datensatz herunterladen"])


# ─── Tab 1: Dateibrowser ───────────────────────────────────────────────────
with tab_browser:
    if "current_dir" not in st.session_state:
        st.session_state["current_dir"] = workdir

    current_dir = st.session_state["current_dir"]

    # Breadcrumb
    parts = [p for p in current_dir.split("/") if p]
    bc_cols = st.columns(len(parts) + 2)
    bc_cols[0].button("/", key="bc_root", on_click=lambda: st.session_state.update(current_dir="/"))
    path_so_far = ""
    for i, part in enumerate(parts):
        path_so_far = "/" + "/".join(parts[: i + 1])
        captured = path_so_far
        if bc_cols[i + 1].button(part, key=f"bc_{i}"):
            st.session_state["current_dir"] = captured
            st.rerun()

    st.caption(f"`{current_dir}`")
    st.divider()

    try:
        entries = files.list_dir(conn, current_dir)
    except Exception as e:
        st.error(f"Verzeichnis nicht lesbar: {e}")
        if st.button("Zum Arbeitsverzeichnis"):
            st.session_state["current_dir"] = workdir
            st.rerun()
        st.stop()

    if not entries:
        st.info("Verzeichnis ist leer.")

    for entry in entries:
        icon = "📂" if entry["is_dir"] else "📄"
        size_str = _fmt_size(entry["size"]) if not entry["is_dir"] else ""
        cols = st.columns([3, 1, 1, 1])
        cols[0].write(f"{icon} {entry['name']}")
        cols[1].caption(size_str)

        if entry["is_dir"]:
            if cols[2].button("Öffnen", key=f"open_{entry['name']}"):
                st.session_state["current_dir"] = posixpath.join(current_dir, entry["name"])
                st.rerun()
        else:
            if cols[2].button("⬇️", key=f"dl_{entry['name']}", help="Herunterladen"):
                with st.spinner("Lade herunter..."):
                    data = files.download(conn, posixpath.join(current_dir, entry["name"]))
                st.download_button(
                    label=f"💾 {entry['name']}",
                    data=data,
                    file_name=entry["name"],
                    key=f"save_{entry['name']}",
                )
            if cols[3].button("🗑️", key=f"rm_{entry['name']}", help="Löschen"):
                files.delete(conn, posixpath.join(current_dir, entry["name"]))
                st.rerun()

    st.divider()
    col_up, col_mkdir = st.columns(2)
    with col_up:
        st.caption("Datei hochladen")
        uf = st.file_uploader("Datei", label_visibility="collapsed", key="browser_upload")
        if uf and st.button("Hochladen", key="browser_upload_btn", type="primary"):
            with st.spinner("Hochladen..."):
                files.upload(conn, posixpath.join(current_dir, uf.name), uf.read())
            st.success(f"✓ {uf.name}")
            st.rerun()
    with col_mkdir:
        st.caption("Neuer Ordner")
        new_folder = st.text_input("Name", label_visibility="collapsed", placeholder="ordner_name", key="mkdir_input")
        if st.button("Erstellen", key="mkdir_btn") and new_folder:
            files.makedirs(conn, posixpath.join(current_dir, new_folder))
            st.rerun()


# ─── Tab 2: Datensatz hochladen ────────────────────────────────────────────
with tab_upload:
    st.subheader("Datensatz auf den Cluster hochladen")

    col_l, col_r = st.columns([1, 1])

    with col_l:
        upload_dest = st.text_input(
            "Zielverzeichnis auf Cluster",
            value=posixpath.join(workdir, "data"),
            help="Wird automatisch angelegt falls nicht vorhanden.",
        )
        uploaded_files = st.file_uploader(
            "Dateien auswählen",
            accept_multiple_files=True,
            help="Mehrere Dateien gleichzeitig möglich (CSV, JSON, ZIP, Parquet, HDF5, …)",
        )

    with col_r:
        st.info(
            "**Tipps für große Datensätze (>500 MB)**\n\n"
            "Streamlit lädt Dateien vollständig in den Browser-Speicher — "
            "für sehr große Datensätze ist direktes `rsync` schneller:\n\n"
            "```bash\nrsync -avz --progress mein_datensatz/ \\\n"
            f"  {username}@its-cs1.its.uni-kassel.de:{posixpath.join(workdir, 'data')}/\n```\n\n"
            "Oder `scp`:\n"
            "```bash\nscp -r mein_datensatz/ \\\n"
            f"  {username}@its-cs1.its.uni-kassel.de:{posixpath.join(workdir, 'data')}/\n```"
        )

    if uploaded_files:
        st.write(f"**{len(uploaded_files)} Datei(en) ausgewählt:**")
        total_size = sum(f.size for f in uploaded_files)
        for f in uploaded_files:
            st.caption(f"• {f.name} ({_fmt_size(f.size)})")
        st.caption(f"Gesamt: {_fmt_size(total_size)}")

        if st.button("Alle hochladen", type="primary"):
            conn.run(f"mkdir -p {upload_dest}")
            progress = st.progress(0, text="Hochladen...")
            status = st.empty()
            errors = []
            for i, uf in enumerate(uploaded_files):
                status.caption(f"Lade hoch: {uf.name}")
                try:
                    files.upload(conn, posixpath.join(upload_dest, uf.name), uf.read())
                except Exception as e:
                    errors.append(f"{uf.name}: {e}")
                progress.progress((i + 1) / len(uploaded_files), text=f"{i+1}/{len(uploaded_files)}")
            progress.empty()
            status.empty()
            if errors:
                st.error("Fehler bei:\n" + "\n".join(errors))
            else:
                st.success(f"✓ {len(uploaded_files)} Datei(en) hochgeladen nach `{upload_dest}`")

    st.divider()
    st.subheader("ZIP-Archiv hochladen & entpacken")
    st.caption("Ideal für viele kleine Dateien (z.B. Bild-Datensätze)")
    col_z1, col_z2 = st.columns([1, 1])
    with col_z1:
        zip_dest = st.text_input(
            "Zielverzeichnis",
            value=posixpath.join(workdir, "data"),
            key="zip_dest",
        )
        zip_file = st.file_uploader("ZIP-Datei auswählen", type=["zip"], key="zip_upload")
    with col_z2:
        st.write("")
        st.write("")
        if zip_file:
            st.info(f"Datei: **{zip_file.name}** ({_fmt_size(zip_file.size)})\nWird nach dem Upload automatisch entpackt.")

    if zip_file and st.button("Hochladen & Entpacken", type="primary"):
        conn.run(f"mkdir -p {zip_dest}")
        remote_zip = posixpath.join(zip_dest, zip_file.name)
        with st.spinner(f"Lade {zip_file.name} hoch..."):
            files.upload(conn, remote_zip, zip_file.read())
        with st.spinner("Entpacke..."):
            out, err, code = conn.run(f"cd {zip_dest} && unzip -o {zip_file.name} && rm {zip_file.name}")
        if code == 0:
            st.success(f"✓ Entpackt nach `{zip_dest}`")
        else:
            st.error(f"Fehler beim Entpacken: {err}")


# ─── Tab 3: Datensatz herunterladen ────────────────────────────────────────
with tab_download:
    st.subheader("Datensatz vom Cluster herunterladen")

    col_l, col_r = st.columns([1, 1])
    with col_l:
        dl_path = st.text_input(
            "Pfad auf Cluster (Datei oder Verzeichnis)",
            value=posixpath.join(workdir, "data"),
            help="Verzeichnisse werden automatisch als .tar.gz gepackt.",
        )

    with col_r:
        st.info(
            "**Für große Datensätze direkt per rsync:**\n\n"
            "```bash\nrsync -avz --progress \\\n"
            f"  {username}@its-cs1.its.uni-kassel.de:{posixpath.join(workdir, 'data')}/ \\\n"
            "  ./mein_lokaler_ordner/\n```"
        )

    if st.button("Herunterladen", type="primary"):
        with st.spinner("Prüfe Pfad..."):
            out, _, _ = conn.run(f"test -d {dl_path} && echo dir || echo file")
            is_dir = out.strip() == "dir"

        if is_dir:
            archive_name = posixpath.basename(dl_path.rstrip("/")) + f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            archive_path = f"/tmp/{archive_name}"
            with st.spinner(f"Packe Verzeichnis als {archive_name}..."):
                parent = posixpath.dirname(dl_path.rstrip("/"))
                name = posixpath.basename(dl_path.rstrip("/"))
                _, err, code = conn.run(f"tar -czf {archive_path} -C {parent} {name}")
            if code != 0:
                st.error(f"tar fehlgeschlagen: {err}")
                st.stop()
            with st.spinner("Lade herunter..."):
                data = files.download(conn, archive_path)
            conn.run(f"rm {archive_path}")
            st.download_button(f"💾 {archive_name}", data=data, file_name=archive_name)
        else:
            fname = posixpath.basename(dl_path)
            with st.spinner(f"Lade {fname} herunter..."):
                data = files.download(conn, dl_path)
            st.download_button(f"💾 {fname}", data=data, file_name=fname)
