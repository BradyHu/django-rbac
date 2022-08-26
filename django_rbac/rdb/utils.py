import os

import yaml


def parse_keto_file(filepath):
    with open(filepath, 'r') as f:
        keto_file = yaml.safe_load(f)
    return keto_file


keto_definition = parse_keto_file(
    os.path.abspath(os.path.join(__file__, '../../config/keto.yml'))
)


def find_namespace(namespace_id: int):
    if namespace_id is None:
        return None
    for namespace in keto_definition.get('namespaces', []):
        if namespace.get('id') == namespace_id:
            return namespace['name']
    else:
        raise Exception({"msg": "namespace not found"})


def find_namespace_id(namespace_name: str):
    if namespace_name is None:
        return None
    for namespace in keto_definition.get('namespaces', []):
        if namespace.get('name') == namespace_name:
            return namespace['id']
    else:
        raise Exception({"msg": "namespace not found"})
