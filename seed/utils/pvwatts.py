# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
import datetime
import requests
import simplejson
from django.core.exceptions import ValidationError
from django.conf import settings
from seed.models import Measure, PropertyMeasure
from helix.models import HelixMeasurement

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
        property_measures = building.propertymeasure_set.filter(measure_id=measure.id)
        property_measure = None
        if property_measures.exists():
            property_measure = property_measures.get()
            current_production = property_measure.measurements.filter(measurement_type='PROD')
            if current_production.exists():
                # Already exists
                continue

        if 'Lat' in building.extra_data:
            lat = building.extra_data['Lat']
        else:
            errors.append(ValidationError('Property has no Lat column defined',
                                          code='invalid'))
        if 'Long' in building.extra_data:
            lng = building.extra_data['Long']
        else:
            errors.append(ValidationError('Property has no Long column defined',
                                          code='invalid'))
        if property_measure:
            capacity = property_measure.measurements.get(measurement_type='CAP').quantity
        elif 'CAP Electric PV' in building.extra_data:
            capacity = building.extra_data['CAP Electric PV']
            capacity = simplejson.loads(capacity)['quantity']
        else:
            errors.append(ValidationError('Property has no CAP Electric PV column defined',
                                          code='invalid'))
        if len(errors) > 0:
            raise ValidationError(errors)
        r = utils.get_pvwatts_production(lat, lng, capacity)
        if r['success']:
            updated += 1
            production = r['production']
            if property_measure == None:
                property_measure = PropertyMeasure(measure=measure,
                                                   property_measure_name='install_photovoltaic_system',
                                                   property_state=building,
                                                   implementation_status=PropertyMeasure.MEASURE_COMPLETED)
                property_measure.save()
            measurement = HelixMeasurement(measure_propety=property_measure,
                                           measurement_type='PROD',
                                           measurement_subtype='PV',
                                           fuel='ELEC',
                                           quantity=production,
                                           unit='KWH',
                                           status='ESTIMATE',
                                           year=datetime.date.today().year)
            measurement.save()
    return updated, len(buildings) - updated
