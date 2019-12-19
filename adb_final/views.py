from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from .forms import *
from .neo4jdb.GraphDB import GraphDB
from pprint import pprint
from urllib.parse import parse_qs, urlparse, quote
import json

db = GraphDB('bolt://140.114.233.144:7687', 'neo4j', 'isaac0625')


def login(request):
    # TODO: user validation
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            validation = ['kch062522@gmail.com',
                          '108065402']  # fake user entrance
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password'].strip()
            print('Request /login/: username=', username, 'password=',
                  password)

            # if username == validation[0] and password == validation[1]:
            user = db.get('User {username:%s, passwd:%s}' % (('\'' + username + '\''), ('\'' + password + '\'')))
            print(user)
            if user:
                request.session['authenticated'] = True
                request.session['username'] = username
                return HttpResponseRedirect('../home/')
            else:
                request.session['authenticated'] = False
                return render(request, "index.html", {'invalid': True})


def logout(request):
    if request.method == 'GET':
        request.session['authenticated'] = False
        return HttpResponseRedirect('/')


def home(request):
    if request.session['authenticated']:
        return render(request, 'home.html', {
            'username': request.session['username'],
            'maincontent': 'user_home.html', 
        })
    else:
        return HttpResponseRedirect('/')



def find_course(request):
    courses = []
    if request.method == 'GET':
        if request.session['authenticated']:
            URL_QS = request.build_absolute_uri()
            qs = parse_qs(urlparse(URL_QS).query)
            CQL_COMMAND = 'MATCH (n:Course) WHERE '
            WHERE_CLAUSE = ''
            if qs:
                items = list(qs.items())
                for item in items:
                    key = item[0]
                    values = item[1]
                    WHERE_CLAUSE += '('
                    for value in values:
                        WHERE_CLAUSE += 'lower(n.%s) CONTAINS \'%s\'' % (key, value.lower())
                        if value != values[-1]:
                            WHERE_CLAUSE += ' OR '
                    WHERE_CLAUSE += ')'
                    if item != items[-1]:
                        WHERE_CLAUSE += ' AND '
                CQL_COMMAND += WHERE_CLAUSE + ' RETURN n'
                courses = db.cql(CQL_COMMAND)
            return render(request, 'home.html', {
                'username': request.session['username'],
                'maincontent': 'find_course.html', 
                'courses': courses
            })
        else:
            return HttpResponseRedirect('/')



def history(request):
    if request.method == 'GET':
        if request.session['authenticated']:
            courses = db.get_relationship('User {username:%s}' % ('\'' + request.session['username'] + '\''), 'Course', ':TAKES', 'b', orderby='course_id')
            return render(request, 'home.html', {
                'title': 'History',
                'username': request.session['username'],
                'maincontent': 'info.html', 
                'courses': courses
            })
        else:
            return HttpResponseRedirect('/')



def take_course(request):
    if request.method == 'POST':
        form = TakeCourseForm(request.POST)
        if form.is_valid() and request.session['authenticated']:
            username = form.cleaned_data['username']
            course_id = form.cleaned_data['course_id']
            already = db.get_relationship('User {username:\'%s\'}' % username,'Course {course_id:%s}' % course_id,'TAKES',target='b.course_id')
            if not already:
                db.take_course(username, course_id)
                return HttpResponse(status=201)
            else:
                return HttpResponse(status=202)



def drop_course(request):
    if request.method == 'POST':
        form = DropCourseForm(request.POST)
        if form.is_valid() and request.session['authenticated']:
            username = form.cleaned_data['username']
            course_id = form.cleaned_data['course_id']
            db.drop_course(username, course_id)
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=404)



def info(request):
    courses = []
    if request.method == 'GET':
        if request.session['authenticated']:
            URL_QS = request.build_absolute_uri()
            qs = parse_qs(urlparse(URL_QS).query)
            key = list(qs.items())[0][0]
            value = list(qs.items())[0][1][0]
            # print(key, value)
            if key == 'instructor':
                courses = db.get_relationship('Instructor {instructor_name:\'%s\'}' % (value), 'Course', ':TEACHS', 'b')
                title = 'Instructor: ' + value
            if key == 'provider':
                courses = db.get('Course {provider:\'%s\'}' % (value),alias='b')
                title = 'Provider: ' + value
            if key == 'language':
                courses = db.get('Course {language:\'%s\'}' % (value),alias='b')
                title = 'Language: ' + value
            if key == 'related_domain':
                courses = db.get_relationship('Related_domain_area {domain_area:\'%s\'}' % (value), 'Course', ':isRELATEDto', 'b')
                title = 'Related Domain Area: ' + value
            return render(request, 'home.html', {
                'title': title,
                'username': request.session['username'],
                'maincontent': 'info.html', 
                'courses': courses,
            })
        else:
            return HttpResponseRedirect('/')



def related_domain(request):
    if request.method == 'GET':
        if request.session['authenticated']:
            URL_QS = request.build_absolute_uri()
            qs = parse_qs(urlparse(URL_QS).query)
            key = list(qs.items())[0][0]
            value = list(qs.items())[0][1][0]
            related_domain = db.get_relationship('Course {course_id:%s}' % (value), 'Related_domain_area', ':isRELATEDto', 'b')
            related_domain = [domain['b']['domain_area'] for domain in related_domain]
            print(related_domain)
            return HttpResponse(json.dumps(related_domain),content_type="application/text")


