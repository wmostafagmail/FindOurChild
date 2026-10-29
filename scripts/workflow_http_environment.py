"""Short-lived loopback SQL transport for host-run synthetic fault tests only.

The application database retains its unpublished port and internal network.
No credentials or SQL are interpreted, recorded or passed to this relay.
"""

import json
import subprocess
import time
from contextlib import contextmanager
from uuid import uuid4

import psycopg

RELAY = """
import select,socket,socketserver
class Relay(socketserver.BaseRequestHandler):
 def handle(self):
  with socket.create_connection(('db',5432),timeout=5) as upstream:
   upstream.settimeout(None)
   streams=[self.request,upstream]
   while True:
    ready,_,_=select.select(streams,[],[],30)
    if not ready: return
    for source in ready:
     data=source.recv(65536)
     if not data: return
     (upstream if source is self.request else self.request).sendall(data)
class Server(socketserver.ThreadingTCPServer):
 allow_reuse_address=True
 daemon_threads=True
Server(('0.0.0.0',55439),Relay).serve_forever()
"""


@contextmanager
def private_sql_bridge():
    """Use only the existing image/network; always delete this run's own relay."""
    from scripts.dev import environment

    env = environment()
    assert env["FOC_DATA_CLASS"] == "synthetic"

    def docker(*args):
        return subprocess.run(
            ["docker", *args], check=True, capture_output=True, text=True, timeout=30
        ).stdout.strip()

    networks = json.loads(
        docker("inspect", "--format", "{{json .NetworkSettings.Networks}}", "foc-phase1a-db-1")
    )
    assert len(networks) == 1
    network = next(iter(networks))
    assert docker("network", "inspect", "--format", "{{.Internal}}", network) == "true"
    # Docker Desktop cannot publish from an internal-only network. Reuse the
    # application's existing edge network solely for loopback ingress; no
    # database service is moved and no external endpoint is contacted.
    application_networks = json.loads(
        docker("inspect", "--format", "{{json .NetworkSettings.Networks}}", "foc-phase1a-api-1")
    )
    edge = set(application_networks) - set(networks)
    assert network in application_networks and len(edge) == 1
    edge = next(iter(edge))
    assert docker("network", "inspect", "--format", "{{.Internal}}", edge) == "false"
    image = docker("inspect", "--format", "{{.Image}}", "foc-phase1a-worker-1")
    assert image.startswith("sha256:")
    name = "foc-synthetic-test-sql-" + uuid4().hex
    created = False
    try:
        docker(
            "create",
            "--name",
            name,
            "--network",
            network,
            "--publish",
            "127.0.0.1:55439:55439",
            "--memory",
            "64m",
            "--memory-swap",
            "64m",
            "--cpus",
            "1",
            "--pids-limit",
            "64",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--entrypoint",
            "python",
            image,
            "-c",
            RELAY,
        )
        created = True
        docker("network", "connect", edge, name)
        docker("start", name)
        deadline = time.monotonic() + 15
        while True:
            try:
                with psycopg.connect(env["FOC_DATABASE_ADMIN_URL"], connect_timeout=1) as conn:
                    assert conn.execute("SELECT data_class FROM platform.environment").fetchone() == (
                        "synthetic",
                    )
                break
            except psycopg.OperationalError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Private synthetic SQL test transport unavailable") from None
                time.sleep(0.1)
        yield
    finally:
        if created:
            docker("rm", "--force", name)
