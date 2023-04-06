from django.conf import settings
from django_rbac.models import KetoRelationTuples
from django_rbac import definitions
from django_rbac import utils
import typing as t


class GraphMixin:
    def __init__(self):
        super().__init__()
        self.visited = set()

    def check_and_add_visited(self, id: str):
        if id in self.visited:
            return True
        else:
            self.visited.add(id)
            return False


class CheckEngine(GraphMixin):
    def _subject_is_allowed(self, requested: definitions.Subject, rels: t.List[definitions.RelationTuple],
                            rest_depth: int) -> bool:
        for sr in rels[:]:
            was_already_visited = self.check_and_add_visited(sr.subject.unique_id())

            if was_already_visited:
                continue

            if requested == sr.subject:
                return True
            sub = sr.subject
            if not isinstance(sub, definitions.SubjectSet):
                continue

            allowed = self.check_one_indirection_further(requested, definitions.RelationTuple(
                object=sub.object,
                relation=sub.relation,
                namespace=sub.namespace
            ), rest_depth - 1)

            if allowed:
                return True

        return False

    def check_one_indirection_further(self, requested: definitions.Subject, expand_query: definitions.RelationTuple,
                                      rest_depth: int) -> bool:
        if rest_depth == 0:
            return False
        next_rels: t.List[KetoRelationTuples] = KetoRelationTuples.objects.filter(
            namespace_id=utils.find_namespace_id(expand_query.namespace),
            object=expand_query.object,
            relation=expand_query.relation
        )
        next_rels: t.List[definitions.RelationTuple] = [i.to_relation_tuple() for i in next_rels]

        allowed = self._subject_is_allowed(requested, next_rels, rest_depth)
        if allowed:
            return allowed

        return False

    def subject_is_allowed(self, subject: definitions.Subject, r: definitions.RelationTuple, rest_depth=-1) -> bool:
        global_max_depth = getattr(settings, 'KETO_MAX_INDIRECTION_DEPTH', 32)
        if rest_depth <= 0 or rest_depth > global_max_depth:
            rest_depth = global_max_depth
        return self.check_one_indirection_further(subject, r, rest_depth)


class ExpandEngine(GraphMixin):
    def build_tree(self, subject: definitions.Subject, rest_depth) -> t.Optional[definitions.Tree]:
        global_max_depth = getattr(settings, 'KETO_MAX_INDIRECTION_DEPTH', 32)
        if rest_depth <= 0 or rest_depth > global_max_depth:
            rest_depth = global_max_depth
        is_user_set = isinstance(subject, definitions.SubjectSet)
        if is_user_set:
            was_already_visited = self.check_and_add_visited(subject.unique_id())
            if was_already_visited:
                return
            subTree = definitions.Tree(
                type=definitions.ExpandNodeType.ExpandNodeUnion,
                subject=subject
            )
            # TODO: implement
            rels: t.List[KetoRelationTuples] = KetoRelationTuples.objects.filter(
                relation=subject.relation,
                namespace_id=utils.find_namespace_id(subject.namespace),
                object=subject.object
            )
            if len(rels) == 0:
                return
            rels: t.List[definitions.RelationTuple] = [i.to_relation_tuple() for i in rels]
            if rest_depth <= 1:
                subTree.type = definitions.ExpandNodeType.ExpandNodeLeaf
                return subTree
            children = []
            for r in rels:
                child = self.build_tree(r.subject, rest_depth - 1)
                if child is None:
                    child = definitions.Tree(
                        type=definitions.ExpandNodeType.ExpandNodeLeaf,
                        subject=r.subject
                    )
                children.append(child)
            subTree.children = children
            return subTree


class PermissionEngine(GraphMixin):
    def build_tree(self, namespace, domain, subject: definitions.Subject, rest_depth) -> t.Optional[definitions.Tree]:
        global_max_depth = getattr(settings, 'KETO_MAX_INDIRECTION_DEPTH', 32)
        if rest_depth <= 0 or rest_depth > global_max_depth:
            rest_depth = global_max_depth
        is_user_set = isinstance(subject, definitions.SubjectSet)
        was_already_visited = self.check_and_add_visited(subject.unique_id())
        if was_already_visited:
            return
        if is_user_set:
            subTree = definitions.Tree(
                type=definitions.ExpandNodeType.ExpandNodeUnion,
                namespace=subject.namespace,
                relation=subject.relation,
                object=subject.object
            )
            # TODO: implement
            rels: t.List[KetoRelationTuples] = KetoRelationTuples.objects.filter(
                subject_set_namespace_id=utils.find_namespace_id(subject.namespace),
                subject_set_object=subject.object,
                subject_set_relation=subject.relation,
                object__startswith=domain
            )
        else:
            # user id
            subTree = definitions.Tree(
                type=definitions.ExpandNodeType.ExpandNodeUnion,
                subject_id=subject.id,
            )
            # TODO: implement
            rels: t.List[KetoRelationTuples] = KetoRelationTuples.objects.filter(
                namespace_id=utils.find_namespace_id(namespace),
                subject_id=subject.id,
                object__startswith=domain
            )
        if len(rels) == 0:
            return
        rels: t.List[definitions.RelationTuple] = [i.to_relation_tuple() for i in rels]
        if rest_depth <= 1:
            subTree.type = definitions.ExpandNodeType.ExpandNodeLeaf
            return subTree
        children = []
        for r in rels:
            subject = definitions.SubjectSet(
                object=r.object,
                relation=r.relation,
                namespace=r.namespace
            )
            child = self.build_tree(r.namespace, domain, subject, rest_depth - 1)
            if child is None:
                child = definitions.Tree(
                    type=definitions.ExpandNodeType.ExpandNodeLeaf,
                    object=r.object,
                    relation=r.relation,
                    namespace=r.namespace
                )
            children.append(child)
        subTree.children = children
        return subTree
