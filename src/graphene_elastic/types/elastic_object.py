import graphene
from ..constants import DYNAMIC_CLASS_NAME_PREFIX
from ..converter import convert_elasticsearch_field
from graphene.types import ObjectType
from six import iteritems

__all__ = ("generate_dynamic_elastic_object_type",)


def counter():
    count = 0

    def c():
        nonlocal count
        count += 1
        return count

    return c


obj_counter = counter()


def get_object_fields_mapping(field):
    properties = field._mapping.properties.properties
    return properties.to_dict()


def generate_dynamic_elastic_object_type(field, registry=None):
    """Generate an InputObjectType by field's properties

    :param field: 
    :registry:
    :return InputObjectType:
    """

    mapping = get_object_fields_mapping(field)

    data = {
        name: convert_elasticsearch_field(_field)
        for name, _field in iteritems(mapping)
    }

    cls = type(
        "{}{}ObjectNode{}".format(
            DYNAMIC_CLASS_NAME_PREFIX,
            field.name.capitalize(),
            obj_counter()
        ),
        (ObjectType,),
        data
    )

    if field.name == "nested":
        cls = graphene.List(cls)

    return cls
