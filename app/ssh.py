#!/usr/bin/env python3

from fabric import Connection
from invoke import UnexpectedExit
from app.exceptions import ServerConnectionError
from paramiko.ssh_exception import NoValidConnectionsError, SSHException
import datetime
import yaml
from pathlib import Path

def load_config(filename):

    script_dir = Path(__file__).parent

    config_path = script_dir / filename
    config_path = config_path.resolve()

    try:
        with open(config_path, "r") as fd:
            return yaml.safe_load(fd)
    except FileNotFoundError:
        raise

def get_date(date):

    date_ajd = datetime.datetime.today()
    date_string = f"{date[0]} {date[1]} {date[2]} {date_ajd.year}"
    d = datetime.datetime.strptime(date_string,'%b %d %H:%M:%S %Y')
    if d > date_ajd:
        d = datetime.datetime(d.year-1,d.month,d.day,d.hour,d.minute,d.second)
    return d

def get_log_date(log):
    return log["date"]

def get_log(servers):

    logs = []
    
    config = load_config("config.yaml")

    for ip in servers:

        try:
            import os
            user = config["user"]
            ssh_file = config["ssh_file"]
            cnx = Connection(host=ip, user=user,
                             connect_timeout=7,
                             connect_kwargs={"key_filename":f"/home/{os.environ.get("USER")}/.ssh/{ssh_file}"})
            lines = cnx.run("sudo tac /var/log/syslog",hide=True)
        except (TimeoutError, NoValidConnectionsError, SSHException, UnexpectedExit) as e:
            raise ServerConnectionError(ip, e)
            
        lines = lines.stdout.strip().splitlines()
        for line in lines:
            line = line.split(None,4)
            date = get_date(line[:3])
            dico = {"date":date,"host":line[3],"message":line[4]}
            logs.append(dico)

    #Si y'a un seul serveur c'est déjà trié dans l'ordre décroissant grâce à la commande tac
    if len(servers) > 1:
        logs.sort(key=get_log_date, reverse=True)

    return logs
