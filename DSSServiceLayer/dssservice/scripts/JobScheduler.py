
import schedule
import time, threading





#========== == == == == == Threading===



def worker():
    print(threading.currentThread().getName(), 'Starting')
    #time.sleep(2)
    print(threading.currentThread().getName(), 'Exiting')

def my_service():
    print
    threading.currentThread().getName(), 'Starting'
    time.sleep(3)
    print
    threading.currentThread().getName(), 'Exiting'



def job():
    print("I'm working...")
    actThreadCount=threading.activeCount()
    print( 'active thread count ' + str(actThreadCount))









def startScheduler(seconds):

    schedule.every(seconds).seconds .do(job)
    #schedule.every().hour.do(job)
    #schedule.every().day.at("10:30").do(job)

    while 1:
        schedule.run_pending()
        #time.sleep(2)

