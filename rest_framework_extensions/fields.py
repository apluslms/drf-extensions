# -*- coding: utf-8 -*-
from rest_framework.relations import (
    HyperlinkedRelatedField,
    HyperlinkedIdentityField,
)
import functools

class ResourceUriField(HyperlinkedIdentityField):
    """
    Represents a hyperlinking uri that points to the detail view for that object.

    Example:
        class SurveySerializer(serializers.ModelSerializer):
            resource_uri = ResourceUriField(view_name='survey-detail')

            class Meta:
                model = Survey
                fields = ('id', 'resource_uri')

        ...
        {
            "id": 1,
            "resource_uri": "http://localhost/v1/surveys/1/",
        }
    """
    pass


class NestedHyperlinkedRelatedField(HyperlinkedRelatedField):
    """
    Handles HyperlinkedRelatedField with views that are nested.

    Args:
        lookup_field: Item specifig overwrite to resolve url kwarg value.
            Default is looked from view class attribute with same name.
        lookup_url_kwarg: Item specifig overwrite to define url pattern argument name.
            Default is looked from view class attribute with same name.
        lookup_map: Item specifig mapping how to resolve url kwargs for named view.
            We also resolve .parent_lookup_map from view class.
    """
    def __init__(self, **kwargs):
        self.lookup_map = kwargs.pop('lookup_map', {})
        self._lookup_field = kwargs.get('lookup_field', None)
        self._lookup_url_kwarg = kwargs.get('lookup_url_kwarg', None)
        super(NestedHyperlinkedRelatedField, self).__init__(**kwargs)

    def get_url(self, obj, view_name, request, format):
        # Unsaved objects will not have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        view = self.context.get('view', None)

        assert view is not None, (
            "`%s` requires the view in the serializer context. "
            "Add `context={'view': view}` when instantiating the serializer. "
            % (self.__class__.__name__,)
        )

        # Use lookup_field and lookup_url_kwarg in order from:
        # init argument, view class or default from parent
        lookup_field = self._lookup_field or getattr(view, 'lookup_field', self.lookup_field)
        lookup_url_kwarg = self._lookup_url_kwarg or getattr(view, 'lookup_url_kwarg', self.lookup_url_kwarg)
        map_ = {lookup_url_kwarg: lookup_field}
        map_.update(getattr(view, 'parent_lookup_map', {}))
        map_.update(self.lookup_map)

        # function to traverse value for source like "foo.bar"
        getattrd = lambda obj, name: functools.reduce(getattr, name.split("."), obj)

        kwargs = dict((
            (key, getattrd(obj, source)) for (key, source) in map_.items()
        ))

        # TODO: better error reporting
        #print("view: %r\nkwargs: %r" % (view, kwargs,))
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class NestedHyperlinkedIdentityField(NestedHyperlinkedRelatedField, HyperlinkedIdentityField):
    pass
