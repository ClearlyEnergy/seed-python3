# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
import datetime
import requests
# from django.core.exceptions import ValidationError
from django.conf import settings
from seed.models import Measure
from helix.models import HelixMeasurement


def get_pvwatts_production(latitude, longitude, capacity, module_type=1, losses=14,
                           array_type=1, azimuth=180):
    params = {
        'api_key': settings.PVWATTS_API_KEY,
        'system_capacity': capacity,
        'losses': losses,
        'array_type': array_type,
        'tilt': 20,
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
    exists = 0
    errors = []
    # May fail if it doesn't get exist
    measure = Measure.objects.get(name='install_photovoltaic_system',
                                  category='renewable_energy_systems',
                                  organization_id=organization.id)

    for building in buildings:
        lat = None
        lng = None
        capacity = 0
        property_measures = building.propertymeasure_set.filter(measure_id=measure.id)

        if building.latitude:
            lat = building.latitude
        elif 'Lat' in building.extra_data:
            lat = building.extra_data['Lat']
        else:
            errors.append('Property at ' + building.address_line_1 + ' has no latitude column defined')
#            errors.append(ValidationError('Property has no latitude column defined',
#                                          code='invalid'))
        if building.longitude:
            lng = building.longitude
        elif 'Long' in building.extra_data:
            lng = building.extra_data['Long']
        else:
            errors.append('Property ' + building.address_line_1 + ' has no longitude column defined')
#            errors.append(ValidationError('Property has no longitude column defined',
#                                          code='invalid'))

        if property_measures.exists():
            for property_measure in property_measures:
                current_production = property_measure.measurements.filter(measurement_type='PROD')
                if current_production.exists() and current_production.first().quantity is not None:
                    # Already exists
                    exists += 1
                    continue

                capacity = property_measure.measurements.get(measurement_type='CAP').quantity
                r = get_pvwatts_production(lat, lng, capacity)
                if r['success']:
                    updated += 1
                    production = round(r['production'])
                    measurement = HelixMeasurement(measure_property=property_measure,
                                                   measurement_type='PROD',
                                                   measurement_subtype='PV',
                                                   fuel='ELEC',
                                                   quantity=production,
                                                   unit='KWH',
                                                   status='ESTIMATE',
                                                   year=datetime.date.today().year)
                    measurement.save()
                    building.extra_data['Measurement Production Quantity'] = production
                    building.save()
        else:
            errors.append('Property ' + building.address_line_1 + ' has no solar capacity defined')
#            errors.append(ValidationError('Property has no solar capacity defined',
#                                          code='invalid'))

    return updated, exists, len(buildings) - updated - exists, errors
