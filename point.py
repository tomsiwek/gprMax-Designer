class TPoint(object):
    """
    Class represents a single point on a two-dimensional plane.

    :param x: x coordinate of the point.
    :param type: float.
    :param y: y coordinate of the point.
    :param type: float.
    """
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        """
        Check if point is equal to another one.

        :param other: point for comparison.
        :param type: TPoint.

        :rtype: boolean. 
        """
        if(self.x == other.x and self.y == other.y):
            return True
        else:
            return False
    
    def __lt__(self, other):
        """
        Check if point is less than another one, ie. its y coordinate is equal
        or less to the other and its x coordinate is lower than the other, as
        defined by de Berg et al, 2007.

        :param other: point for comparison.
        :param type: TPoint.

        :rtype: boolean. 
        """
        if(self.y >= other.y and self.x < other.x):
            return True
        else:
            return False
    
    def __str__(self):
        """
        Return a string representaion of the point.

        :rtype: string.
        """
        return "(" + str(self.x) + ", " + str(self.y) + ")"