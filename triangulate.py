from bisect import bisect_left
from copy import copy, deepcopy
import cProfile
#from itertools import islice
from math import asin, atan2, pi
import matplotlib.pyplot as plt
from sortedcontainers import SortedDict
import sys


class Vertex(object):
    """
    Class represents a polygon vertex on a 2D plane.

    :param x: vertex x coordinate.
    :type x: float
    :param y: vertex y coordinate.
    :type y: float
    :param v_type: vertex type.
    :type v_type: string
    """

    def __init__(self, x, y, v_type = None):
        """
        Initialise object variables.
        """
        self.x = x
        self.y = y
        self.v_type = v_type

    def __eq__(self, other):
        """
        "==" operator overload.

        :param other: vertex to be compared againts.
        :type other: Vertex

        :returns: True if corresponding coordinates of both vertices are equal,
                  False otherwise.
        :rtype: boolean
        """
        if(self.x == other.x and self.y == other.y):
            return True
        else:
            return False
    
    def __lt__(self, other):
        """
        "<" operator overload.

        :param other: vertex to be compared againts.
        :type other: Vertex

        :returns: True if self.y is greater than other.y or both are equal
                  and self.x is lesser than other.x, False otherwise.
        :rtype: boolean
        """
        if(self.y > other.y):
            return True
        elif(self.y == other.y and self.x < other.x):
            return True
        else:
            return False
    
    def __le__(self, other):
        """
        "<=" operator overload.

        :param other: vertex to be compared againts.
        :type other: Vertex

        :returns: True if self.__eq__(other) or self.__lt__(other),
                  False otherwise.
        :rtype: boolean
        """
        if(self.__eq__(other) or self.__lt__(other)):
            return True
        else:
            return False
    
    def __str__(self):
        """
        Return string representation of a vertex.

        :returns: string representing the vertex.
        :rtype: string
        """
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class Edge(object):
    """
    Class represents a polygon edge on a 2D plane.

    :param start: edge first vertex.
    :type start: Vertex
    :param end: edge second vertex.
    :type end: Vertex
    :param helper: edge helper vertex.
    :type helper: Vertex
    """

    def __init__(self, start = None, end = None, helper = None):
        """
        Initialise object variables.
        The edge always begins in vertex of higher y coordinate.
        """
        if(start.y > end.y):
            self.start = start
            self.end = end
        else:
            self.start = end
            self.end = start
        self.helper = helper

    def __eq__(self, other):
        """
        "==" operator overload.

        :param other: edge to be compared againts.
        :type other: Edge

        :returns: True if edges begin and end in the same points, False otherwise.
        :rtype: boolean
        """
        if(self.start == other.start and self.end == other.end):
            return True
        else:
            return False
    
    def __lt__(self, other):
        """
        "<" operator overload.

        :param other: edge to be compared againts.
        :type other: Edge

        :returns: True if self.start is lesser than other.start
                  (see Vertex.__le__()), False otherwise.
        :rtype: boolean
        """
        if(self.start < other.start):
            return True
        else:
            return False
    
    def __le__(self, other):
        """
        "<=" operator overload.

        :param other: edge to be compared againts.
        :type other: Edge

        :returns: True if self.start is lesser or equal to other.start
                  (see Vertex.__le__() and Vertex.__eq__()), False otherwise.
        :rtype: boolean
        """
        if(self.__eq__(other) or self.__lt__(other)):
            return True
        else:
            return False
    
    def __str__(self):
        """
        Return string representation of an edge.

        :returns: string representing the edge.
        :rtype: string
        """
        return str(self.start) + ":" + str(self.end)


