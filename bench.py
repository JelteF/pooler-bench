#!/bin/env python3
import os
import subprocess
from contextlib import contextmanager
import sys
import shlex

import click


def eprint(*args, **kwargs):
    """eprint prints to stderr"""

    print(*args, file=sys.stderr, **kwargs)


def run(command, *args, check=True, shell=None, silent=False, **kwargs):
    """run runs the given command and prints it to stderr"""

    if shell is None:
        shell = isinstance(command, str)

    if not shell:
        command = list(map(str, command))

    if not silent:
        if shell:
            eprint(f"+ {command}")
        else:
            eprint(f"+ {shlex.join(command)}")
    if silent:
        kwargs.setdefault("stdout", subprocess.DEVNULL)
    return subprocess.run(command, *args, check=check, shell=shell, **kwargs)


def sudo(command, *args, **kwargs):
    """
    A version of run that prefixes the command with sudo when the process is
    not already run as root
    """
    effective_user_id = os.geteuid()
    if effective_user_id == 0:
        return run(command, *args, **kwargs)
    if isinstance(command, str):
        return run(f"sudo {command}", *args, **kwargs)
    else:
        return run(["sudo", *command])


def pipe(command, *args, shell=None, silent=False, stdin=subprocess.PIPE, **kwargs):
    if shell is None:
        shell = isinstance(command, str)

    if not shell:
        command = list(map(str, command))

    if not silent:
        if shell:
            eprint(f"+ {command}")
        else:
            eprint(f"+ {shlex.join(command)}")
    if silent:
        kwargs.setdefault("stdout", subprocess.DEVNULL)
    return subprocess.Popen(command, *args, shell=shell, stdin=stdin, **kwargs)


def capture(command, *args, strip=True, **kwargs):
    """runs the given command and returns its output as a string"""
    output = run(command, *args, stdout=subprocess.PIPE, text=True, **kwargs).stdout
    if strip:
        return output.strip()
    return output


@contextmanager
def add_latency(ports: list[int], latency: int):
    """Adds the given latency in milliseconds to the given ports on localhost"""
    if not latency or not ports:
        yield
        return
    # Add the all zeros priomap to prio so all regular traffic flows
    # through a single band. By default prio assigns traffic to different
    # band according to the DSCP value of the packet. This means that some
    # traffic that doesn't match your filter might end up in the same class
    # as the delayed traffic.
    # Source: https://stackoverflow.com/a/40203517/2570866
    sudo(
        "tc qdisc add dev lo root handle 1: prio bands 2 priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
    )

    sudo(f"tc qdisc add dev lo parent 1:2 handle 20: netem delay {latency}ms")
    for port in ports:
        sudo(
            f"tc filter add dev lo parent 1:0 protocol ip prio {port} u32 match ip dport {port} 0xffff flowid 1:2"
        )

    try:
        yield
    finally:
        for port in ports:
            sudo(f"tc filter del dev lo parent 1: prio {port}")
        sudo("tc qdisc del dev lo parent 1:2 handle 20:")
        sudo("tc qdisc del dev lo root")


@click.group()
def cli():
    pass


@cli.group("run")
def cli_run():
    pass


PORTS = {
    "pgbouncer": 5001,
    "odyssey": 5002,
    "pgcat": 5003,
    "supavisor": 5004,
}

POSTGRES_PORT = 9700


@cli.command()
@click.argument(
    "pooler", type=click.Choice(["pgbouncer", "odyssey", "pgcat", "supavisor"])
)
@click.option("--client", "-c", type=int, default=10)
@click.option("--jobs", "-j", type=int, default=10)
@click.option("--time", "-T", type=int, default=10)
@click.option(
    "--protocol",
    type=click.Choice(["prepared", "extended", "simple"]),
    default="prepared",
)
@click.option("--postgres-latency", is_flag=True)
@click.option("--pooler-latency", is_flag=True)
@click.option("--latency", type=int, default=1)
@click.option("--bench", default="pipeline", type=click.Choice(["pipeline", "large", "select-only", "tcpb"]))
@click.option("--large-size", type=int, default=10000)
def bench(
    pooler,
    client,
    jobs,
    time,
    protocol="prepared",
    postgres_latency=False,
    pooler_latency=False,
    latency=1,
    bench="pipeline",
    large_size=10000,
):
    os.environ["PGPASSWORD"] = "test"
    latency_ports = []
    if postgres_latency:
        latency_ports.append(POSTGRES_PORT)
    if pooler_latency:
        latency_ports.append(PORTS[pooler])
    large_string = "a" * large_size
    stdin = ''
    args = []
    if bench == "large":
        stdin = f"select '{large_size}'";
    elif bench == "select-only":
        args = ["--select-only"]
    elif bench != "tcpb":
        args = [f"--file={bench}.sql"]

    with add_latency(latency_ports, latency):
        run(
            [
                "pgbench",
                "--port",
                PORTS[pooler],
                "--username=postgres",
                "--progress=1",
                "--time",
                time,
                "--client",
                client,
                "--jobs",
                jobs,
                "--protocol",
                protocol,
                *args,
            ],
            input=stdin.encode(),
        )


@cli_run.command("pgbouncer")
@click.argument("index", type=int, default=1)
def run_pgbouncer(index):
    run(f"pgbouncer/pgbouncer configs/pgbouncer/{index}.ini")


@cli_run.command("odyssey")
def run_odyssey():
    run("odyssey/build/sources/odyssey configs/odyssey.conf")

@cli_run.command("pgcat")
def run_pgcat():
    run("pgcat/target/release/pgcat configs/pgcat.toml")

@cli_run.command("supavisor")
def run_supavisor():
    # run("odyssey/build/sources/odyssey configs/odyssey.conf")
    ...

@cli_run.command("postgres")
def run_postgres():
    run("tools/citus_dev/citus_dev make test --destroy --size 0 --no-lib --no-extension --init-with setup.sql")
    run("echo max_connections=1000 >> test/coordinator/postgresql.conf")
    run("tools/citus_dev/citus_dev restart test")
    run("pgbench -i -p 9700")




if __name__ == "__main__":
    cli()
