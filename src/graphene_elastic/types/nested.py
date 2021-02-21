from graphene.types.field import Field


class NestedField(Field):
    # TODO: 动态的Nested Field可以直接承载nested

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        super(NestedField, cls).__init_subclass_with_meta__(**options)
