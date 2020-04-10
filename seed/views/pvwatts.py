# !/usr/bin/env python
# encoding: utf-8

# from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from seed.decorators import ajax_request_class

from seed.lib.superperms.orgs.decorators import has_perm_class
from seed.models import Organization

from seed.models.properties import PropertyState
from seed.models.tax_lots import TaxLotState

from seed.utils.api import api_endpoint_class
from seed.utils.pvwatts import pvwatts_buildings


class PvwattsViews(viewsets.ViewSet):

    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('can_modify_data')
    @action(detail=False, methods=['POST'])
    def pvwatts_by_ids(self, request):
        body = dict(request.data)
        property_ids = body.get('property_ids')
        taxlot_ids = body.get('taxlot_ids')
        org_id = body.get('org_id')
        organization = Organization.objects.get(id=org_id)

        result = {}

        if property_ids:
            properties = PropertyState.objects.filter(id__in=property_ids)
            calculated, exists, not_calculated, errors = pvwatts_buildings(properties, organization)
            result = JsonResponse({
                'not_calculated': not_calculated,
                'calculated': calculated,
                'exists': exists,
                'errors': errors
            })

        if taxlot_ids:
            taxlots = TaxLotState.objects.filter(id__in=taxlot_ids)
            calculated, not_calculated = pvwatts_buildings(taxlots, organization)
            result["taxlots"] = {
                'not_calculated': not_calculated,
                'calculated': calculated,
                'exists': exists
            }
        return result
