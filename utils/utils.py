from threading import Lock



# TODO 定时清理长时间没有用的lock
class _NamedThreadLock:
   
    def __init__(self) -> None:
        self.get_lock_lock = Lock()
        self.locks = {}
    
    def get_lock(self,name):
        with self.get_lock_lock:
            if name not in self.locks:
                self.locks[name] = Lock()
            return self.locks[name]
            

    def __call__(self, name):
        return self.get_lock(name)


NamedThreadLock = _NamedThreadLock()