class Polygon(object):
    """
    Class represents a polygon with its vertices and edges.

    :param vertices: list of polygons vertices.
    :type vertices: list of Vertex
    """

    def __init__(self, vertices):
        """
        Initialise object variables.
        Vertices must be stored in clockwise order.
        """
        if(not self._counterclockwise(vertices)):
            vertices.reverse()
        self._vertices = vertices[:]
        self._num_of_vertices = len(vertices)
        self._edges = []
        self._vertex_indices_dict = {}
        self._edge_indices_dict = {}
        for i, v in enumerate(vertices):
            v_nex = self._vertices[(i+1)%len(self._vertices)]
            e = Edge(v, v_nex)
            self._edges.append(e)
            self._vertex_indices_dict[(v.x, v.y)] = i
            self._edge_indices_dict[(e.start.x, e.start.y, e.end.x, e.end.y)] = i
    
    def __getitem__(self, index):
        """
        "[]" operator overload.

        :param index: index of a desired vertex in the list.
        :type index: integer

        :returns: vertex designated by the given index.
        :rtype: Vertex
        """
        return self._vertices[index]

    def vertex_index(self, v):
        """
        Get an index of a given vertex.

        :param v: examined vertex.
        :type v: Vertex

        :returns: index of a given vertex.
        :rtype: integer
        """
        i = self._vertex_indices_dict[(v.x, v.y)]
        return i
    
    def edge_index(self, e):
        """
        Get an index of a given vertex.

        :param v: examined vertex.
        :type v: Vertex

        :returns: index of a given vertex.
        :rtype: integer
        """
        i = self._edge_indices_dict[(e.start.x, e.start.y, e.end.x, e.end.y)]
        return i

    def previous_vertex(self, v):
        """
        Get a vertex preceding the given one in the vertices list.

        :param v: examined vertex.
        :type v: Vertex

        :returns: vertex preceding the given one.
        :rtype: Vertex
        """
        i_prev = self.vertex_index(v) - 1
        return self._vertices[i_prev]
    
    def next_vertex(self, v):
        """
        Get a vertex following the given one in the vertices list.

        :param v: examined vertex.
        :type v: Vertex

        :returns: vertex following the given one.
        :rtype: Vertex
        """
        i_nex = (self.vertex_index(v)  + 1)%self._num_of_vertices
        return self._vertices[i_nex]

    def get_vertices(self):
        """
        Get a list of polygon vertices.

        :returns: list of polygon vertices.
        :rtype: list of Vertex
        """
        return self._vertices
    
    def get_edge(self, v):
        """
        Get a polygon edge begining in a given vertex.

        :param v: examined vertex.
        :type v: Vertex

        :return: an edge that begins in a given vertex.
        :rtype: Edge
        """
        i = self.vertex_index(v)
        return self._edges[i]
    
    def previous_edge(self, v = None, edge = None):
        """
        Get an edge preceding the given one, or a given vertex, in the edges list.

        :param v: examined vertex.
        :type v: Vertex
        :param edge: examined edge
        :type edge: Edge

        :returns: edge preceding the given one, or a given vertex.
        :rtype: Edge
        """
        if(edge is None):
            i_pre = self.vertex_index(self.previous_vertex(v))
        else:
            i_pre = self.edge_index(edge) - 1
        return self._edges[i_pre]
    
    def next_edge(self, v = None, edge = None):
        """
        Get an edge following the given one, or a given vertex, in the edges list.

        :param v: examined vertex.
        :type v: Vertex
        :param edge: examined edge
        :type edge: Edge

        :returns: edge following the given one, or a given vertex.
        :rtype: Edge
        """
        if(edge is None):
            i_nex = self.vertex_index(self.next_vertex(v))
        else:
            i_nex = (self.edge_index(edge) + 1)%(self._num_of_vertices)
        return self._edges[i_nex]

    def signed_area(self, vertices = None):
        """
        Calculate a signed polygon area (ie. positive or negative).

        :param vertices: list of vertices constituing a polygon. If none is given,
                         method computes area of self.
        :type vertices: list of Vertex

        :returns: signed polygon area.
        :rtype: float
        """
        darea = 0.0
        if(vertices is not None):
            for v1, v2 in zip(vertices, vertices[1:] + vertices[:1]):
                darea += (v2.x - v1.x)*(v2.y + v1.y)
        else:
            for v1, v2 in zip(self._vertices, self._vertices[1:] + \
                              self._vertices[:1]):
                darea += (v2.x - v1.x)*(v2.y + v1.y)
        return darea/2

    def _counterclockwise(self, vertices):
        """
        Check wether given vertices in a list are in counterclockwise order.

        :param vertices: list of vertices to be examined.
        :type vertices: list of Vertex

        :returns: True if vertices are in counterclockwise order, False otherwise.
        :rtype: boolean
        """
        area = self.signed_area(vertices)
        if(area >= 0):
            return False
        else:
            return True
    
    def centroid(self):
        """
        Calculate polygons centeroid (geometric centre).

        :return: polygon centroid.
        :rtype: Vertex
        """
        area = self.signed_area()
        sum_x = 0.0
        sum_y = 0.0
        for vj, vj_more_1 in zip(self._vertices, self._vertices[1:] + \
                                 self._vertices[0:1]):
            sum_x += (vj.x*vj_more_1.x)*(vj.x*vj_more_1.y - vj_more_1.x*vj.y)
            sum_y += (vj.y*vj_more_1.y)*(vj.x*vj_more_1.y - vj_more_1.x*vj.y)
        return Vertex(sum_x/(6*area), sum_y/(6*area))
    
    def num_of_vertices(self):
        """
        Get number of polygon vertices.

        :return: number of polygon vertices.
        :rtype: integer
        """
        return self._num_of_vertices

    def get_first_vertex(self):
        """
        Get first vertex of the polygon.

        :return: first vertex of the polygon.
        :rtype: Vertex
        """
        return self._vertices[0]
    
    def get_first_edge(self):
        """
        Get first edge of the polygon.

        :return: first edge of the polygon.
        :rtype: Edge
        """
        return self._edges[0]
    
    def point_in_polygon(self, v):
        """
        Check wether given point lies within the polygon.
        Source:
        http://idav.ucdavis.edu/~okreylos/TAship/Spring2000/PointInPolygon.html

        :param v: examined point.
        :type v: Vertex

        :return: True of v lies within the polygon area, False otherwise.
        :rtype: boolean  
        """
        intersetion_count = 0
        x_min = min([vertex.x for vertex in self._vertices]) - 0.1
        x_max = max([vertex.x for vertex in self._vertices]) + 0.1
        for v1, v2 in zip(self._vertices[:], self._vertices[1:] + \
                          self._vertices[0:1]):
            if(v1.y < v.y and v2.y < v.y):
                continue
            elif(v1.y >= v.y and v2.y >= v.y):
                continue
            else:
                s = intersect(Vertex(x_min, v.y), Vertex(x_max, v.y), v1, v2)
                if(s.x >= v.x):
                    intersetion_count += 1
        if(intersetion_count % 2 == 1):
            return True
        else:
            return False
   

