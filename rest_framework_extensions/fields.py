from rest_framework.relations import HyperlinkedIdentityField


class ResourceUriField(HyperlinkedIdentityField):
    """
    Represents a hyperlinking uri that points to the
    detail view for that object.

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
