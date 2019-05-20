class TPoint (object):
    """
    Class represents single point on two-dimensional plane.
    """
    def __init__ (self, x = 0, y = 0):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if(self.x == other.x and self.y == other.y):
            return True
        else:
            return False
    
    def __lt__(self, other):
        if(self.y >= other.y and self.x < other.x):
            return True
        else:
            return False
    
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"