def angle(v1, v2, v3):
    """
    Calculate an angle between points v1, v2 and v3.
    Source:
    https://stackoverflow.com/questions/1211212/how-to-calculate-an-angle-from-three-points
    
    :param v1: angle first point.
    :type v1: Vertex
    :param v2: angle second point.
    :type v2: Vertex
    :param v3: angle third point.
    :type v3: Vertex
    
    :return: Angle between v1, v2 and v3 in radians.
    :rtype: float
    """
    x = (v3.x - v2.x)*(v1.x - v2.x) + (v3.y - v2.y)*(v1.y - v2.y)
    y = (v3.x - v2.x)*(v1.y - v2.y) - (v3.y - v2.y)*(v1.x - v2.x)
    if(x == 0.0 and y == 0.0):
        return 0.0
    alpha = atan2(y, x)
    if(alpha < 0):
        alpha = 2*pi + alpha
    return alpha


def vector_between_two_other(v1, v2, v3):
    """
    Check wether a vector lies between two other.
    Source:
    https://stackoverflow.com/questions/693806/how-to-determine-whether-v3-is-between-v1-and-v2-when-we-go-from-v1-to-v2-counter/693969#693969

    :param v1: first vector limiting the area.
    :type v1: Vertex
    :param v2: second vector limiting the area.
    :type v2: Vertex
    :param v3: vector to be examined.
    :type v3: Vertex
    """
    crossProds = [v1.x*v2.y - v1.y*v2.x, \
                  v1.x*v3.y - v1.y*v3.x, \
                  v3.x*v2.y - v3.y*v2.x]
    def matlab_all(lst):
        """
        Check wether all elements in a list are non-zero.

        :param lst: list to be examined.
        :type lst: list of float

        :return: True if none of the list elements equals 0, False otherwise.
        :rtype: boolean
        """
        for i in lst:
            if(i == 0):
                return False
        return True
    def ge_zero(lst):
        """
        Get a list containg 1 if a corresponging input list element is equal 
        or greater than 0 or 0 otherwise.

        :param lst: list to be examined.
        :type lst: list of float

        :return: list of 1s and 0s.
        :rtype: list of integer
        """
        result = []
        for i in lst:
            if(i >= 0):
                result.append(1)
            else:
                result.append(0)
        return result
    def lt_zero(lst):
        """
        Get a list containg 1 if a corresponging input list element is lesser 
        than 0 or 0 otherwise.

        :param lst: list to be examined.
        :type lst: list of float

        :return: list of 1s and 0s.
        :rtype: list of integer
        """
        result = []
        for i in lst:
            if(i < 0):
                result.append(1)
            else:
                result.append(0)
        return result
    if(matlab_all(ge_zero(crossProds)) or (crossProds[0] < 0 and not matlab_all(lt_zero(crossProds[1:])))):
        return True
    else:
        result = False
    return result


