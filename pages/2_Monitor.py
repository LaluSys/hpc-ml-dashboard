import time

import streamlit as st

from hpc import slurm

st.set_page_config(page_title="Job Monitor", layout="wide")
st.title("Job Monitor")

if "ssh" not in st.session_state or not st.session_state["ssh"].is_alive():
    st.warning("Bitte zuerst verbinden (Startseite).")
    st.stop()

conn = st.session_state["ssh"]
username = st.session_state["username"]
workdir = st.session_state["workdir"]

col_refresh, col_interval, _ = st.columns([1, 1, 4])
with col_refresh:
    auto_refresh = st.toggle("Auto-Refresh", value=True)
with col_interval:
    interval = st.selectbox("Interval", [10, 30, 60], index=0, format_func=lambda x: f"{x}s")

placeholder = st.empty()

def render():
    with placeholder.container():
        try:
            df = slurm.list_jobs(conn, username)
        except Exception as e:
            st.error(f"squeue fehlgeschlagen: {e}")
            return

        if df.empty:
            st.info("Keine laufenden Jobs.")
        else:
            status_colors = {"RUNNING": "green", "PENDING": "orange", "FAILED": "red", "COMPLETED": "blue"}

            def color_status(val):
                color = status_colors.get(val, "gray")
                return f"color: {color}; font-weight: bold"

            st.dataframe(
                df.style.map(color_status, subset=["Status"]),
                hide_index=True,
                use_container_width=True,
            )

        st.divider()
        st.subheader("Log-Viewer")

        col1, col2 = st.columns([2, 1])
        with col1:
            job_id_input = st.text_input("Job-ID", placeholder="z.B. 12345")
        with col2:
            log_type = st.radio("Log-Typ", ["stdout (.out)", "stderr (.err)"], horizontal=True)

        col_view, col_cancel = st.columns([1, 1])
        with col_view:
            if st.button("Log laden", disabled=not job_id_input):
                with st.spinner("Lade Log..."):
                    if "stdout" in log_type:
                        log = slurm.get_log(conn, job_id_input, workdir)
                    else:
                        log = slurm.get_err(conn, job_id_input, workdir)
                    st.code(log, language=None)
        with col_cancel:
            if st.button("Job abbrechen", type="secondary", disabled=not job_id_input):
                if slurm.cancel(conn, job_id_input):
                    st.success(f"Job {job_id_input} abgebrochen.")
                else:
                    st.error("scancel fehlgeschlagen.")

render()

if auto_refresh:
    time.sleep(interval)
    st.rerun()
