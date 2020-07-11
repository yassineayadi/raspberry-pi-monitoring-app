import psutil, subprocess, json 
from datetime import datetime
from pathlib import Path
import pandas as pd

def get_disk_usage():
    disk = psutil.disk_usage('/')
    # Divide from Bytes -> KB -> MB -> GB
    free = round(disk.free/1024.0/1024.0/1024.0,1)
    total = round(disk.total/1024.0/1024.0/1024.0,1)
    used = total - free

    timestamp = datetime.now()

    disk = {"timestamp": timestamp,
            "values":
                {"total": total,
                "used": used,
                "free": free
                }
            }

    return disk

def get_cpu_usage():
    timestamp = datetime.now()
    cpu_percent = psutil.cpu_percent()

    return (timestamp, cpu_percent)

def get_memory_usage():
    timestamp = datetime.now()
    memory = psutil.virtual_memory()
    # available = round(memory.available/1024.0/1024.0,0)
    # total = round(memory.total/1024.0/1024.0,0)
    total = round(memory.total/1024.0/1024.0,0)
    used = round(memory.used/1024.0/1024.0,0)
    available = round(memory.available/1024.0/1024.0,0)
    
    

    memory = {"timestamp": timestamp,
              "values":
                {"available": available,
                "used": used,
                "total": total
                }
             }

    return memory

def get_current_processes():
    # retrieves a dictionary of current processes with their pid 
    # and usage information
        
    procs = [p for p in psutil.process_iter(attrs=['pid','name','username','cwd','environ','create_time','terminal','cpu_percent','memory_percent'])]
    # procs = [p for p in psutil.process_iter()]
    
    # ENVIRON
    # not including 'environ' (environment), only provides environment variables accessible to the process

    # CWD
    # not including 'cwd', currently only access to root user
    # 'cwd': p.cwd(),

    # CPU_PERCENT
    # dividing the p.cpu_percent() by the psutil.cpu_count() to get the same behaviour as in windows task manager
    # otherwise can retrieve value > 100, when the application uses multiple threads

    process_dict = {p.pid: {'pid': p.pid, 'name':p.name(), 'username': p.username(), \
                     'create_time': datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S"), \
                     'run_time': convert_time_delta_to_string(datetime.now() - datetime.fromtimestamp(p.create_time())), \
                     
                     # rounded 4, to get the necessary precison (2) once rounded in the frontend as %.
                     'cpu_percent': round((p.cpu_percent()/psutil.cpu_count())/100,4), 'memory_percent': round(p.memory_percent()/100,4)} for p in procs}

    return process_dict

def convert_time_delta_to_string(timedelta):
    # total number of seconds
    s = timedelta.total_seconds()
    # hours
    hours = s // 3600 
    # remaining seconds
    s = s - (hours * 3600)
    # minutes
    minutes = s // 60
    # remaining seconds
    seconds = s - (minutes * 60)
    # total time
    return '{:02}h: {:02}m: {:02}s'.format(int(hours), int(minutes), int(seconds))

def get_pi_revisions():
    # gets relative path of parent folder
    path = str(Path.cwd().parent) + '/raspberry_pi_revision_codes.json'
    path = str(Path.cwd()) + '/raspberry_pi_revision_codes.json'
    # reads json file
    with open(path) as f:
        revision_json = json.load(f)

    return revision_json

def get_current_pi_revision():
    pi_revisions = get_pi_revisions()

    process =  subprocess.Popen("cat /proc/cpuinfo | grep 'Revision' | awk '{print $3}'", shell=True, stdout=subprocess.PIPE)
    
    # read process output
    process_output =  process.stdout.readlines()
    
    # decode and retrieve first entry
    current_revision = [rev.decode().strip() for rev in process_output][0]

    return pi_revisions[current_revision]

def create_system_table():
    df = pd.DataFrame.from_dict(get_current_processes(), orient='index')
    df.sort_values(by='memory_percent', ascending=False, inplace=True)
    df = df.head(20)
    return df

if __name__ == "__main__":
    pass
    # print(get_current_pi_revision())
    # p = current_processes()

    p = get_current_processes()
    df = pd.DataFrame.from_dict(p, orient='index')
    # df.set_index('pid', inplace=True)
    # print(generate_table(pd.DataFrame.from_dict(current_processes(), orient='index')))
    df.sort_values(by='memory_percent', ascending=False, inplace=True)
    print(df.head(20))