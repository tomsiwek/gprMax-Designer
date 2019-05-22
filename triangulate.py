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
    2D vertex
    """

    def __init__(self, x, y, v_type = None):
        # self.x = Decimal(str(x))
        # self.y = Decimal(str(y))
        self.x = x
        self.y = y
        self.v_type = v_type

    def __eq__(self, other):
        if(self.x == other.x and self.y == other.y):
            return True
        else:
            return False
    
    def __lt__(self, other):
        if(self.y > other.y):
            return True
        elif(self.y == other.y and self.x < other.x):
            return True
        else:
            return False
    
    def __le__(self, other):
        if(self.__eq__(other) or self.__lt__(other)):
            return True
        else:
            return False
    
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class Edge(object):
    """
    2D edge
    """

    def __init__(self, start = None, end = None, helper = None):
        "Edge always begins in point of higher y value"
        if(start.y > end.y):
            self.start = start
            self.end = end
        else:
            self.start = end
            self.end = start
        self.helper = helper

    def __eq__(self, other):
        if(self.start == other.start and self.end == other.end):
            return True
        else:
            return False
    
    def __lt__(self, other):
        if(self.start < other.start):
            return True
        else:
            return False
    
    def __le__(self, other):
        if(self.__eq__(other) or self.__lt__(other)):
            return True
        else:
            return False
    
    def __str__(self):
        return str(self.start) + ":" + str(self.end)


class Polygon(object):
    """
    Polygon with its vertices and edges
    """

    def __init__(self, vertices):
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
        return self._vertices[index]

    def vertex_index(self, v):
        i = self._vertex_indices_dict[(v.x, v.y)]
        return i
    
    def edge_index(self, e):
        i = self._edge_indices_dict[(e.start.x, e.start.y, e.end.x, e.end.y)]
        return i

    def previous_vertex(self, v):
        i_prev = self.vertex_index(v) - 1
        return self._vertices[i_prev]
    
    def next_vertex(self, v):
        i_nex = (self.vertex_index(v)  + 1)%self._num_of_vertices
        return self._vertices[i_nex]

    def get_vertices(self):
        return self._vertices
    
    def get_edge(self, v):
        i = self.vertex_index(v)
        return self._edges[i]
    
    def previous_edge(self, v = None, edge = None):
        if(edge is None):
            i_pre = self.vertex_index(self.previous_vertex(v))
        else:
            i_pre = self.edge_index(edge) - 1
        return self._edges[i_pre]
    
    def next_edge(self, v = None, edge = None):
        if(edge is None):
            i_nex = self.vertex_index(self.next_vertex(v))
        else:
            i_nex = (self.edge_index(edge) + 1)%(self._num_of_vertices)
        return self._edges[i_nex]

    def signed_area(self, vertices = None):
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
        area = self.signed_area(vertices)
        if(area >= 0):
            return False
        else:
            return True
    
    def centeroid(self):
        area = self.signed_area()
        sum_x = 0.0
        sum_y = 0.0
        for vj, vj_more_1 in zip(self._vertices, self._vertices[1:] + \
                                 self._vertices[0:1]):
            sum_x += (vj.x*vj_more_1.x)*(vj.x*vj_more_1.y - vj_more_1.x*vj.y)
            sum_y += (vj.y*vj_more_1.y)*(vj.x*vj_more_1.y - vj_more_1.x*vj.y)
        return Vertex(sum_x/(6*area), sum_y/(6*area))
    
    def num_of_vertices(self):
        return self._num_of_vertices

    def get_first_vertex(self):
        return self._vertices[0]
    
    def get_first_edge(self):
        return self._edges[0]
    
    def point_in_polygon(self, v):
        """
        http://idav.ucdavis.edu/~okreylos/TAship/Spring2000/PointInPolygon.html
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
    
    def split_polygon(self, diag):
        raise NotImplementedError("Feature not yet completed")
        # new_polygon = []
        # reverse = False
        # start = diag.start
        # end = diag.end
        # if(not diag.start < diag.end):
        #     start = diag.end
        #     end = diag.start
        # if(self.next_vertex(start) < start):
        #     reverse = True
        # vj = start
        # if(not reverse):
        #     while(not vj == end):
        #         new_polygon.append(vj)
        #         vj = self.next_vertex(vj)
        #     new_polygon.append(vj)
        # else:
        #     while(not vj == end):
        #         new_polygon.append(vj)
        #         vj = self.previous_vertex(vj)
        #     new_polygon.append(vj)
        # return new_polygon


