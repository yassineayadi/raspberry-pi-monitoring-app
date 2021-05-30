import psutil, subprocess, json
from datetime import datetime
from pathlib import Path
import pandas as pd
import os

from app.helpers import convert_time_delta_to_string


# TO DO:
# Create an Object Model for the raspberry Pi

class RaspberryPi():

    @staticmethod
    def get_pi_revisions() -> dict:
        # gets relative path of current folder
        path = str(Path.cwd()) + '/app/assets/raspberry_pi_revision_codes.json'
        # reads json file
        with open(path) as f:
            revision = json.load(f)

        return revision

    @staticmethod
    def get_current_pi_revision() -> str:
        pi_revisions = RaspberryPi.get_pi_revisions()

        process = subprocess.Popen("cat /proc/cpuinfo | grep 'Revision' | awk '{print $3}'", shell=True,
                                   stdout=subprocess.PIPE)

        # read process output
        process_output = process.stdout.readlines()

        # decode and retrieve first entry
        current_revision = [rev.decode().strip() for rev in process_output][0]

        return pi_revisions[current_revision]

    def get_disk_usage(self) -> dict:
        disk = psutil.disk_usage('/')
        # Divide from Bytes -> KB -> MB -> GB
        free = round(disk.free / 1024.0 / 1024.0 / 1024.0, 1)
        total = round(disk.total / 1024.0 / 1024.0 / 1024.0, 1)
        used = total - free

        timestamp = datetime.now()

        disk = {"timestamp": timestamp,
                "values": {"total": total,
                           "used": used,
                           "free": free
                           }
                }

        return disk

    def get_cpu_usage(self) -> tuple:
        timestamp = datetime.now()
        cpu_percent = psutil.cpu_percent()

        return (timestamp, cpu_percent)

    def get_memory_usage(self) -> dict:
        timestamp = datetime.now()
        memory = psutil.virtual_memory()
        # available = round(memory.available/1024.0/1024.0,0)
        # total = round(memory.total/1024.0/1024.0,0)
        total = round(memory.total / 1024.0 / 1024.0, 0)
        used = round(memory.used / 1024.0 / 1024.0, 0)
        available = round(memory.available / 1024.0 / 1024.0, 0)

        memory = {"timestamp": timestamp,
                  "values": {"available": available,
                             "used": used,
                             "total": total
                             }
                  }

        return memory

    def get_current_processes(self) -> dict:
        # retrieves a dictionary of current processes with their pid and usage information

        # ENVIRON
        # not including 'environ' (environment), only provides environment variables accessible to the process

        # CWD
        # not including 'cwd', currently only access to root user
        # 'cwd': p.cwd(),

        # CPU_PERCENT
        # dividing the p.cpu_percent() by the psutil.cpu_count() to get the same behaviour as in windows task manager
        # otherwise can retrieve value > 100, when the application uses multiple threads

        procs = [p for p in psutil.process_iter(
            attrs=['pid', 'name', 'username', 'cwd', 'environ', 'create_time', 'terminal', 'cpu_percent',
                   'memory_percent'])]

        processes = {p.pid: {'pid': p.pid, 'name': p.name(), 'username': p.username(),
                             'create_time': datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
                             'run_time': convert_time_delta_to_string(
                                 datetime.now() - datetime.fromtimestamp(p.create_time())),
                             # rounded 4, to get the necessary precison (2) once rounded in the frontend as %.
                             'cpu_percent': round((p.cpu_percent() / psutil.cpu_count()) / 100, 4),
                             'memory_percent': round(p.memory_percent() / 100, 4)}
                     for p in procs}

        return processes

    def __init__(self):
        self.revision = RaspberryPi.get_current_pi_revision()


if __name__ == "__main__":
    pass
