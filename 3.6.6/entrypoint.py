import subprocess
import glob
import os

HOME_SITE="/home/site/wwwroot"
DEFAULT_SITE="/opt/defaultsite"
STARTUP_COMMAND_FILE="/opt/startup/startupCommand"
APPSVC_VIRTUAL_ENV="antenv"

# Temp patch. Remove when Kudu script is available.
os.environ["PYTHONPATH"] = HOME_SITE + "/antenv/lib/python3.6/site-packages"

def subprocess_cmd(command):
    print ('executing:')
    print (command)

    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print (proc_stdout.decode("utf-8"))

## Check for custom startup command
def custom_check():
    with open(STARTUP_COMMAND_FILE, 'r') as myfile:
          startupScript = myfile.read()
          if not startupScript:
              return None
          else:
              return startupScript

## Django check: If 'wsgi.py' is provided, identify as Django. 
def check_django():
    with os.scandir(HOME_SITE) as siteRoot:
        for entry in siteRoot:
            if not entry.name.startswith(APPSVC_VIRTUAL_ENV) and entry.is_dir():
                print(entry.name)
                with os.scandir(HOME_SITE + '/'+ entry.name) as subFolder:
                    for subEntry in subFolder:
                        if subEntry.name == 'wsgi.py' and subEntry.is_file():
                            return entry.name + '.wsgi'
    return None

## Flask check: If 'application.py' is provided or a .py module is present, identify as Flask.
def check_flask():
    
    py_modules = glob.glob(HOME_SITE+'/*.py')
    if len(py_modules) == 0:
        return None
    for module in py_modules: 
        if module[-14:] == 'application.py':
            print ('found flask app')
            return 'application:app'

def start_server():
    
    cmd = custom_check()
    if cmd is not None: 
        subprocess_cmd('. antenv/bin/activate')
        subprocess_cmd(
                'GUNICORN_CMD_ARGS="--bind=0.0.0.0" gunicorn ' + cmd
               )

    cmd = check_django()
    if cmd is not None:
        subprocess_cmd('. antenv/bin/activate')
        subprocess_cmd(
                'GUNICORN_CMD_ARGS="--bind=0.0.0.0" gunicorn ' + cmd
               )

    cmd = check_flask()
    if cmd is not None:
        subprocess_cmd('. antenv/bin/activate')
        subprocess_cmd(
                'GUNICORN_CMD_ARGS="--bind=0.0.0.0" gunicorn ' + cmd
               )
    else:          
        print('starting default app')
        subprocess_cmd(
              'GUNICORN_CMD_ARGS="--bind=0.0.0.0 --chdir /opt/defaultsite" gunicorn application:app'
              )    

subprocess_cmd('python --version')
subprocess_cmd('pip --version')
start_server()

