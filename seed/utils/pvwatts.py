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

def get_ceapi_solarnpv(postal_code, state, lat, lng, capacity, year_installed, solar_production):
    params = {
        'ceapikey': settings.CE_API_KEY, 
        'zipcode': postal_code, 
        'state': state, 
        'year_installed': year_installed}
    if solar_production:
        params['production'] = solar_production
    else:
        params['capacity'] = capacity
        params['lat'] = lat
        params['lon'] = lng

    response = requests.get('https://ce-api-stage.herokuapp.com/solar_npv', params=params)
    if response.status_code == requests.codes.ok:
        return {'success': True, 'npv': response.json()['solar_npv'][1]}
    return {'success': False, 'code': response.status_code, 'body': response.json()['errors']}
    
def get_ceapi_solar_repl_cost(postal_code, state, capacity):
    params = {
        'ceapikey': settings.CE_API_KEY, 
        'zipcode': postal_code, 
        'state': state,
        'capacity': capacity}

    response = requests.get('https://ce-api-stage.herokuapp.com/solar_replacement_cost', params=params)
    if response.status_code == requests.codes.ok:
        return {'success': True, 'solar_cost': response.json()['solar_cost']}
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

def solar_npv(buildings, organization):
    updated = 0
    exists = 0
    errors = []
    # May fail if it doesn't get exist
    measure = Measure.objects.get(name='install_photovoltaic_system',
                                  category='renewable_energy_systems',
                                  organization_id=organization.id)

    curr_year = datetime.date.today().year
    for building in buildings:
        lat = None
        lng = None
        solar_production = None
        capacity = None
        property_measures = building.propertymeasure_set.filter(measure_id=measure.id)

        if property_measures.exists():
            for property_measure in property_measures:
                current_production = property_measure.measurements.filter(measurement_type='PROD')
                current_npv = property_measure.measurements.filter(measurement_type='NPV', year=curr_year)
                postal_code = building.postal_code
                state = building.state
                
                if not postal_code:
                    errors.append('Property at ' + building.address_line_1 + ' has no postal code')
                    continue
                
                if not state:
                    errors.append('Property at ' + building.address_line_1 + ' has no state')
                    continue

                ### ADD FILTER BY YEAR
                if current_npv.exists() and current_npv.first().quantity is not None:
                    exists += 1
                    continue

                if current_production.exists() and current_production.first().quantity is not None:
                    solar_production = current_production.first().quantity
                else: 
                    if building.latitude:
                        lat = building.latitude
                    elif 'Lat' in building.extra_data:
                        lat = building.extra_data['Lat']
                    else:
                        errors.append('Property at ' + building.address_line_1 + ' has no latitude column defined, please geocode')
                    if building.longitude:
                        lng = building.longitude
                    elif 'Long' in building.extra_data:
                        lng = building.extra_data['Long']
                    else:
                        errors.append('Property ' + building.address_line_1 + ' has no longitude column defined, please geocode')

                capacity = property_measure.measurements.get(measurement_type='CAP').quantity
                year_installed = property_measure.measurements.get(measurement_type='CAP').year
                
                if not capacity and not current_production:
                    errors.append('Property at ' + building.address_line_1 + ' has no solar capacity or production')
                    continue
                
                if not year_installed:
                    errors.append('Property at ' + building.address_line_1 + ' has installation year for the solar array')
                    continue
                    
                r = get_ceapi_solarnpv(postal_code, state, lat, lng, capacity, year_installed, solar_production)

                if r['success']:
                    updated += 1
                    npv = round(r['npv'])
                    measurement = HelixMeasurement(measure_property=property_measure,
                                                   measurement_type='NPV',
                                                   measurement_subtype='PV',
                                                   quantity=npv,
                                                   unit='DOLLR',
                                                   status='ESTIMATE',
                                                   year=datetime.date.today().year)
                    measurement.save()
                    building.extra_data['Measurement Net Present Value Quantity'] = npv
                    building.save()
        else:
            errors.append('Property ' + building.address_line_1 + ' has no solar capacity defined')

    return updated, exists, len(buildings) - updated - exists -len(errors), errors

def solar_repl_cost(buildings, organization):
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
        solar_production = None
        capacity = None
        property_measures = building.propertymeasure_set.filter(measure_id=measure.id)

        if property_measures.exists():
            for property_measure in property_measures:
                current_repl = property_measure.measurements.filter(measurement_type='REPL')
                postal_code = building.postal_code
                state = building.state
                capacity = property_measure.measurements.get(measurement_type='CAP').quantity
                
                if not postal_code:
                    errors.append('Property at ' + building.address_line_1 + ' has no postal code')
                    continue

                if not state:
                    errors.append('Property at ' + building.address_line_1 + ' has no state')
                    continue
                    
                if state not in ['MA', 'CT']:
                    errors.append('No data for this state')
                    continue

                if current_repl.exists() and current_repl.first().quantity is not None:
                    exists += 1
                    continue

                if not capacity:
                    errors.append('Property at ' + building.address_line_1 + ' has no solar capacity')
                    continue

                r = get_ceapi_solar_repl_cost(postal_code, state, capacity)

                if r['success']:
                    updated += 1
                    repl_cost = round(r['solar_cost'])
                    measurement = HelixMeasurement(measure_property=property_measure,
                                                   measurement_type='REPL',
                                                   measurement_subtype='PV',
                                                   quantity=repl_cost,
                                                   unit='DOLLR',
                                                   status='ESTIMATE',
                                                   year=datetime.date.today().year)
                    measurement.save()
                    building.extra_data['Measurement Replacement Cost Quantity'] = repl_cost
                    building.save()
        else:
            errors.append('Property ' + building.address_line_1 + ' has no solar capacity defined')

    return updated, exists, len(buildings) - updated - exists - len(errors), errors