# class Node(object):
#     def __init__(self, key, *, parent = None, edge = None):
#         self.key = key
#         self.edge = edge
#         self.left_child = None
#         self.right_child = None
#         self.parent = parent


# class LBST(object):
#     """
#     Binary search tree that stores all data in leaves. Innder node's key is equal to the maximal leave key
#     in its left subtree
#     """
#     def __init__(self):
#         self.root = None
#         self._max_key = None

#     def print(self):
#         self._print_in_order(self.root)
#         print('---')

#     def _print_in_order(self, current_node):
#         if(current_node is not None):
#             self._print_in_order(current_node.left_child)
#             print(current_node.key)
#             self._print_in_order(current_node.right_child)

#     def max(self):
#         current_node = self.root
#         while(current_node.right_child is not None):
#             current_node = current_node.right_child
#         return current_node.key
    
#     def min(self):
#         current_node = self.root
#         while(current_node.left_child is not None):
#             current_node = current_node.left_child
#         return current_node.key
    
#     def insert(self, edge, vertex):
#         key = vertex.x
#         if(self.root is None):
#             self.root = Node(key, edge = edge)
#             self._max_key = key
#         else:
#             self._insert_node(key, edge)

#     def _insert_node(self, key, edge):
#         current_node = self.root
#         prev_key = key
#         while(current_node.right_child is not None):
#             if(key < current_node.right_child.key):
#                 prev_key = current_node.key
#                 if(key > current_node.key):
#                     current_node.key = key
#                 current_node = current_node.left_child
#             else:
#                 current_node = current_node.right_child
#         parent = current_node.parent
#         if(parent is None or current_node == parent.left_child):
#             ckey = current_node.key
#             current_node.key = min(ckey, key)
#             if(ckey < key):
#                 current_node.left_child = Node(min(ckey, key), parent = current_node, \
#                                                                edge = current_node.edge)
#                 current_node.right_child = Node(max(ckey, key), parent = current_node, edge = edge)
#             else:
#                 current_node.left_child = Node(min(ckey, key), parent = current_node, edge = edge)
#                 current_node.right_child = Node(max(ckey, key), parent = current_node, \
#                                                 edge = current_node.edge)
#             if(key > self._max_key):
#                 self._max_key = key
#         elif(current_node.key == self._max_key):
#             current_node.left_child = Node(current_node.key, parent = current_node, \
#                                            edge = current_node.edge)
#             current_node.right_child = Node(key, parent = current_node, edge = edge)
#             self._max_key = key
#         else:
#             left_subtree = copy(parent)
#             parent.right_child = Node(key, parent = parent, edge = edge)
#             parent.key = prev_key
#             parent.left_child = left_subtree
#             parent.left_child.parent = current_node.parent
#             self._update_subtree_parents(left_subtree)
#             if(key > self._max_key):
#                 self._max_key = key
#         if(parent is not None):
#             parent.edge = None
    
#     def _update_subtree_parents(self, current_node):
#         if(current_node.left_child is not None):
#             self._update_subtree_parents(current_node.left_child)
#             current_node.left_child.parent = current_node
#             current_node.right_child.parent = current_node
#             self._update_subtree_parents(current_node.right_child)
        
#     def find_max_smaller_than(self, x):
#         return self._find_max_smaller_than_node(self.root, x)
    
#     def _find_max_smaller_than_node(self, current_node, x):
#         if(current_node == None):  
#             return None
#         if(current_node.key == x):  
#             return current_node
#         elif(current_node.key < x):  
#             node = self._find_max_smaller_than_node(current_node.right_child, x)
#             if(node is None): 
#                 return current_node
#             else: 
#                 return node
#         elif(current_node.key > x):
#             return self._find_max_smaller_than_node(current_node.left_child, x)
    
#     def find_leaf(self, key):
#         return self._find_leaf_node(self.root, key)

#     def _find_leaf_node(self, current_node, key):
#         if(current_node is None):
#             return None
#         elif(key == current_node.key):
#             if(current_node.left_child is not None):
#                 return self._find_leaf_node(current_node.left_child, key)
#             else:
#                 return current_node
#         elif(key < current_node.key):
#             return self._find_leaf_node(current_node.left_child, key)
#         else:
#             return self._find_leaf_node(current_node.right_child, key)
    
