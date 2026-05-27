import posixpath
from pathlib import Path

import streamlit as st
from jinja2 import Environment, FileSystemLoader

from hpc import slurm

st.set_page_config(page_title="Job einreichen", layout="wide")
st.title("Job einreichen")

if "ssh" not in st.session_state or not st.session_state["ssh"].is_alive():
    st.warning("Bitte zuerst verbinden (Startseite).")
    st.stop()

conn = st.session_state["ssh"]
cfg = st.session_state["cfg"]
workdir = st.session_state["workdir"]

# Load templates
templates_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
available_templates = [t.stem for t in templates_dir.glob("*.sh")]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Ressourcen")
    job_name = st.text_input("Job-Name", value="ml_train")
    template_name = st.selectbox("Job-Template", available_templates)

    try:
        df_sinfo = slurm.sinfo_summary(conn)
        partitions = df_sinfo["Partition"].tolist() if not df_sinfo.empty else ["pub23", "pub23gpu", "pub12"]
    except Exception:
        partitions = ["pub23", "pub23gpu", "pub12"]

    default_partition = cfg["defaults"].get("partition", "pub23")
    partition_idx = partitions.index(default_partition) if default_partition in partitions else 0
    partition = st.selectbox("Partition", partitions, index=partition_idx)
    time_limit = st.text_input("Zeitlimit (HH:MM:SS)", value=cfg["defaults"].get("time", "02:00:00"))
    mem = st.text_input("RAM", value=cfg["defaults"].get("mem", "16G"))
    cpus = st.number_input("CPUs", min_value=1, max_value=48, value=cfg["defaults"].get("cpus", 4))

    extra_modules = st.multiselect(
        "Zusätzliche Module",
        ["nvidia-hpc-sdk/25.1/cuda-12.6", "gcc/14.2.0", "openmpi/5.0.8/gcc-14.2.0"],
        default=["nvidia-hpc-sdk/25.1/cuda-12.6"] if "gpu" in partition else [],
    )

with col2:
    st.subheader("Script")
    script_source = st.radio("Script-Quelle", ["Pfad auf Cluster", "Lokal hochladen"])

    script_path_remote = ""
    script_args = ""

    if script_source == "Pfad auf Cluster":
        script_path_remote = st.text_input(
            "Script-Pfad auf Cluster",
            value=posixpath.join(workdir, "train.py"),
            placeholder="~/ml-jobs/train.py",
        )
        script_args = st.text_input("Argumente", placeholder="--epochs 10 --lr 0.001")
    else:
        uploaded = st.file_uploader("Python-Script", type=["py", "sh"])
        if uploaded:
            remote_scripts_dir = posixpath.join(workdir, "scripts")
            script_path_remote = posixpath.join(remote_scripts_dir, uploaded.name)
            script_args = st.text_input("Argumente", placeholder="--epochs 10 --lr 0.001")
            st.caption(f"Wird hochgeladen nach: `{script_path_remote}`")

    use_venv = st.checkbox("User-venv aktivieren (~/.ml-venv)", value=True)

# Preview
with st.expander("Script-Vorschau"):
    modules = cfg["defaults"].get("modules", ["python/3.13.0/gcc-14.2.0"]) + extra_modules
    template = jinja_env.get_template(f"{template_name}.sh")
    preview = template.render(
        job_name=job_name,
        partition=partition,
        time=time_limit,
        mem=mem,
        cpus=cpus,
        workdir=workdir,
        modules=modules,
        script=script_path_remote or "~/ml-jobs/train.py",
        args=script_args,
        use_venv=use_venv,
    )
    st.code(preview, language="bash")

st.divider()

if st.button("Job einreichen", type="primary", disabled=not script_path_remote):
    if script_source == "Lokal hochladen" and uploaded:
        from hpc import files
        sftp = conn.get_sftp()
        try:
            sftp.mkdir(posixpath.join(workdir, "scripts"))
        except OSError:
            pass
        files.upload(conn, script_path_remote, uploaded.read())

    modules = cfg["defaults"].get("modules", ["python/3.13.0/gcc-14.2.0"]) + extra_modules
    script_content = template.render(
        job_name=job_name,
        partition=partition,
        time=time_limit,
        mem=mem,
        cpus=cpus,
        workdir=workdir,
        modules=modules,
        script=script_path_remote,
        args=script_args,
        use_venv=use_venv,
    )

    with st.spinner("Reiche Job ein..."):
        try:
            job_id = slurm.submit(conn, script_content, job_name, workdir)
            st.success(f"Job eingereicht! Job-ID: **{job_id}**")
            st.info("Wechsle zu 'Jobs überwachen' um den Status zu sehen.")
        except Exception as e:
            st.error(f"Fehler: {e}")
