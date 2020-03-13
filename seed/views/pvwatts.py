# !/usr/bin/env python
# encoding: utf-8

from rest_framework import viewsets
from rest_framework.decorators import list_route

from seed.decorators import ajax_request_class

from seed.lib.superperms.orgs.decorators import has_perm_class

from seed.models.properties import PropertyState
from seed.models.tax_lots import TaxLotState

from seed.utils.api import api_endpoint_class


class PvwattsViews(viewsets.ViewSet):

    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('can_modify_data')
    @list_route(methods=['POST'])
    def pvwatts_by_ids(self, request):
        body = dict(request.data)
        property_ids = body.get('property_ids')
        taxlot_ids = body.get('taxlot_ids')

        if property_ids:
            properties = PropertyState.objects.filter(id__in=property_ids)
# plug in to calculation here, e.g pvwatts_buildings(properties)

        if taxlot_ids:
            taxlots = TaxLotState.objects.filter(id__in=taxlot_ids)
# plug in to calculation here, e.g. pvwatts_buildings(taxlots)

    @ajax_request_class
    @list_route(methods=['POST'])
    def results_summary(self, request):
        body = dict(request.data)
        property_ids = body.get('property_ids')
        tax_lot_ids = body.get('tax_lot_ids')

        result = {}

        if property_ids:
            result["properties"] = {
                'not_calculated': 10,
                'calculated': 20
            }

        if tax_lot_ids:
            result["tax_lots"] = {
                'not_calculated': 10,
                'calculated': 20
            }

        return result
