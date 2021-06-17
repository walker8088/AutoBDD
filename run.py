
import os
import datetime
import traceback
import win32api

if __name__ == "__main__":
    curr_dir = os.path.dirname(__file__)
    print(curr_dir)
    if curr_dir:
        os.chdir(curr_dir)
    try:
        from autobdd.app import run
        run()
    except Exception as e:
        #log_file = f'exception_{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log' 
        #with open(log_file, 'w') as f:
        #    f.write(str(e))
        tb = traceback.format_exc()    
        win32api.MessageBox(0, tb)