import re

from django_rbac.engine import CheckEngine, ExpandEngine, PermissionEngine
from django_rbac.definitions import SubjectID, SubjectSet, RelationTuple
from django_rbac.utils import find_namespace_id
from django_rbac.models import KetoRelationTuples
import typing as t


def check(namespace: str, object: str, relation: str = None, subject_id: str = None, subject_set_namespace: str = None,
          subject_set_object: str = None, subject_set_relation: str = None, max_depth=-1):
    """
    Use: check <subject> <relation> <namespace> <object>
    Check whether a subject has a relation on an object.
    """
    if subject_id:
        subject = SubjectID(id=subject_id)
    else:
        assert subject_set_namespace and \
            subject_set_object and \
            subject_set_relation, "must provide subject_id or subject_set"
        subject = SubjectSet(namespace=subject_set_namespace, object=subject_set_object, relation=subject_set_relation)
    relation_tuple = RelationTuple(namespace=namespace, object=object, relation=relation)
    engine = CheckEngine()
    allowed = engine.subject_is_allowed(subject, relation_tuple, max_depth)
    return allowed


def expand(namespace: str, object: str, relation: str = None, max_depth=-1):
    """
    Use: expand <relation> <namespace> <object>
    """
    subject = SubjectSet(namespace=namespace, object=object, relation=relation)
    engine = ExpandEngine()
    tree = engine.build_tree(subject, max_depth)
    return tree


def query_permission_tree(namespace: str, domain: str, subject_id: str, max_depth=-1):
    subject = SubjectID(id=subject_id)
    engine = PermissionEngine()
    tree = engine.build_tree(namespace, domain, subject, max_depth)
    return tree


def query_permission(namespace: str, domain: str, subject_id: str, max_depth=-1) -> t.List[str]:
    tree = query_permission_tree(namespace, domain, subject_id, max_depth)
    if tree is None:
        return []
    ret = []
    queue = tree.children
    while queue:
        node = queue.pop(0)
        if node.relation == 'menu_owner':
            ret.append(re.compile(r'^/\d+/groups/(.*?)/menus/(.*?)$').findall(node.object)[0])
        queue.extend(node.children)
    return ret


def get_relation_tuples(namespace: str = None, object: str = None, relation: str = None, subject_id: str = None,
                        subject_set_namespace: str = None,
                        subject_set_object: str = None, subject_set_relation: str = None) -> t.List[RelationTuple]:
    kwargs = {}
    if namespace:
        kwargs['namespace_id'] = find_namespace_id(namespace)
    if object:
        kwargs['object'] = object
    if relation:
        kwargs['relation'] = relation
    if subject_id:
        kwargs['subject_id'] = subject_id
    if subject_set_namespace:
        kwargs['subject_set_namespace_id'] = find_namespace_id(subject_set_namespace)
    if subject_set_object:
        kwargs['subject_set_object'] = subject_set_object
    if subject_set_relation:
        kwargs['subject_set_relation'] = subject_set_relation
    rels: t.List[KetoRelationTuples] = KetoRelationTuples.objects.filter(**kwargs)
    rels: t.List[RelationTuple] = [i.to_relation_tuple() for i in rels]
    return rels