#     def delete(self, vertex, edge):
#         key = vertex.x
#         current_node = self.root
#         while(current_node.right_child is not None):
#             if(key <= current_node.key):
#                 if(key == current_node.key):
#                     current_node.key = current_node.left_child.key
#                 current_node = current_node.left_child
#             else:
#                 current_node = current_node.right_child
#         parent = current_node.parent
#         if(parent is None):
#             self.root = None
#             self._max_key = None
#         else:
#             if(key == self._max_key):
#                 left = self._get_direct_left_leaf(current_node)
#                 self._max_key = left.key
#             if(current_node == parent.left_child):
#                 subtree = copy(parent.right_child)
#             elif(current_node == parent.right_child):
#                 subtree = copy(parent.left_child)
#             if(parent.parent is not None):
#                 subtree.parent = parent.parent
#                 if(parent == parent.parent.left_child):
#                     parent.parent.left_child = subtree
#                 elif(parent == parent.parent.right_child):
#                     parent.parent.right_child = subtree
#             else:
#                 self.root = subtree
#                 self.root.parent = None
#             self._update_subtree_parents(subtree)
#             del current_node

#     def find_left(self, vertex):
#         key = vertex.x
#         current_node = self.root
#         while(current_node.right_child is not None):
#             if(key > current_node.key and key > current_node.right_child.key):
#                 current_node = current_node.right_child
#             else:
#                 current_node = current_node.left_child
#         if(current_node.key >= key):
#             return self._get_direct_left_leaf(current_node)
#         elif((max(current_node.edge.start.x, current_node.edge.end.x) > vertex.x and
#             max(current_node.edge.start.y, current_node.edge.end.y) > vertex.y)):
#             return self._get_direct_left_leaf(current_node)
#         else:
#             return current_node

#     def _get_direct_left_leaf(self, right_node):
#         current_node = right_node.parent
#         if(current_node is not None):
#             current_node = current_node.left_child
#             while(current_node.right_child is not None):
#                 current_node = current_node.right_child
#             return current_node
               

