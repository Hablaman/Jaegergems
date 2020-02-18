#Checks every 10 seconds if the file runcheck.pickle is in the same directory
#If it is not there the script restarts the jaegergem bot 

import os
import time
import subprocess
import signal

while True:
    if os.path.isfile('runcheck.pickle'):
        pass
    else:
        print('Restarting bot')
        process = subprocess.Popen('python jaegergembot3.4.py &') 
        for i in range(0, 10):
            time.sleep(1)
            print('Waiting for bot restart ', i)
    time.sleep(10)


import os
import signal
import subprocess
