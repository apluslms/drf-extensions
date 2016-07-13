# -*- coding: utf-8 -*-
# Try to import six from Django, fallback to included `six`.

from django.utils import six


from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework_extensions.etag.mixins import ReadOnlyETAGMixin, ETAGMixin
from rest_framework_extensions.utils import get_rest_framework_features
from rest_framework_extensions.bulk_operations.mixins import ListUpdateModelMixin
from rest_framework_extensions.settings import extensions_api_settings
from django.http import Http404


class DetailSerializerMixin(object):
    """
    Add custom serializer for detail view
    """
    serializer_detail_class = None
    queryset_detail = None

    def get_serializer_class(self):
        error_message = "'{0}' should include a 'serializer_detail_class' attribute".format(self.__class__.__name__)
        assert self.serializer_detail_class is not None, error_message
        if self._is_request_to_detail_endpoint():
            return self.serializer_detail_class
        else:
            return super(DetailSerializerMixin, self).get_serializer_class()

    def get_queryset(self, *args, **kwargs):
        if self._is_request_to_detail_endpoint() and self.queryset_detail is not None:
            return self.queryset_detail.all()  # todo: test all()
        else:
            return super(DetailSerializerMixin, self).get_queryset(*args, **kwargs)

    def _is_request_to_detail_endpoint(self):
        if hasattr(self, 'lookup_url_kwarg'):
            lookup = self.lookup_url_kwarg or self.lookup_field
        return lookup and lookup in self.kwargs


class PaginateByMaxMixin(object):

    def get_page_size(self, request):
        if self.page_size_query_param and self.max_page_size and request.query_params.get(self.page_size_query_param) == 'max':
            return self.max_page_size
        return super(PaginateByMaxMixin, self).get_page_size(request)


class ReadOnlyCacheResponseAndETAGMixin(ReadOnlyETAGMixin, CacheResponseMixin):
    pass


class CacheResponseAndETAGMixin(ETAGMixin, CacheResponseMixin):
    pass


class NestedViewSetMixin(object):
    """
    Adds filtering in get_page_size based on .parent_lookup_map definitions.

    Raises:
        Http404: If queryset.filter() raised ValueError.
            This happens if filter string was wrong.
    """
    def get_queryset(self):
        return self.filter_queryset_by_parents_lookups(
            super(NestedViewSetMixin, self).get_queryset()
        )

    def filter_queryset_by_parents_lookups(self, queryset):
        map_ = getattr(self, 'parent_lookup_map', {})
        kwargs = self.get_parents_query_dict() # TODO: replace with {} when removed
        for kw, filter_ in map_.items():
            filter_ = filter_.replace('.', '__')
            value = self.kwargs.get(kw, None)
            if value is not None:
                kwargs[filter_] = value
        if kwargs:
            try:
                return queryset.filter(**kwargs)
            except ValueError:
                # FIXME: should probably raise ImproperlyConfigured
                raise Http404
        else:
            return queryset

    def get_parents_query_dict(self):
        """
        Resolve legacy parent query dict.
        Deprecated in 0.2.9 and will be removed in 0.3.0
        """
        result = {}
        for kwarg_name, kwarg_value in six.iteritems(self.kwargs):
            if kwarg_name.startswith(extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX):
                query_lookup = kwarg_name.replace(
                    extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX,
                    '',
                    1
                )
                query_value = kwarg_value
                result[query_lookup] = query_value

        if result:
            # FIXME: create warning
            pass
        return result
