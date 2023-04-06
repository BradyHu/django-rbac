# Register your models here.
from django.contrib import admin
from . import models


@admin.register(models.KetoRelationTuples)
class RelationTupleAdmin(admin.ModelAdmin):
    list_display = ['namespace_id', 'object', 'subject_id', 'subject_set_namespace_id', 'subject_set_object',
                    'subject_set_relation']
    search_fields = ['namespace_id', 'object', 'subject_id', 'subject_set_namespace_id', 'subject_set_object',
                     'subject_set_relation']
