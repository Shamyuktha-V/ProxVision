import math
import xml.etree.ElementTree as ET
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import  Label
from kivy.uix.textinput import TextInput
from kivy.uix.bubble import Button

CIRCLE_TAG_NAME = '{http://www.w3.org/2000/svg}circle'
GROUP_TAG_NAME = '{http://www.w3.org/2000/svg}g'

def circle_to_point(circle):
    return (float(circle.attrib['cx']),
            float(circle.attrib['cy']), str(circle.attrib['id']))


def read_svg_file(svg_file_name):
    return ET.parse(svg_file_name)


def get_all_points(tree):
    return [circle_to_point(circle)
            for circle in tree.iter(CIRCLE_TAG_NAME)]


def get_point_by_id(tree, point_id):
    return [circle_to_point(circle)
            for circle in tree.iter(CIRCLE_TAG_NAME)
            if 'id' in circle.attrib
            if circle.attrib['id'] == point_id]


def get_group_by_id(tree, group_id):
    return [circle
            for group in tree.iter(GROUP_TAG_NAME)
            if 'id' in group.attrib
            if group.attrib['id'] == group_id
            for circle in get_all_points(group)]


def distance(point1, point2):
    x1, y1, lab1 = point1
    x2, y2, lab2 = point2

    dx = x1 - x2
    dy = y1 - y2

    return math.sqrt((dx * dx) + (dy * dy))


k = 2


def build_kdtree(points, depth=0):
    n = len(points)

    if n <= 0:
        return None

    axis = depth % k

    sorted_points = sorted(points, key=lambda point: point[axis])

    return {
        'point': sorted_points[n // 2],
        'left': build_kdtree(sorted_points[:n // 2], depth + 1),
        'right': build_kdtree(sorted_points[n // 2 + 1:], depth + 1)
    }


def closer_distance(pivot, p1, p2):
    if p1 is None:
        return p2

    if p2 is None:
        return p1

    d1 = distance(pivot, p1)
    d2 = distance(pivot, p2)

    if d1 < d2:
        return p1
    else:
        return p2


def kdtree_closest_point(root, point, depth=0):
    if root is None:
        return None

    axis = depth % k

    next_branch = None
    opposite_branch = None

    if point[axis] < root['point'][axis]:
        next_branch = root['left']
        opposite_branch = root['right']
    else:
        next_branch = root['right']
        opposite_branch = root['left']

    best = closer_distance(point,
                           kdtree_closest_point(next_branch,
                                                point,
                                                depth + 1),
                           root['point'])

    if distance(point, best) > (point[axis] - root['point'][axis]):
        best = closer_distance(point,
                               kdtree_closest_point(opposite_branch,
                                                    point,
                                                    depth + 1),
                               best)

    return best

class childApp(GridLayout):
    def _init_(self,**kwargs):
        super(childApp,self)._init_()
        self.cols=1
        self.add_widget(Label(text='Source Location',font_size=25))
        self.s_location=TextInput()
        self.add_widget(self.s_location)
        self.add_widget(Label(text='Destination Location',font_size=25))
        self.d_location = TextInput()
        self.add_widget(self.d_location)
        self.add_widget(Label(text='Boys_pg                College                Girls_pg              Hospital                Hotel\nHouse                   Park                     Office                  Restaurants          School', font_size=15))
        self.find =Button(text="Submit")
        self.find.bind(on_press = self.find_closest)
        self.add_widget(self.find)

    def find_closest(self,instance):
        svg_files = ['./points.svg']
        for svg_file in svg_files:
            svg_tree = read_svg_file(svg_file)
            [pivot] = get_point_by_id(svg_tree,self.s_location.text)
            points = get_group_by_id(svg_tree,self.d_location.text)
            kdtree = build_kdtree(points)
            nearest = kdtree_closest_point(kdtree, pivot)
            dis = distance(pivot, nearest)
            final="The nearest "+self.d_location.text+" is "+nearest[2]+"\nDistance is "+str(dis)
            self.add_widget(Label(text=final, font_size=20))

class ClosestApp(App):
     def build(self):
         return childApp()


ClosestApp().run()