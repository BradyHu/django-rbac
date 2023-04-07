from django.test import TestCase
from django_rbac.api import write, read
import re
from django_rbac.definitions import SubjectID, SubjectSet, RelationTuple, Tree


class TestAPI(TestCase):
    def test_create_relation_tuple(self):
        result = write.create_relation_tuple('reports', 'finance', 'view', None, "groups", "finance", "member")
        self.assertEqual(result.namespace_id, 1)


class TestRBAC(TestCase):
    def test_check(self):
        res = read.check(subject_id='dilan', relation='view', namespace='reports', object='finance')
        self.assertEqual(res, False)
        res = read.check(subject_id='dilan', relation='view', namespace='reports', object='community')
        self.assertEqual(res, True)
        res = read.check(subject_id='dilan', relation='edit', namespace='reports', object='finance')
        self.assertEqual(res, False)

    def test_get_relation_tuples(self):
        res = read.get_relation_tuples(subject_id='dilan', relation='member')
        self.assertEqual(res, [
            RelationTuple(namespace='groups', object='community', relation='member', subject=SubjectID(id='dilan')),
            RelationTuple(namespace='groups', object='marketing', relation='member', subject=SubjectID(id='dilan'))
        ])
        res = read.get_relation_tuples(subject_set_namespace='groups', subject_set_object='marketing', subject_set_relation='member')
        self.assertEqual(res, [
            RelationTuple(namespace='reports', object='marketing', relation='view', subject=SubjectSet(namespace='groups', object='marketing', relation='member'))
        ])
        res = read.get_relation_tuples(subject_set_namespace='groups', subject_set_object='community', subject_set_relation='member')
        self.assertEqual(res, [
            RelationTuple(namespace='reports', object='community', relation='view', subject=SubjectSet(namespace='groups', object='community', relation='member'))
        ])

    def test_expand(self):
        res = read.expand(relation='view', namespace='reports', object='finance')
        self.assertEqual(
            res,
            Tree(type='union', subject=SubjectSet(namespace='reports', object='finance', relation='view'), namespace=None, object=None, relation=None, subject_id=None, children=[
                Tree(type='union', subject=SubjectSet(namespace='groups', object='finance', relation='member'), namespace=None, object=None, relation=None, subject_id=None, children=[
                    Tree(type='leaf', subject=SubjectID(id='lila'), namespace=None, object=None, relation=None, subject_id=None, children=[])
                ]),
                Tree(type='union', subject=SubjectSet(namespace='groups', object='admin', relation='member'), namespace=None, object=None, relation=None, subject_id=None, children=[
                    Tree(type='leaf', subject=SubjectID(id='neel'), namespace=None, object=None, relation=None, subject_id=None, children=[])
                ])
            ])
        )

    def test_permission(self):
        res = read.query_permission_tree('groups', "", 'dilan')
        self.assertEqual(res, Tree(
            type='union', subject=None, namespace=None, object=None, relation=None, subject_id='dilan', children=[
                Tree(type='union', subject=None, namespace='groups', object='community', relation='member', subject_id=None, children=[
                    Tree(type='leaf', subject=None, namespace='reports', object='community', relation='view', subject_id=None, children=[])
                ]),
                Tree(type='union', subject=None, namespace='groups', object='marketing', relation='member', subject_id=None, children=[
                    Tree(type='leaf', subject=None, namespace='reports', object='marketing', relation='view', subject_id=None, children=[])
                ])
            ]
        ))

    def setUp(self) -> None:
        for relation_tuple in """
// View only access for finance department
reports:finance#view@(groups:finance#member)
// View only access for community department
reports:community#view@(groups:community#member)
// View only access for marketing department
reports:marketing#view@(groups:marketing#member)
// Edit access for admin group
reports:finance#edit@(groups:admin#member)
reports:community#edit@(groups:admin#member)
reports:marketing#edit@(groups:admin#member)
reports:finance#view@(groups:admin#member)
reports:community#view@(groups:admin#member)
reports:marketing#view@(groups:admin#member)
groups:finance#member@lila
groups:community#member@dilan
groups:marketing#member@hadley
groups:admin#member@neel
groups:marketing#member@dilan
""".strip().split():
            by_id = re.match(r'^(?P<namespace>[a-z]+):(?P<object>[a-z]+)#(?P<relation>[a-z]+)@(?P<subject_id>[a-z]+)$', relation_tuple)
            if by_id:
                write.create_relation_tuple(**by_id.groupdict())
            by_subject_set = re.match(r'^(?P<namespace>[a-z]+):(?P<object>[a-z]+)#(?P<relation>[a-z]+)@'
                                      r'\((?P<subject_set_namespace>[a-z]+):(?P<subject_set_object>[a-z]+)#(?P<subject_set_relation>[a-z]+)\)$', relation_tuple)
            if by_subject_set:
                write.create_relation_tuple(**by_subject_set.groupdict())
        return super().setUp()
