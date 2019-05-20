from math import floor

from point import TPoint

class TGeometry(object):
    """
    Class contains static methods used for coordinates calculations (window and model system).
    """
    # Calculate model coordinates given windows coordinates
    @staticmethod
    def window_to_model(window_pt, min_model, max_model, min_window, max_window, dx, dy):
        mod_pt = TPoint()
        mod_pt.x = TGeometry.round_to_multiple((max_model.x - min_model.x)*(window_pt.x - min_window.x)/(max_window.x - min_window.x) + min_model.x, dx)
        mod_pt.y = TGeometry.round_to_multiple((max_model.y - min_model.y)*(window_pt.y - min_window.y)/(max_window.y - min_window.y) + min_model.y, dy)
        return mod_pt

    # Calculate window coordinates given model coordinates
    @staticmethod
    def model_to_window(mod_pt, min_model, max_model, min_window, max_window):
        window_pt = TPoint()
        window_pt.x = round(((mod_pt.x - min_model.x)*(max_window.x - min_window.x))/(max_model.x - min_model.x) + min_window.x)
        window_pt.y = round(((mod_pt.y - min_model.y)*(max_window.y - min_window.y))/(max_model.y - min_model.y) + min_window.y)
        return window_pt

    # Calculate distance in model coordinate system given distance in window coordinate system
    @staticmethod
    def dist_window_to_model(mod_dist, min_model, max_model, min_window, max_window, dx, dy):
        return TGeometry.round_to_multiple(mod_dist*(max_model.x - min_model.x)/(max_window.x - min_window.x), min(dx, dy))
    
    # Calculate distance in windows coordinate system given distance in model coordinate system
    @staticmethod
    def dist_model_to_window(win_dist, min_model, max_model, min_window, max_window):
        return win_dist*(max_window.x - min_window.x)/(max_model.x - min_model.x)

    # Round given real to nearest multiple of another real
    @staticmethod
    def round_to_multiple (x, m):
        m_reverse = m**(-1)
        return floor (x*m_reverse + 0.5)/m_reverse # Python has issues with float multiplying

    @staticmethod
    def position_in_boundries(pos, box_min, box_max):
        "Detect if given mouse position lies within model"
        if(pos.x >= min(box_min.x, box_max.x) and pos.x <= max(box_min.x, box_max.x) and \
           pos.y >= min(box_min.y, box_max.y) and pos.y <= max(box_min.y, box_max.y)):
            return True
        return False

    @staticmethod
    def point_visible(point, min_model, max_model):
        "Detect if given point is within visible area of model"
        if((point.x >= min_model.x and point.y >= min_model.y) and \
           (point.x <= max_model.x and point.y <= max_model.y)):
            return True
        else:
            return False

    @staticmethod
    def intersect(point1, point2, point3, point4):
        "Detect if two line segments intersect"
        def sign(a):
            if(a >= 0):
                return 1
            else:
                return -1
        det1 = point1.x*point2.y + point1.y*point3.x + point2.x*point3.y - \
               point3.x*point2.y - point1.x*point3.y - point2.x*point1.y
        det2 = point1.x*point2.y + point1.y*point4.x + point2.x*point4.y - \
               point4.x*point2.y - point1.x*point4.y - point2.x*point1.y
        if(sign(det1) != sign(det2)):
            return True
        else:
            return False
    
    @staticmethod
    def polygon_area(points):
        "Calculates area of polygon enclosed by points in given list"
        sum = 0.0
        for i, pt in enumerate(points):
            if(i == 0):
                sum += pt.x*(points[1].y - points[-1].y)
            elif(i + 1 == len(points)):
                sum += pt.x*(points[0].y - points[-2].y)
            else:
                sum += pt.x*(points[i+1].y - points[i-1].y)
        return abs(sum/2)