from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import typing as t
import uuid
from enum import Enum


@dataclass_json
@dataclass
class Subject:
    def unique_id(self):
        raise NotImplemented

    def __eq__(self, other):
        raise NotImplemented


@dataclass_json
@dataclass
class SubjectID(Subject):
    id: str

    def unique_id(self):
        return self.id

    def __eq__(self, other):
        if type(other) != SubjectID:
            return False
        return self.id == other.id


@dataclass_json
@dataclass
class SubjectSet:
    namespace: str
    object: str
    relation: str

    def unique_id(self):
        return f'{self.namespace}{self.object}{self.relation}'

    def __eq__(self, other):
        if type(other) != SubjectSet:
            return False
        return self.namespace == other.namespace and self.object == other.object and self.relation == other.relation


@dataclass_json
@dataclass
class RelationQuery:
    namespace: str
    object: str
    relation: str
    subject: Subject


@dataclass_json
@dataclass
class RelationTuple:
    namespace: str
    object: str
    relation: str
    subject: Subject = None


class ExpandNodeType(str, Enum):
    ExpandNodeUnion = 'union'
    ExpandNodeExclusion = 'exclusion'
    ExpandNodeIntersection = 'intersection'
    ExpandNodeLeaf = 'leaf'
    ExpandNodeUnspecified = 'unspecified'


@dataclass_json
@dataclass
class Tree:
    type: str
    subject: Subject = None
    namespace: str = None
    object: str = None
    relation: str = None
    subject_id: str = None
    children: t.List['Tree'] = field(default_factory=list)