def intersect(v1, v2, v3, v4):
    """
    Calculate a intersection point of two line segments.
    Source:
    https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect

    :param v1: original point of the first line segment.
    :type v1: Vertex
    :param v2: final point of the first line segment.
    :type v2: Vertex
    :param v3: original point of the second line segment.
    :type v3: Vertex
    :param v4: final point of the second line segment.
    :type v4: Vertex

    :return: None if line segments do not intersect, a intersection point otherwise.
    :rtype: Vertex
    """
    s1 = Vertex(v2.x - v1.x, v2.y - v1.y)
    s2 = Vertex(v4.x - v3.x, v4.y - v3.y)
    try:
        s = (-s1.y * (v1.x - v3.x) + s1.x * (v1.y - v3.y)) / (-s2.x * s1.y + s1.x * s2.y)
    except:
        return None
    try:
        t = ( s2.x * (v1.y - v3.y) - s2.y * (v1.x - v3.x)) / (-s2.x * s1.y + s1.x * s2.y)
    except:
        return None
    if(s >= 0 and s <= 1 and t >= 0 and t <= 1):
        return Vertex(v1.x + (t*s1.x), v1.y + (t*s1.y))
    return None


def overlapping(v1, v2, v3, v4):
    """
    Check wether two line segments overlap each other.
    Source:
    https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect

    :param v1: original point of the first line segment.
    :type v1: Vertex
    :param v2: final point of the first line segment.
    :type v2: Vertex
    :param v3: original point of the second line segment.
    :type v3: Vertex
    :param v4: final point of the second line segment.
    :type v4: Vertex

    :return: True if line segment overlap each other, False otherwise.
    :rtype: boolean
    """
    s1 = Vertex(v2.x - v1.x, v2.y - v1.y)
    s2 = Vertex(v4.x - v3.x, v4.y - v3.y)
    cross1 = s1.x*s2.y - s1.y*s2.x
    s3 = Vertex(v3.x - v1.x, v3.y - v1.y)
    cross2 = s3.x*s2.y - s3.y*s2.x
    if(cross1 == 0.0 and cross2 == 0.0):
        t0 = (s3.x*s1.x + s3.y*s1.y)/(s1.x*s1.x + s1.y*s1.y)
        t1 = t0 + (s2.x*s1.x + s2.y*s1.y)/(s1.x*s1.x + s1.y*s1.y)
        if((t0 < 0 and t1 < 0) or (t0 > 1 and t1 > 1)):
            return False
        else:
            return True
    return False

def create_edges(p):
    """
    Create edges list from a given vertices list.

    :param p:
    :type p: list of Vertex

    :return: list of created edges.
    :rtype: list of Edge
    """
    d = []
    for i, _ in enumerate(p):
        e = Edge(p[i], p[(i+1)%len(p)])
        d.append(e)
    return d[:]


def plot_diags(polygon, diags, point = None, point2 = None, title = None):
    """
    Plot polygon diagonals.

    :param diags: list of diagonals to be ploted.
    :type diags: list of Edge
    :param point: point to be ploted againts the polygon with diagonals.
    :type point: Vertex
    :param point2: second point to be ploted againts the polygon with diagonals.
    :type point2: Vertex
    :param title: plot title.
    :type title: string
    """
    for i, pt in enumerate(polygon):
        plt.plot([pt.x, polygon[(i+1)%len(polygon)].x], [pt.y, polygon[(i+1)%len(polygon)].y], c = 'b')
    for d in diags:
        plt.plot([d.start.x, d.end.x], [d.start.y, d.end.y], c = 'r')
    if(point is not None):
        x_min = min([pt.x for pt in polygon]) - 0.1
        x_max = max([pt.x for pt in polygon]) + 0.1
        plt.plot([x_min, x_max], [point.y, point.y], 'k', linewidth = 0.5)
        plt.plot([point.x], [point.y], '.g')
    if(point2 is not None):
        plt.plot([point2.x], [point2.y], '.r')
    if(title is not None):
        plt.title(str(title))
    plt.grid()
    plt.show()


