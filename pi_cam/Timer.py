from time import time

class Timer:
    def __init__(self,names):
        self.names = names
        self.t = [0]*(len(names)+1)

    def reset(self):
        self.i = 1
        self.t[0] = time()

    def tick(self):
        self.t[self.i] = time()
        self.i+=1

    def __repr__(self):
        res = '-------------\n'
        for i in range(len(self.names)):
            res += '{}: {}ms\n'.format(
                self.names[i],
                1000*(self.t[i+1] - self.t[i]))
        res += 'Total: {}ms'.format(1000*(self.t[-1] - self.t[0]))
        return res