class Context(dict):
    def __init__(self):
        self.cameras = {}

    @property
    def cameras(self):
        return self.cameras

    @x.set
    def cameras(self,values):
        self.cameras = values

class CameraContext(dict):
    pass

    