def make_monotone(polygon):
    """
    Divide a polygon into y-monotone pieces.
    Source: 
    de Berg, van Kreveld, Overmars, Schwrzkopf 'Computational geometry'
    Section 3.2

    :param polygon: polygon to be divided.
    :type polygon: Polygon

    :return: list of diagonals dividing the polygon into y-monotone pieces.
    :rtype: list of Edge
    """

    def create_vertices_queue(vertices_list):
        """
        Create vertices queue sorted in descending order by y coordinate, then
        ascending by x coordinate.

        :param vertices_list: list of vertices to form the queue of.
        :type vertices_list: list of Vertex

        :return: vertices queue.
        :rtype: list of Vertex
        """
        q = vertices_list[:]
        q.sort(key = lambda pt: (pt.y, -pt.x))
        return q

    def vertex_type(v, polygon):
        """
        Determine type of a vertex.
        
        :param v: examined vertex.
        :type v: Vertex
        :param polygon: the polygon to which the vertex belongs.
        :type polygon: Polygon 

        :return: type of the vertex (start, split, end, merge, regular_up, regular_down)
        :rtype: string
        """
        v_pre = polygon.previous_vertex(v)
        v_nex = polygon.next_vertex(v)
        alpha = angle(v_pre, v, v_nex)
        def lower(p, q):
            """
            Check wether point p is lower than q, according to de Berg et al.

            :param p: vertex to be compared.
            :type p: Vertex
            :param q: vertex to be compared againts.
            :type q: Vertex

            :return: True if p is lower than q, ie. its y coordinate is lesser than q or
                     they are equal and p.x is greater than q.x, False otherwise.
            :rtype: boolean
            """
            if(p.y < q.y or (p.y == q.y and p.x > q.x)):
                return True
            else:
                return False
        def upper(p, q):
            """
            Check wether point p is above q, according to de Berg et al.

            :param p: vertex to be compared.
            :type p: Vertex
            :param q: vertex to be compared againts.
            :type q: Vertex

            :return: True if p is above q, ie. its y coordinate is greater than q or
                     they are equal and p.x is lesser than q.x, False otherwise.
            :rtype: boolean
            """
            if(p.y > q.y or (p.y == q.y and p.x < q.x)):
                return True
            else:
                return False            
        if(lower(v_pre, v) and lower(v_nex, v)):
            if(alpha < pi):
                v_type = "start"
            else:
                v_type = "split"
        elif(upper(v_pre, v) and upper(v_nex, v)):
            if(alpha < pi):
                v_type = "end"
            else:
                v_type = "merge"
        elif((lower(v_pre, v)) and upper(v_nex, v)):
            v_type = "regular_up"
        elif(upper(v_pre, v) and lower(v_nex, v)):
            v_type = "regular_down"
        return v_type
    
    def insert(dictionary, e):
        """
        Insert edge to a dictionary.

        :param dictionary: dictionary into which an edge is to be inserted.
        :type dictionary: sortedcontainers.SortedDict
        :param e: edge to be inserted.
        :type e: Edge
        """
        key = min(e.start.x, e.end.x)
        dk = 1.0e-10
        while(key in dictionary):
            key += dk
        dictionary[key] = e

    def delete(dictionary, e):
        """
        Delete edge from a dictionary.

        :param dictionary: dictionary from which an edge is to be deleted.
        :type dictionary: sortedcontainers.SortedDict
        :param e: edge to be deleted.
        :type e: Edge
        """
        key = min(e.start.x, e.end.x)
        dk = 1.0e-10
        while((key+dk) in dictionary):
            key += dk
        del dictionary[key]

    def find_left(dictionary, v):
        """
        Find nearest edge located to the left of a given vertex in the dictionary.
        Source:
        https://stackoverflow.com/questions/7934547/python-find-closest-key-in-a-dictionary-from-the-given-input-key

        :param dictionary: dictionary in which the edge is to be found.
        :type dictionary: sortedcontainers.SortedDict
        :param v: vertex which x coordinate is to be used as a search key.
        :type v: Vertex

        :return: nearest edge located to the left of a given vertex.
        :rtype:Edge
        """
        key = v.x
        if(len(dictionary) == 1):
            ind = next(reversed(dictionary))
            return dictionary[ind]
        ind = bisect_left(list(dictionary.keys()), key)
        if(ind == len(dictionary)):
            ind -= 1
        found_key = list(dictionary.keys())[ind]
        if(found_key > key):
            found_key = list(dictionary.keys())[ind - 1]
            ind -= 1
        e = dictionary[found_key]
        min_x = min(e.start.x, e.end.y) - 0.1
        max_x = max(e.start.x, e.end.y) + 0.1
        tmp_v1 = Vertex(min_x, v.y)
        tmp_v2 = Vertex(max_x, v.y)
        s = intersect(e.start, e.end, tmp_v1, tmp_v2)
        if(debug and left_count >= left_stop):
            print(v, s)
        if(s is not None and s.x >= v.x):
            found_key = list(dictionary.keys())[ind - 1]
        return dictionary[found_key]
            
    def handle_start_vertex(v):
        """
        Handle encountered start vertex.

        :param v: examined vertex.
        :type v: Veretx
        """
        nonlocal t, polygon
        e = polygon.get_edge(v)
        e.helper = v
        insert(t, e)
    
    def handle_end_vertex(v):
        """
        Handle encountered end vertex.

        :param v: examined vertex.
        :type v: Veretx
        """
        nonlocal t, d, polygon
        e_prev = polygon.previous_edge(v)
        helper = e_prev.helper
        if(helper is not None and helper.v_type == "merge"):
            d.append(Edge(v, e_prev.helper))
        delete(t, e_prev)
    
    def handle_split_vertex(v):
        """
        Handle encountered split vertex.

        :param v: examined vertex.
        :type v: Veretx
        """
        nonlocal t, d, polygon, left_count
        e = polygon.get_edge(v)
        left = find_left(t, v)
        if(debug):
            left_count += 1
            if(left_count >= left_stop):
                plot_diags(polygon.get_vertices(), [left], v, title = left_count)
        d.append(Edge(v, left.helper))
        left.helper = v
        e.helper = v
        insert(t, e)
    
    def handle_merge_vertex(v):
        """
        Handle encountered merge vertex.

        :param v: examined vertex.
        :type v: Veretx
        """
        nonlocal t, d, polygon, left_count
        e_prev = polygon.previous_edge(v)
        if(e_prev.helper is not None and e_prev.helper.v_type == "merge"):
            d.append(Edge(v, e_prev.helper))
        delete(t, e_prev)
        left = find_left(t, v)
        if(debug):
            left_count += 1
            if(left_count >= left_stop):
                plot_diags(polygon.get_vertices(), [left], v, title = left_count)
        if(left.helper.v_type == "merge"):
            d.append(Edge(v, left.helper))
        left.helper = v
    
    def handle_regular_down_vertex(v):
        """
        Handle encountered regular_down vertex vertex.

        :param v: examined vertex.
        :type v: Veretx
        """
        nonlocal t, d, polygon
        e_prev = polygon.previous_edge(v) 
        if(e_prev.helper is not None and e_prev.helper.v_type == "merge"):
            d.append(Edge(v, e_prev.helper))
        delete(t, e_prev)
        e = polygon.get_edge(v)
        e.helper = v
        insert(t, e)
    
    def handle_regular_up_vertex(v):
        """
        Handle encountered regular_up vertex.

        :param v: examined vertex.
        :type v: Veretx
        """
        nonlocal left_count
        left = find_left(t, v)
        if(debug):
            left_count += 1
            if(left_count >= left_stop):
                plot_diags(polygon.get_vertices(), [left], v, title = left_count)
        if(left.helper.v_type == "merge"):
            d.append(Edge(v, left.helper))
        left.helper = v

    q = create_vertices_queue(polygon.get_vertices())
    d = []
    t = SortedDict()
    debug = False
    left_stop = 23
    left_count = 0
    while(q != []):
        v = q.pop()
        v.v_type = vertex_type(v, polygon)
        if(v.v_type == "start"):
            handle_start_vertex(v)
        elif(v.v_type == "end"):
            handle_end_vertex(v)
        elif(v.v_type == "split"):
            handle_split_vertex(v)
        elif(v.v_type == "merge"):
            handle_merge_vertex(v)
        elif(v.v_type == "regular_down"):
            handle_regular_down_vertex(v)
        elif(v.v_type == "regular_up"):
            handle_regular_up_vertex(v)
        else:
            raise TypeError("Unknown vertex type!")
        if(debug):
            print(v, v.v_type)
    return d

