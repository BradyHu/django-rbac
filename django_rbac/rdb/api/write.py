from django_rbac.rdb.utils import find_namespace_id
from django_rbac.rdb.models import KetoRelationTuples
import typing as t


def delete_relation_tuples(namespace: str = None, object: str = None, relation: str = None, subject_id: str = None,
                           subject_set_namespace: str = None, subject_set_object: str = None,
                           subject_set_relation: str = None):
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
    KetoRelationTuples.objects.filter(**kwargs).delete()


def patch_multiple_relation_tuples(array):
    for item in array:
        patch_relation_tuples(**item)


def patch_relation_tuples(action: str, namespace: str, object: str, relation: str, subject_id: str = None,
                          subject_set_namespace: str = None, subject_set_object: str = None,
                          subject_set_relation: str = None):
    if subject_id is None:
        assert subject_set_namespace is not None and subject_set_object is not None and subject_set_relation is not None, "subject_set_namespace, subject_set_object, and subject_set_relation are required when subject_id is not specified"
    if action == 'insert':
        KetoRelationTuples.objects.get_or_create(
            namespace_id=find_namespace_id(namespace),
            object=object,
            relation=relation,
            subject_id=subject_id,
            subject_set_namespace_id=find_namespace_id(subject_set_namespace),
            subject_set_object=subject_set_object,
            subject_set_relation=subject_set_relation
        )
    elif action == 'delete':
        KetoRelationTuples.objects.filter(
            namespace_id=find_namespace_id(namespace),
            object=object,
            relation=relation,
            subject_id=subject_id,
            subject_set_namespace_id=find_namespace_id(subject_set_namespace),
            subject_set_object=subject_set_object,
            subject_set_relation=subject_set_relation
        ).delete()
    else:
        raise Exception(detail={'msg': 'action must be insert or delete'})


def create_relation_tuple(namespace: str, object: str, relation: str, subject_id: str = None,
                          subject_set_namespace: str = None, subject_set_object: str = None,
                          subject_set_relation: str = None):
    if subject_id is None:
        assert subject_set_namespace is not None and subject_set_object is not None and subject_set_relation is not None, "subject_set_namespace, subject_set_object, and subject_set_relation are required when subject_id is not specified"

    instance, _ = KetoRelationTuples.objects.get_or_create(
        namespace_id=find_namespace_id(namespace),
        object=object,
        relation=relation,
        subject_id=subject_id,
        subject_set_namespace_id=find_namespace_id(subject_set_namespace),
        subject_set_object=subject_set_object,
        subject_set_relation=subject_set_relation
    )
    return instance
