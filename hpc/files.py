import io
import posixpath
import stat

from .connection import SSHConnection


def list_dir(conn: SSHConnection, path: str) -> list[dict]:
    """List directory contents via SFTP. Returns list of {name, size, is_dir, mtime}."""
    sftp = conn.get_sftp()
    entries = []
    for attr in sftp.listdir_attr(path):
        entries.append({
            "name": attr.filename,
            "size": attr.st_size,
            "is_dir": stat.S_ISDIR(attr.st_mode),
            "mtime": attr.st_mtime,
        })
    return sorted(entries, key=lambda x: (not x["is_dir"], x["name"].lower()))


def upload(conn: SSHConnection, remote_path: str, data: bytes) -> None:
    sftp = conn.get_sftp()
    with sftp.open(remote_path, "wb") as f:
        f.write(data)


def download(conn: SSHConnection, remote_path: str) -> bytes:
    sftp = conn.get_sftp()
    buf = io.BytesIO()
    sftp.getfo(remote_path, buf)
    return buf.getvalue()


def makedirs(conn: SSHConnection, path: str) -> None:
    sftp = conn.get_sftp()
    parts = path.split("/")
    current = ""
    for part in parts:
        if not part:
            current = "/"
            continue
        current = posixpath.join(current, part)
        try:
            sftp.mkdir(current)
        except OSError:
            pass


def delete(conn: SSHConnection, remote_path: str) -> None:
    sftp = conn.get_sftp()
    sftp.remove(remote_path)