def inner_diagonal(v1, v2, polygon):
    """
    Check wether given line segment constitutes a inner diagonal of the polygon.
    Source:
    https://stackoverflow.com/questions/693837/how-to-determine-a-diagonal-is-in-or-out-of-a-concave-polygon

    :param v1: first diagonal point.
    :type v1: Vertex
    :param v2: second diagonal point.
    :type v2: Vertex
    :param polygon: examined polygon.
    :type polygon: Polygon

    :return: True if a line segment contitutes an inner polygon diagonal,
             False otherwise.
    :rtype: boolean
    """
    debug = False
    if(debug):
        plot_diags(polygon.get_vertices(), [Edge(v1, v2)])
    try:
        v1_pos = polygon.vertex_index(v1)
        v2_pos = polygon.vertex_index(v2)
    except:
        return False
    if(v1_pos > v2_pos):
        v2, v1 = v1, v2
    if(polygon.next_vertex(v1) == v2):
        # If v1 and v2 are consecutive they can't constitute a diagonal
        return False
    for vj in polygon.get_vertices():
        # Check instersections with every edge in polygon
        v_nex = polygon.next_vertex(vj)
        s = intersect(v1, v2, vj, v_nex)
        if(s is not None and s.x != v1.x and s.y != v1.y and \
           s.x != v2.x and s.y != v2.y):
            return False
        if(overlapping(v1, v2, vj, v_nex)):
            return False
    v1_nex = polygon.next_vertex(v1)
    v1_pre = polygon.previous_vertex(v1)
    vec1 = Vertex(v1_nex.x - v1.x, v1_nex.y - v1.y)
    vec2 = Vertex(v1_pre.x - v1.x, v1_pre.y -v1.y)
    vec3 = Vertex(v2.x - v1.x, v2.y - v1.y)
    if(not vector_between_two_other(vec1, vec2, vec3)):
        return False
    return True


