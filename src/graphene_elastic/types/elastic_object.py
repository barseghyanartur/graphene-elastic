from .json_string import ElasticJSONString

__all__ = ("ElasticObject",)


class ElasticObject(ElasticJSONString):
    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        print(options, "*" * 78)
        super(ElasticObject, cls).__init_subclass_with_meta__(**options)
