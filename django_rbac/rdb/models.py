from django.db import models
from . import definitions
from .utils import find_namespace, find_namespace_id


class KetoRelationTuples(models.Model):
    namespace_id = models.IntegerField()
    object = models.CharField(max_length=64)
    relation = models.CharField(max_length=64)
    subject_id = models.CharField(max_length=64, blank=True, null=True)
    subject_set_namespace_id = models.IntegerField(blank=True, null=True)
    subject_set_object = models.CharField(max_length=64, blank=True, null=True)
    subject_set_relation = models.CharField(max_length=64, blank=True, null=True)
    commit_time = models.DateTimeField(auto_now=True)

    def to_relation_tuple(self) -> definitions.RelationTuple:
        if self.subject_id:
            subject = definitions.SubjectID(id=self.subject_id)
        else:
            subject = definitions.SubjectSet(
                namespace=find_namespace(self.subject_set_namespace_id),
                object=self.subject_set_object,
                relation=self.subject_set_relation
            )
        relation_tuple = definitions.RelationTuple(
            namespace=find_namespace(self.namespace_id),
            object=self.object,
            relation=self.relation,
            subject=subject
        )
        return relation_tuple
