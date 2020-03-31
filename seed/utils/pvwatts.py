# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
import requests
import simplejson
from django.conf import settings
from seed.models import Measure

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

def pvwatts_buildings(buildings, organization):
    updated = 0
    # May fail if it doesn't get exist
    measure = Measure.objects.get(name='install_photovoltaic_system',
                                  category='renewable_energy_systems',
                                  organization_id=organization.id)
    for building in buildings:
        lat = None
        lng = None
        capacity = 0
        errors = []
        property_measure = building.propertymeasure_set.filter(measure_id=measure.id)
        # This should check if the production measurement type in the measure and continue
        # if the quantity is defined.
        if len(property_measure) > 0:
            # Already exists
            continue

        if 'Lat' in building.extra_data:
            lat = building.extra_data['Lat']
        else:
            errors.append('Property has no Lat column defined')
        if 'Long' in building.extra_data:
            lng = building.extra_data['Long']
        else:
            errors.append('Property has no Long column defined')
        # Get capacity from install_photovoltaic_system Measure in the capacity measurement
        # Replacing this:
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
