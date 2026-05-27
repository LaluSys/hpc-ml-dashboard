import paramiko


class SSHConnection:
    def __init__(self, hostname: str, username: str, password: str, port: int = 22):
        self.hostname = hostname
        self.username = username
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port,
            timeout=10,
            allow_agent=True,
            look_for_keys=True,
        )

    def run(self, cmd: str) -> tuple[str, str, int]:
        """Execute command, return (stdout, stderr, exit_code)."""
        stdin, stdout, stderr = self._client.exec_command(cmd, timeout=30)
        exit_code = stdout.channel.recv_exit_status()
        return stdout.read().decode(), stderr.read().decode(), exit_code

    def get_sftp(self) -> paramiko.SFTPClient:
        return self._client.open_sftp()

    def is_alive(self) -> bool:
        try:
            transport = self._client.get_transport()
            return transport is not None and transport.is_active()
        except Exception:
            return False

    def close(self):
        self._client.close()