def split_polygons(polygon, diagolnals):
    """
    Split a polygon into separate shapes along given diagonals. 
    Source
    https://stackoverflow.com/questions/9455875/how-to-split-a-polygon-along-n-given-diagonals

    :param polygon: polygon to be split.
    :type polygon: Polygon.
    :param diagonals: diagonals along which the polygon is to be split.
    :type: diagonal: list of Edge
    """
    vert = deepcopy(polygon.get_vertices())
    polygons = []
    def arc_lenght(i, j):
        return min(max(i,j) - min(i,j), polygon.num_of_vertices() - max(i,j) + min(i,j))
    def sorter(edge):
        return arc_lenght(polygon.vertex_index(edge.start), polygon.vertex_index(edge.end))
    sorted_diagonals = diagolnals[:]
    sorted_diagonals.sort(key = sorter)
    debug = False
    diag_count = 0
    diag_stop = 1
    for diag, diag_nex in zip(sorted_diagonals[:-1], sorted_diagonals[1:]):
        if(debug):
            diag_count += 1
            if(diag_count >= diag_stop):
                plt.plot([vert[0].x], [vert[0].y], 'og')
                plt.title(str(diag_count))
                for i, pt in enumerate(vert):
                    plt.plot([pt.x, vert[(i+1)%len(vert)].x], [pt.y, vert[(i+1)%len(vert)].y], c = 'b')
                plt.plot([diag.start.x, diag.end.x], [diag.start.y, diag.end.y], c = 'r')
                plt.show()
        start_pos = min(vert.index(diag.start), vert.index(diag.end))
        end_pos = max(vert.index(diag.start), vert.index(diag.end))
        p1 = Polygon(vert[start_pos:(end_pos+1)])
        p2 = Polygon(vert[:(start_pos+1)] + vert[(end_pos)%len(vert):])
        next_in = ""
        if(p1.num_of_vertices() < p2.num_of_vertices()):
            if(inner_diagonal(diag_nex.start, diag_nex.end, p1)):
                next_in = "p1"
            else:
                next_in = "p2"
        else:
            if(inner_diagonal(diag_nex.start, diag_nex.end, p2)):
                next_in = "p2"
            else:
                next_in = "p1"
        if(next_in == "p1"):
            polygons.append(p2)
            if(end_pos + 1 == len(vert)):
                vert = vert[(start_pos):]
            else:
                vert = vert[(start_pos):(end_pos+1)%len(vert)]
        else:
            polygons.append(p1)
            if(end_pos + 1 == len(vert)):
                vert = vert[end_pos:] + vert[:(start_pos+1)]
            else:
                vert = vert[:(start_pos+1)] + vert[end_pos:]
    # Last diagonal
    try:
        diag = sorted_diagonals[-1]
    except IndexError:
        # Triangle, hence the list is empty
        polygons.append(Polygon(vert))
    else:
        start_pos = min(vert.index(diag.start), vert.index(diag.end))
        end_pos = max(vert.index(diag.start), vert.index(diag.end))
        p1 = Polygon(vert[start_pos:(end_pos+1)])
        p2 = Polygon(vert[:(start_pos+1)] + vert[(end_pos)%len(vert):])
        polygons.append(p1)
        polygons.append(p2)
    return polygons


