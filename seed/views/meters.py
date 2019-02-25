# !/usr/bin/env python
# encoding: utf-8
# # import json
#
# from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import list_route
# from rest_framework.decorators import detail_route
# from rest_framework.parsers import JSONParser, FormParser

from seed.data_importer.meters_parsers import PMMeterParser
# from seed.decorators import require_organization_id_class
from seed.decorators import ajax_request_class
from seed.lib.mcm import reader
# from seed.lib.superperms.orgs.decorators import has_perm_class
from seed.models import ImportFile
# from seed.utils.api import api_endpoint_class


class MeterViewSet(viewsets.ViewSet):

    @ajax_request_class
    @list_route(methods=['POST'])
    def parsed_meters_confirmation(self, request):
        body = dict(request.data)
        file_id = body['file_id']
        org_id = body['organization_id']

        import_file = ImportFile.objects.get(pk=file_id)
        parser = reader.MCMParser(import_file.local_file)
        raw_meter_data = list(parser.data)

        meters_parser = PMMeterParser(org_id, raw_meter_data)

        result = {}

        result["validated_type_units"] = meters_parser.validated_type_units()
        result["proposed_imports"] = meters_parser.proposed_imports()

        return result


#     raise_exception = True
#     parser_classes = (JSONParser, FormParser)
#
#     @api_endpoint_class
#     @require_organization_id_class
#     @has_perm_class('requires_viewer')
#     def list(self, request):
#         """
#         Returns all of the meters for a property view
#         ---
#         type:
#             status:
#                 required: true
#                 type: string
#                 description: Either success or error
#             property_view_id:
#                 required: true
#                 type: integer
#                 description: property view id of the request
#             meters:
#                 required: true
#                 type: array[meters]
#                 description: list of meters for property_view_id
#         parameters:
#             - name: organization_id
#               description: The organization_id for this user's organization
#               required: true
#               paramType: query
#             - name: property_view_id
#               description: The property_view_id of the building holding the meter data
#               required: true
#               paramType: query
#         """
#         pv_id = request.GET.get('property_view_id', None)
#         org_id = request.GET.get('organization_id')
#
#         if pv_id is None:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'No property_view_id specified',
#                 'meters': []
#             })
#
#         # verify that the user has access to view property
#         pvs = PropertyView.objects.filter(id=pv_id, state__organization=org_id)
#         if pvs.count() == 0:
#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'No property_ids found for organization',
#                 'meters': []
#             })
#         else:
#             return JsonResponse({
#                 'status': 'success',
#                 'property_view_id': pv_id,
#                 'meters': [
#                     obj_to_dict(m) for m in Meter.objects.filter(property_view=pv_id)
#                 ]
#             })
#
#     @api_endpoint_class
#     @has_perm_class('requires_viewer')
#     def retrieve(self, request, pk=None):
#         """
#         Returns a single meter based on its id
#         ---
#         type:
#             status:
#                 required: true
#                 type: string
#                 description: Either success or error
#             meters:
#                 required: true
#                 type: dict
#                 description: meter object
#         parameters:
#             - name: pk
#               description: Meter primary key
#               required: true
#               paramType: path
#         """
#         meter = Meter.objects.get(pk=pk)
#         if meter:
#             res = {}
#             res['status'] = 'success'
#             res['meter'] = obj_to_dict(meter)
#             res['meter']['timeseries_count'] = meter.timeseries_set.count()
#             return JsonResponse(res)
#         else:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'No meter object found',
#             })
#
#     @api_endpoint_class
#     @require_organization_id_class
#     @has_perm_class('requires_member')
#     def create(self, request):
#         """
#         Creates a new project
#
#         :POST: Expects organization_id in query string.
#         ---
#         parameters:
#             - name: organization_id
#               description: ID of organization to associate new project with
#               type: integer
#               required: true
#               paramType: query
#             - name: property_view_id
#               description: Property view id to which to add the meter
#               required: true
#               paramType: form
#             - name: name
#               description: name of the new meter
#               type: string
#               required: true
#               paramType: form
#             - name: energy_type
#               description: type of metered energy
#               type: integer
#               required: true
#               paramType: form
#             - name: energy_units
#               description: units of energy being metered
#               type: integer
#               required: true
#               paramType: form
#         type:
#             status:
#                 required: true
#                 type: string
#                 description: Either success or error
#
#         """
#         org_id = request.GET.get('organization_id', '')
#
#         # verify that the user has access to view property
#         pv_id = request.data['property_view_id']
#         pvs = PropertyView.objects.filter(id=pv_id, state__organization=org_id)
#         if pvs.count() == 0 or pvs.count() > 1:
#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'No property id {} found for organization {}'.format(pv_id, org_id),
#             })
#         else:
#             #     energy_type = _convert_energy_data(energy_type_name, ENERGY_TYPES)
#             #     energy_units = _convert_energy_data(energy_unit_name, ENERGY_UNITS)
#             data = {
#                 "name": request.data['name'],
#                 "energy_type": request.data['energy_type'],
#                 "energy_units": request.data['energy_units'],
#                 "property_view": pvs.first(),
#             }
#             m = Meter.objects.create(**data)
#
#             return JsonResponse({
#                 'status': 'success',
#                 'meter': obj_to_dict(m),
#             })
#
#     @api_endpoint_class
#     @has_perm_class('requires_viewer')
#     def timeseries(self, request, pk=None):
#         """
#         Returns timeseries for meter
#         ---
#         type:
#             status:
#                 required: true
#                 type: string
#                 description: Either success or error
#             meter:
#                 required: true
#                 type: dict
#                 description: meter information
#             data:
#                 required: true
#                 type: list
#                 description: timeseries information
#         parameters:
#             - name: pk
#               description: Meter primary key
#               required: true
#               paramType: path
#         """
#         meter = Meter.objects.get(pk=pk)
#         res = {
#             'status': 'success',
#             'meter': obj_to_dict(meter),
#         }
#         res['meter']['data'] = []
#
#         ts = meter.timeseries_set.order_by('begin_time')
#         for t in ts:
#             res['meter']['data'].append({
#                 'begin': str(t.begin_time),
#                 'end': str(t.begin_time),
#                 'value': t.reading,
#             })
#
#         return JsonResponse(res)
#
#     @api_endpoint_class
#     @has_perm_class('can_modify_data')
#     @detail_route(methods=['POST'])
#     def add_timeseries(self, request, pk=None):
#         """
#         Returns timeseries for meter
#         ---
#         type:
#             status:
#                 required: true
#                 type: string
#                 description: Either success or error
#             meter:
#                 required: true
#                 type: dict
#                 description: meter information
#             timeseries:
#                 required: true
#                 type: list
#                 description: timeseries information
#         parameters:
#             - name: pk
#               description: Meter primary key
#               required: true
#               paramType: path
#         """
#         # TODO: Finish implementing this
#         return JsonResponse({
#             'status': 'success',
#             'message': 'Not yet implemented'
#         })
