# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
import requests
import simplejson
from django.conf import settings

def get_pvwatts_production(latitude, longitude, capacity, module_type=1, losses=5,
                           array_type=1, tilt=5, azimuth=180):
    params = {
        'api_key': settings.PVWATTS_API_KEY,
        'system_capacity': capacity,
        'losses': losses,
        'array_type': array_type,
        'tilt': tilt,
        'azimuth': azimuth,
        'module_type': module_type,
        'lat': latitude,
        'lon': longitude,
    }
    response = requests.get('https://developer.nrel.gov/api/pvwatts/v6.json', params=params)
    if response.status_code == requests.codes.ok:
        return {'success': True, 'production': response.json()['outputs']['ac_annual']}
    return {'success': False, 'code': response.status_code, 'body': response.json()['errors']}

def pvwatts_buildings(buildings):
    updated = 0
    for building in buildings:
        lat = None
        lng = None
        capacity = 0
        errors = []
        if 'Lat' in building.extra_data:
            lat = building.extra_data['Lat']
        else:
            errors.append('Property has no Lat column defined')
        if 'Long' in building.extra_data:
            lng = building.extra_data['Long']
        else:
            errors.append('Property has no Long column defined')
        if 'CAP Electric PV' in building.extra_data:
            capacity = building.extra_data['CAP Electric PV']
            capacity = simplejson.loads(capacity)['quantity']
        else:
            errors.append('Property has no CAP Electric PV column defined')
        if len(errors) > 0:
            return JsonResponse({'status': 'error', 'errors': errors}, status=422)
        r = utils.get_pvwatts_production(lat, lng, capacity)
        if r['success']:
            production = r['production']
            updated += 1
        return updated, len(buildings) - updated
