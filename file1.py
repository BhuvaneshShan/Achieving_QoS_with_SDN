from threading import Thread
def runfile():
    execfile("client.py")

   

if __name__ == "__main__":
    
    thread = Thread(target = runfile, args = [])
    thread.start()
    thread.join()
    print 'Finished'


