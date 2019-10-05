class Sample(object):
    def __init__(self, subObject, u, v):
        self.subObject = subObject
        self.u = u
        self.v = v

        self.vec = self.subObject.valueAt(u, v)
        self.nvec = self.subObject.normalAt(u, v)
