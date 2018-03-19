from time import sleep
from daemonize import Daemonize
import app
import psycopg2
import requests
import json
import jinja2

pid = "/tmp/test.pid"


def main():
    while True:
        sleep(5)
        daemon = Daemonize(app="app.main()", pid=pid, action=main)
        daemon.start()
