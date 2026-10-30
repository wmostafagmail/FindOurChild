"""Real Linux PID-namespace/cgroup helpers, never neural execution."""

import os

import pytest

from tools.phase2e.demo_governance.isolation import run


def image():
    # Missing Linux runner is a failure, never skip/success.
    value = os.environ.get("FOC_GOVERNANCE_PROBE_IMAGE")
    assert value, "Required Linux source-only isolation harness not provisioned"
    return value


def test_dg_w01_docker_client_death_does_not_cancel_watchdog():
    r = run(image(), "sleep", lose_client=True)
    assert r["exit"] == 124 and r["elapsed"] < 15


def test_dg_w02_no_control_plane_dependency_after_admission():
    # Kill attached control client; supervisor timerfd and pidfd run entirely
    # inside namespace. There is no Docker/API call on its termination path.
    r = run(image(), "descendant", lose_client=True)
    assert r["exit"] == 124 and r["elapsed"] < 15


def test_dg_w03_supervisor_death_kills_namespace():
    r = run(image(), "descendant", kill_supervisor=True)
    assert r["exit"] != 0 and r["elapsed"] < 15


def test_dg_w04_independent_cpu_and_wall_limits():
    a = run(image(), "spin")
    b = run(image(), "sleep")
    assert a["exit"] in {128 + 24, 128 + 9} and b["exit"] == 124


def test_dg_w05_memory_exhaustion_fails_job():
    r = run(image(), "memory")
    assert r["exit"] in {71, 137} and r["elapsed"] < 15


def test_dg_w06_descendants_fd_output_and_watchdog_attack():
    assert run(image(), "descendant")["exit"] == 124
    assert run(image(), "fds")["exit"] == 72
    assert run(image(), "output")["exit"] in {73, 153}
    assert run(image(), "attack")["exit"] == 0
    assert run(image(), "pids")["exit"] == 74
    assert run(image(), "network")["exit"] == 0


def test_dg_w07_stable_container_identity_and_unknown_probe_denied():
    from tools.phase2e.demo_governance.records import Denied

    with pytest.raises(Denied):
        run("foreign-name", "sleep")
    with pytest.raises(Denied):
        run(image(), "../../arbitrary")
    assert run(image(), "ok")["exit"] == 0