def angle(v1, v2, v3):
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
    https://stackoverflow.com/questions/693806/how-to-determine-whether-v3-is-between-v1-and-v2-when-we-go-from-v1-to-v2-counter/693969#693969
    """
    crossProds = [v1.x*v2.y - v1.y*v2.x, \
                  v1.x*v3.y - v1.y*v3.x, \
                  v3.x*v2.y - v3.y*v2.x]
    def matlab_all(lst):
        for i in lst:
            if(i == 0):
                return False
        return True
    def ge_zero(lst):
        result = []
        for i in lst:
            if(i >= 0):
                result.append(1)
            else:
                result.append(0)
        return result
    def lt_zero(lst):
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
    https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
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
    https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
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
    d = []
    for i, _ in enumerate(p):
        e = Edge(p[i], p[(i+1)%len(p)])
        d.append(e)
    return d[:]


def plot_diags(polygon, diags, point = None, point2 = None, title = None):
    for i, pt in enumerate(polygon):
        plt.plot([pt.x, polygon[(i+1)%len(polygon)].x], [pt.y, polygon[(i+1)%len(polygon)].y], c = 'b')
    for d in diags:
        plt.plot([d.start.x, d.end.x], [d.start.y, d.end.y], c = 'r')
        # plt.pause(0.5)
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
    Derived from: 
    de Berg, van Kreveld, Overmars, Schwrzkopf 'Computational geometry'
    Section 3.2
    """

    def create_vertices_queue(vertices_list):
        q = vertices_list[:]
        q.sort(key = lambda pt: (pt.y, -pt.x))
        return q

    def vertex_type(v, polygon):
        "Determine type of vertex"
        v_pre = polygon.previous_vertex(v)
        v_nex = polygon.next_vertex(v)
        alpha = angle(v_pre, v, v_nex)
        def lower(p, q):
            if(p.y < q.y or (p.y == q.y and p.x > q.x)):
                return True
            else:
                return False
        def upper(p, q):
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
        # print(v, v_type)
        return v_type
    
    def insert(dictionary, e, v):
        """
        Insert edge to dictionary.
        """
        key = min(e.start.x, e.end.x)
        while(key in dictionary):
            key += 1.0e-10
        dictionary[key] = e

    def delete(dictionary, e, v):
        """
        Delete edge from dictionary.
        """
        key = min(e.start.x, e.end.x)
        dk = 1.0e-10
        while((key+dk) in dictionary):
            key += dk
        del dictionary[key]

    def find_left(dictionary, v):
        """
        Find nearest edge located to the left of given vertex in dictionary.
        https://stackoverflow.com/questions/7934547/python-find-closest-key-in-a-dictionary-from-the-given-input-key
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
        nonlocal t, polygon
        e = polygon.get_edge(v)
        e.helper = v
        insert(t, e, v)
    
    def handle_end_vertex(v):
        nonlocal t, d, polygon
        e_prev = polygon.previous_edge(v)
        helper = e_prev.helper
        if(helper is not None and helper.v_type == "merge"):
            d.append(Edge(v, e_prev.helper))
        delete(t, e_prev, polygon.previous_vertex(v))
    
    def handle_split_vertex(v):
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
        insert(t, e, v)
    
    def handle_merge_vertex(v):
        nonlocal t, d, polygon, left_count
        e_prev = polygon.previous_edge(v)
        if(e_prev.helper is not None and e_prev.helper.v_type == "merge"):
            d.append(Edge(v, e_prev.helper))
        delete(t, e_prev, polygon.previous_vertex(v))
        left = find_left(t, v)
        if(debug):
            left_count += 1
            if(left_count >= left_stop):
                plot_diags(polygon.get_vertices(), [left], v, title = left_count)
        if(left.helper.v_type == "merge"):
            d.append(Edge(v, left.helper))
        left.helper = v
    
    def handle_regular_down_vertex(v):
        nonlocal t, d, polygon
        e_prev = polygon.previous_edge(v) 
        if(e_prev.helper is not None and e_prev.helper.v_type == "merge"):
            d.append(Edge(v, e_prev.helper))
        delete(t, e_prev, polygon.previous_vertex(v))
        e = polygon.get_edge(v)
        e.helper = v
        insert(t, e, v)
    
    def handle_regular_up_vertex(v):
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
    https://stackoverflow.com/questions/693837/how-to-determine-a-diagonal-is-in-or-out-of-a-concave-polygon
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
        # If v1 and v2 are consecutive they can't be diagonal
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
    https://stackoverflow.com/questions/9455875/how-to-split-a-polygon-along-n-given-diagonals
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
    Derived from: 
    de Berg, van Kreveld, Overmars, Schwrzkopf 'Computational geometry'
    Section 3.3
    """

    def same_chain(v1, v2, polygon):
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
        vert = polygon[:]
        vert.sort(key = lambda pt: (pt.y, -pt.x))
        vert.reverse()
        return vert[:]

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


