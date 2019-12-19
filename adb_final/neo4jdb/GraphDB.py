from py2neo import *


class GraphDB():

    def __init__(self, host, u, p):
        self.db = Graph(host, username=u, password=p)
    

    def cql(self, cql_command=''):
        return self.db.run(cql_command).data()


    def get(self, node_name, orderby='', limit='', skip='', alias='n'):
        if orderby != '':
            orderby = 'ORDER BY n.' + orderby
        if limit != '':
            limit = 'LIMIT ' + str(limit)
        if skip != '':
            skip = 'SKIP ' + str(skip)
        return self.db.run('MATCH (%s:%s) RETURN %s %s %s %s' % (alias,node_name, alias, orderby, skip, limit)).data()


    def get_relationship(self, node1, node2, relationship, target='a', orderby='', limit='', skip=''):
        # example: get_relationship('Course {course_id:100}', 'Related_domain_area', ':isRELATEDto', 'b')
        # example: get_relationship('Course {course_id:100}', 'Related_domain_area', ':isRELATEDto', 'b', limit=10)
        if orderby != '':
            orderby = 'ORDER BY ' + target + '.' + orderby
        if limit != '':
            limit = 'LIMIT ' + str(limit)
        if skip != '':
            skip = 'SKIP ' + str(skip)
        print('MATCH (a:%s)-[%s]-(b:%s) return %s %s %s %s' % (node1, relationship, node2, target, orderby, skip, limit))
        return self.db.run('MATCH (a:%s)-[%s]-(b:%s) RETURN %s %s %s %s' % (node1, relationship, node2, target, orderby, skip, limit)).data()


    def take_course(self, username, course_id):
        user = list(self.db.nodes.match('User', username=username))[0]
        course = list(self.db.nodes.match('Course', course_id=int(course_id)))[0]
        TAKES = Relationship.type('TAKES')
        r = TAKES(user, course)
        self.db.create(r)


    def drop_course(self, username, course_id):
        user = list(self.db.nodes.match('User', username=username))[0]
        course = list(self.db.nodes.match('Course', course_id=int(course_id)))[0]
        r = list(self.db.relationships.match([user, course], 'TAKES'))[0]
        self.db.separate(r)