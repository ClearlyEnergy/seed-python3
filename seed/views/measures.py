# !/usr/bin/env python
# encoding: utf-8
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md
"""
# import json

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.renderers import JSONRenderer

from seed.models import (
    Measure,
)
from helix.models import HELIXPropertyMeasure as PropertyMeasure
from seed.serializers.measures import MeasureSerializer, PropertyMeasureSerializer
from seed.utils.viewsets import (
    SEEDOrgModelViewSet,
    SEEDOrgCreateUpdateModelViewSet
)


# HELIX class MeasureViewSet(viewsets.ReadOnlyModelViewSet):
class MeasureViewSet(SEEDOrgModelViewSet):
    """
    API View for measures. This only includes retrieve and list since the measures are immutable.

    The reset POST method is for resetting the measures back to the default list provided
    by BuildingSync enumeration.json file.
    """
    serializer_class = MeasureSerializer
    model = Measure
    orgfilter = 'organization_id'
    parser_classes = (JSONParser, FormParser,)
    renderer_classes = (JSONRenderer,)
    filter_fields = ('category',)
    pagination_class = None

    @action(detail=False, methods=['POST'])
    def reset(self, request):
        """
        Reset all the measures back to the defaults (as provided by BuildingSync)
        ---
        parameters: {}
        type:
            organization_id:
                required: true
                type: integer
                paramType: query
            status:
                required: true
                type: string
                description: Either success or error
            measures:
                required: true
                type: list
                description: list of measures
        """
        organization_id = request.query_params.get('organization_id', None)
        if not organization_id:
            return JsonResponse({
                'status': 'error', 'message': 'organization_id not provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Measure.populate_measures(organization_id)
        data = dict(measures=list(
            Measure.objects.filter(organization_id=organization_id).order_by('id').values())
        )

        data['status'] = 'success'
        return JsonResponse(data)

    @action(detail=False, methods=['GET'])
    def categories(self, request):
        """
        Retrieves the categories of measures for an org.
        ---
        parameters:
            - name: organization_id
              description: The organization_id
              required: true
              paramType: query
        type:
            status:
                description: success or error
                type: string
                required: true
            categories:
                description: Categories of measures
                type: array of string
                required: true
        """
        org_id = int(request.query_params.get('organization_id', None))

        categories = list(Measure.objects.filter(organization_id=org_id).order_by('category').values_list('category', 'category_display_name').distinct())
        return JsonResponse({'status': 'success', 'categories': categories})


class PropertyMeasureViewSet(SEEDOrgCreateUpdateModelViewSet):
    serializer_class = PropertyMeasureSerializer
    model = PropertyMeasure
    orgfilter = 'measure__organization_id'
