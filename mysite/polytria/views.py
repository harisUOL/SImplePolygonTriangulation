from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from CGAL.CGAL_Kernel import Point_2
from CGAL.CGAL_Triangulation_2 import Constrained_Delaunay_triangulation_2

class FaceInfo2(object):
    def __init__(self):
        self.nesting_level = -1

    def in_domain(self):
        return (self.nesting_level % 2) != 1

def mark_domains(ct, start_face, index, edge_border, face_info):
    if face_info[start_face].nesting_level != -1:
        return
    queue = [start_face]
    while queue:
        fh = queue.pop(0)
        if face_info[fh].nesting_level == -1:
            face_info[fh].nesting_level = index
            for i in range(3):
                e = (fh, i)
                n = fh.neighbor(i)
                if face_info[n].nesting_level == -1:
                    if ct.is_constrained(e):
                        edge_border.append(e)
                    else:
                        queue.append(n)

def mark_domain(cdt):
    face_info = {face: FaceInfo2() for face in cdt.all_faces()}
    index = 0
    border = []
    mark_domains(cdt, cdt.infinite_face(), index + 1, border, face_info)
    while border:
        e = border.pop(0)
        n = e[0].neighbor(e[1])
        if face_info[n].nesting_level == -1:
            lvl = face_info[e[0]].nesting_level + 1
            mark_domains(cdt, n, lvl, border, face_info)
    return face_info

def insert_polygon(cdt, points):
    handles = [cdt.insert(point) for point in points]
    for i in range(len(points)):
        cdt.insert_constraint(handles[i], handles[(i + 1) % len(points)])

def home(request):
    return render(request, 'polytria/home.html')

def about(request):
    return render(request, 'polytria/about.html')

def result(request):
    if request.method == 'POST':
        coordinates = json.loads(request.body)
        points = [Point_2(coord['x'], coord['y']) for coord in coordinates]

        cdt = Constrained_Delaunay_triangulation_2()
        insert_polygon(cdt, points)

        face_info = mark_domain(cdt)
        edges = []
        for edge in cdt.finite_edges():
            segment = cdt.segment(edge)
            source = segment.source()
            target = segment.target()
            edges.append({'source': (source.x(), source.y()), 'target': (target.x(), target.y())})

        # Store edges in session
        request.session['edges'] = edges

        return JsonResponse({'redirect': True})

    edges = request.session.get('edges', [])
    return render(request, 'polytria/result.html', {'edges': json.dumps(edges)})