def triangulate_monotone_polygon(polygon):
    """
    Triangulate an y-monotone polygon.
    Source: 
    de Berg, van Kreveld, Overmars, Schwrzkopf 'Computational geometry'
    Section 3.3

    :param polygon: y-monotone polygon to be triangulated.
    :type polygon: Polygon
    """

    def same_chain(v1, v2, polygon):
        """
        Check wether two vertices lie on the same polygon edges chain, observing
        from the topmost one.

        :param v1:
        :type v1: Vertex
        :param v2:
        :type v2: Vertex

        :return: True if given vertices lie on the same polygon edges chain,
                 False otherwise.
        :rtype: boolean
        """
        summit = u[0]
        bottom = u[-1]
        v1_found = False
        v2_found = False
        reverse = False
        if(v1 == v2):
            raise Exception("Both given vertices are the same!")
        if(v1 == summit or v2 == summit):
            return False
        lenght = abs(polygon.vertex_index(summit) - polygon.vertex_index(bottom))
        if(lenght < polygon.num_of_vertices() - lenght):
            reverse = True
        # Walk through shorter branch
        vj = summit
        if(not reverse):
            while(not vj == bottom):
                if(vj == v1):
                    v1_found = True
                if(vj == v2):
                    v2_found = True
                vj = polygon.next_vertex(vj)
        else:
            while(not vj == bottom):
                if(vj == v1):
                    v1_found = True
                if(vj == v2):
                    v2_found = True
                vj = polygon.previous_vertex(vj)
        if(v1_found is True and v2_found is True):
            return True
        elif(v1_found is False and v2_found is False):
            return True
        return False

    def create_vertices_sequence(polygon):
        """
        Create vertices sequence sorted in descending order by y coordinate, then
        ascending by x coordinate.

        :param polygon: polygon from which vertices the sequence is to be created.
        :type polygn: Polygon

        :return: vertices sequence.
        :rtype: list of Vertex
        """
        vert = polygon[:]
        vert.sort(key = lambda pt: (pt.y, -pt.x))
        vert.reverse()
        return vert

    debug = False
    u = create_vertices_sequence(polygon.get_vertices())
    s = [u[0], u[1]]
    d = []
    for j in range(2, polygon.num_of_vertices() - 1):
        if(debug):
            plot_diags(polygon.get_vertices(), d, u[j], s[-1])
        if(not same_chain(u[j], s[-1], polygon)):
            while(s != []):
                last = s.pop()
                if(len(s) >= 1):
                    d.append(Edge(u[j], last))
            s = [u[j-1], u[j]]
        else:
            last = s.pop()
            while(len(s) > 0 and inner_diagonal(u[j], s[-1], polygon)):
                d.append(Edge(u[j], s[-1]))
                if(debug):
                    plot_diags(polygon.get_vertices(), d)
                last = s.pop()
            s.append(last)
            s.append(u[j])
    s.pop()
    while(len(s) > 1):
        last = s.pop()
        d.append(Edge(u[-1], last))
    if(debug):
        plot_diags(polygon.get_vertices(), d, u[-1])
    return d


# if(__name__ == "__main__"):
#     with open('test_poly_1000.txt', 'r') as f:
#         content = f.readlines()
#     polygon_dupl = []
#     for line in content:
#         x, y = line.split('\t')
#         polygon_dupl.append(Vertex(float(x), float(y)))
#     polygon = []
#     for pt in polygon_dupl:
#         if(pt not in polygon):
#             polygon.append(pt)

#     from timeit import default_timer as timer
#     polygon_obj = Polygon(polygon)
#     start = timer()
#     edges = make_monotone(polygon_obj)
#     monotone_polygons = split_polygons(polygon_obj, edges)
#     edges2 = []
#     for poly in monotone_polygons:
#         if(poly != []):
#             edges2 += triangulate_monotone_polygon(poly)
#     # tt = split_polygons(polygon_obj, edges)
#     end = timer()
#     print("n vertices:", len(polygon))
#     print("elapsed time:", end - start)
#     for i, pt in enumerate(polygon):
#         plt.plot([pt.x, polygon[(i+1)%len(polygon)].x], [pt.y, polygon[(i+1)%len(polygon)].y], c = 'b')
#     for e in edges:
#         plt.plot([e.start.x, e.end.x], [e.start.y, e.end.y], c = 'r')
#     for i, e in enumerate(edges2):
#         plt.plot([e.start.x, e.end.x], [e.start.y, e.end.y], c = 'g', linewidth = 0.75)
#     plt.grid()
#     plt.show()