if(__name__ == "__main__"):
    # polygon = [Vertex(1, 1), Vertex(3, 0), Vertex(2, 2), \
    #            Vertex(4, 3), Vertex(5, 1), Vertex(6, 5), \
    #            Vertex(2, 5)]

    # polygon = [Vertex(0, 3), Vertex(1, 1), Vertex(3, 2), \
    #            Vertex(5, 1), Vertex(6, 3), Vertex(4, 4), \
    #            Vertex(3, 3), Vertex(1, 4)]

    # polygon = [Vertex(0, 4), Vertex(2, 2), Vertex(3, 3), \
    #            Vertex(6, 0), Vertex(5, 5), Vertex(7, 4), \
    #            Vertex(9, 8), Vertex(6, 7), Vertex(6, 10), \
    #            Vertex(4, 9), Vertex(3, 10), Vertex(1, 8.7), \
    #            Vertex(3, 8), Vertex(2, 6), Vertex(1, 7)]

    # polygon = [Vertex(3.71, 9.03), Vertex(2.8, 7.08), Vertex(0.2, 6.47), \
    #            Vertex(2.66, 6.41), Vertex(2.02, 4.15), Vertex(3.86, 6.1), \
    #            Vertex(5.12, 3.58), Vertex(4.41, 6.05), Vertex(9.29, 8.12), 
    #            Vertex(4.03, 7.22)]

    # polygon = [Vertex(3.64, 9.24), Vertex(0.47, 1.05), Vertex(2.39, 3.71), \
    #            Vertex(2.78, 1.17), Vertex(3.9, 4.69), Vertex(4.27, 1.83), \
    #            Vertex(5.19, 7.42), Vertex(5.75, 2.25), Vertex(6.42, 7.15), \
    #            Vertex(7.41, 1.63), Vertex(7.56, 8.29), Vertex(5.75, 8.8), \
    #            Vertex(5.8, 9.88), Vertex(2.08, 9.64), Vertex(2.08, 8.29)]

    # polygon = [Vertex(1,4), Vertex(3,1), Vertex(4,6), \
    #            Vertex(5,2), Vertex(6,5), Vertex(6,9), \
    #            Vertex(2,8)]

    # polygon = [Vertex(2.12,8.03),Vertex(2.12,6.47),Vertex(3.24,5.86), \
    #            Vertex(2.14,4.83),Vertex(3.56,4.86),Vertex(4.36,5.76), \
    #            Vertex(4.36,4.92),Vertex(5.61,4.92),Vertex(5.61,6.54), \
    #            Vertex(6.41,6.54),Vertex(6.41,4.98),Vertex(7.54,5.66), \
    #            Vertex(6.53,7.58),Vertex(5.07,7.58),Vertex(4.19,8.32), \
    #            Vertex(3.34,7.78),Vertex(4.05,7.78),Vertex(2.76,6.92)]

    # polygon = [Vertex(3.17,8.59),Vertex(2.14,7.64),Vertex(1.46,6.34), \
    #            Vertex(1.19,4.36),Vertex(1.41,4.14),Vertex(2.63,5.59), \
    #            Vertex(3.47,4.22),Vertex(3.08,3.17),Vertex(3.39,2.36), \
    #            Vertex(5.97,2.54),Vertex(7.46,3.76),Vertex(7.46,5.53), \
    #            Vertex(5.31,5.83),Vertex(3.76,5.58),Vertex(6.03,7.9), \
    #            Vertex(9.29,7.53),Vertex(9.29,8.39),Vertex(6.68,9.44), \
    #            Vertex(5.66,8.08),Vertex(4.32,6.81),Vertex(3.44,8.31)]

    # polygon = [Vertex(2.42,7.68),Vertex(2.07,6.83),Vertex(1.71,5.46), \
    #            Vertex(1.76,4.15),Vertex(2.54,3.42),Vertex(3.92,2.93), \
    #            Vertex(5.36,2.95),Vertex(6.93,3.32),Vertex(7.0,4.29), \
    #            Vertex(6.31,5.88),Vertex(5.95,6.9),Vertex(6.78,6.66), \
    #            Vertex(7.73,5.15),Vertex(8.42,5.34),Vertex(8.54,7.1), \
    #            Vertex(7.29,8.19),Vertex(5.2,8.58),Vertex(4.19,8.36), \
    #            Vertex(3.39,8.19)]

    # polygon = [Vertex(0.97,8.71),Vertex(0.97,3.63),Vertex(8.53,3.63), \
    #            Vertex(8.53,8.51),Vertex(7.66,8.49),Vertex(6.93,8.0), \
    #            Vertex(6.46,7.27),Vertex(6.34,6.54),Vertex(5.98,5.9), \
    #            Vertex(5.25,5.88),Vertex(4.9,7.08),Vertex(5.05,8.53), \
    #            Vertex(5.07,9.22),Vertex(4.8,9.14),Vertex(4.24,8.12), \
    #            Vertex(4.12,6.98),Vertex(4.08,6.37),Vertex(3.63,5.88), \
    #            Vertex(2.76,5.93),Vertex(2.37,7.07),Vertex(1.83,8.68), \
    #            Vertex(1.66,8.9)]

    # polygon = [Vertex(1.9,2.46),Vertex(1.9,5.8),Vertex(2.27,5.75), \
    #            Vertex(2.42,4.93),Vertex(2.9,3.54),Vertex(3.51,4.47), \
    #            Vertex(4.08,6.34),Vertex(4.42,5.07),Vertex(4.86,3.46), \
    #            Vertex(5.47,4.68),Vertex(6.29,6.29),Vertex(6.81,6.25), 
    #            Vertex(6.81,2.46)]

    # polygon = [Vertex(10.0,0.0),Vertex(10.0,6.97),Vertex(9.39,7.1), \
    #            Vertex(9.03,6.63),Vertex(8.27,4.9),Vertex(7.64,3.83), \
    #            Vertex(6.73,3.42),Vertex(6.22,3.83),Vertex(6.25,5.0), \
    #            Vertex(6.31,6.34),Vertex(6.25,7.61),Vertex(5.68,8.05), \
    #            Vertex(5.42,7.85),Vertex(5.32,7.47),Vertex(5.1,6.1), \
    #            Vertex(4.95,4.71),Vertex(4.42,3.41),Vertex(3.66,2.98), \
    #            Vertex(3.53,3.31),Vertex(3.63,4.36),Vertex(3.61,5.76), \
    #            Vertex(3.53,6.88),Vertex(3.0,7.75),Vertex(2.81,7.68), \
    #            Vertex(2.61,6.83),Vertex(2.58,5.56),Vertex(2.51,4.64), \
    #            Vertex(2.49,4.14),Vertex(1.76,3.05),Vertex(1.54,3.07),
    #            Vertex(1.37,3.19),Vertex(1.05,4.08),Vertex(1.0,4.75), \
    #            Vertex(0.95,5.34),Vertex(0.85,5.93),Vertex(0.71,6.61), \
    #            Vertex(0.49,7.47),Vertex(0.39,7.63),Vertex(0.0,7.75), \
    #            Vertex(0.0,0.0)]

    # polygon = [Vertex(0.0,7.98), Vertex(0.0,0.0), Vertex(10.0,0.0), \
    #            Vertex(10.0,7.53), Vertex(9.81,7.63), Vertex(9.36,7.46), \
    #            Vertex(9.02,6.81), Vertex(8.9,6.0), Vertex(8.81,5.34), \
    #            Vertex(8.75,4.69), Vertex(8.56,4.03), Vertex(8.39,3.9), \
    #            Vertex(7.95,4.22), Vertex(7.73,5.36), Vertex(7.83,6.44), \
    #            Vertex(7.86,7.12), Vertex(8.32,7.83), Vertex(8.64,8.19), \
    #            Vertex(8.56,8.71), Vertex(6.75,8.95), Vertex(5.92,7.9), \
    #            Vertex(5.73,6.15), Vertex(6.34,3.88), Vertex(7.41,3.03), \
    #            Vertex(8.56,2.95), Vertex(8.93,2.2), Vertex(7.9,1.53), \
    #            Vertex(6.05,1.81), Vertex(4.81,2.85), Vertex(4.66,4.31), \
    #            Vertex(4.71,6.39), Vertex(4.59,7.54), Vertex(4.07,7.68), \
    #            Vertex(3.27,5.41), Vertex(2.8,3.66), Vertex(2.12,3.2), \
    #            Vertex(1.49,3.76), Vertex(1.07,6.02), Vertex(0.66,7.56)]

    # polygon = [Vertex(0.0,0.0),Vertex(0.0,8.0),Vertex(0.58,6.94),Vertex(1.11,5.92),\
    #            Vertex(1.64,4.61),Vertex(2.12,3.59),Vertex(3.14,2.77),Vertex(4.1,2.57),\
    #            Vertex(5.21,2.57),Vertex(6.47,2.72),Vertex(7.63,3.11),Vertex(8.93,3.3),\
    #            Vertex(10.04,3.3),Vertex(11.49,2.91),Vertex(13.18,2.18),Vertex(14.09,1.99),\
    #            Vertex(15.73,1.94),Vertex(16.89,1.99),Vertex(18.15,2.43),Vertex(18.97,2.72),\
    #            Vertex(20.13,3.16),Vertex(21.04,3.5),Vertex(22.78,4.08),Vertex(24.52,4.22),\
    #            Vertex(26.64,3.88),Vertex(28.86,3.16),Vertex(30.36,2.82),Vertex(31.61,2.67),\
    #            Vertex(33.69,2.67),Vertex(36.1,2.77),Vertex(38.56,2.67),Vertex(40.44,2.48),\
    #            Vertex(43.0,2.52),Vertex(44.21,2.67),Vertex(45.95,3.16),Vertex(47.01,3.79),\
    #            Vertex(47.92,4.71),Vertex(48.5,5.44),Vertex(49.18,6.46),Vertex(50.0,8.0),\
    #            Vertex(50.0,0.0)]

    # polygon = [Vertex(0.0,8.0),Vertex(1.35,7.04),Vertex(1.83,6.36),Vertex(2.41,5.53),\
    #            Vertex(2.99,4.81),Vertex(3.43,4.71),Vertex(4.63,4.61),Vertex(5.5,4.71),\
    #            Vertex(6.47,4.81),Vertex(7.24,4.95),Vertex(8.64,4.95),Vertex(10.71,4.71),\
    #            Vertex(12.69,4.71),Vertex(14.43,5.1),Vertex(15.4,5.34),Vertex(17.42,5.68),\
    #            Vertex(19.64,5.58),Vertex(21.57,5.53),Vertex(24.18,5.53),Vertex(27.17,5.39),\
    #            Vertex(29.87,4.76),Vertex(33.16,4.66),Vertex(33.74,4.66),Vertex(38.42,4.95),\
    #            Vertex(39.67,4.9),Vertex(43.15,5.1),Vertex(45.13,5.53),Vertex(46.48,5.92),\
    #            Vertex(48.41,6.75),Vertex(50.0,8.00),Vertex(49.18,6.46),Vertex(48.5,5.44),\
    #            Vertex(47.92,4.71),Vertex(47.01,3.79),Vertex(45.95,3.16),Vertex(44.21,2.67),\
    #            Vertex(43.0,2.52),Vertex(40.44,2.48),Vertex(38.56,2.67),Vertex(36.1,2.77),\
    #            Vertex(33.69,2.67),Vertex(31.61,2.67),Vertex(30.36,2.82),Vertex(28.86,3.16),\
    #            Vertex(26.64,3.88),Vertex(24.52,4.22),Vertex(22.78,4.08),Vertex(21.04,3.5),\
    #            Vertex(20.13,3.16),Vertex(18.97,2.72),Vertex(18.15,2.43),Vertex(16.89,1.99),\
    #            Vertex(15.73,1.94),Vertex(14.09,1.99),Vertex(13.18,2.18),Vertex(11.49,2.91),\
    #            Vertex(10.04,3.3),Vertex(8.93,3.3),Vertex(7.63,3.11),Vertex(6.47,2.72),\
    #            Vertex(5.21,2.57),Vertex(4.1,2.57),Vertex(3.14,2.77),Vertex(2.12,3.59),\
    #            Vertex(1.64,4.61),Vertex(1.11,5.92),Vertex(0.58,6.94)]
    
    # polygon = [Vertex(0.0,8.0),Vertex(50.0,8.0),Vertex(48.41,6.75),Vertex(46.48,5.92),\
    #            Vertex(45.13,5.53),Vertex(43.15,5.1),Vertex(39.67,4.9),Vertex(38.42,4.95),\
    #            Vertex(33.74,4.66),Vertex(33.16,4.66),Vertex(29.87,4.76),Vertex(27.17,5.39),\
    #            Vertex(24.18,5.53),Vertex(21.57,5.53),Vertex(19.64,5.58),Vertex(17.42,5.68),\
    #            Vertex(15.4,5.34),Vertex(14.43,5.1),Vertex(12.69,4.71),Vertex(10.71,4.71),\
    #            Vertex(8.64,4.95),Vertex(7.24,4.95),Vertex(6.47,4.81),Vertex(5.5,4.71),\
    #            Vertex(4.63,4.61),Vertex(3.43,4.71),Vertex(2.99,4.81),Vertex(2.41,5.53),\
    #            Vertex(1.83,6.36),Vertex(1.35,7.04)]

    with open('test_poly_1000.txt', 'r') as f:
        content = f.readlines()
    polygon_dupl = []
    for line in content:
        x, y = line.split('\t')
        polygon_dupl.append(Vertex(float(x), float(y)))
    polygon = []
    for pt in polygon_dupl:
        if(pt not in polygon):
            polygon.append(pt)

    from timeit import default_timer as timer
    polygon_obj = Polygon(polygon)
    start = timer()
    edges = make_monotone(polygon_obj)
    monotone_polygons = split_polygons(polygon_obj, edges)
    edges2 = []
    for poly in monotone_polygons:
        if(poly != []):
            edges2 += triangulate_monotone_polygon(poly)
    # tt = split_polygons(polygon_obj, edges)
    end = timer()
    print("n vertices:", len(polygon))
    print("elapsed time:", end - start)
    for i, pt in enumerate(polygon):
        plt.plot([pt.x, polygon[(i+1)%len(polygon)].x], [pt.y, polygon[(i+1)%len(polygon)].y], c = 'b')
    for e in edges:
        plt.plot([e.start.x, e.end.x], [e.start.y, e.end.y], c = 'r')
    for i, e in enumerate(edges2):
        plt.plot([e.start.x, e.end.x], [e.start.y, e.end.y], c = 'g', linewidth = 0.75)
    plt.grid()
    plt.show()
