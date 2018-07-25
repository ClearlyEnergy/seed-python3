# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author nicholas.long@nrel.gov
"""

import copy
import json
import logging
import os
from quantityfield import ureg
from collections import OrderedDict

import xmltodict
from django.db.models import FieldDoesNotExist

from seed.models.measures import _snake_case

_log = logging.getLogger(__name__)


class BuildingSync(object):
    ADDRESS_STRUCT = {
        "root": "n1:Audits.n1:Audit.n1:Sites.n1:Site.n1:Address",
        "return": {
            "address_line_1": {
                "path": "n1:StreetAddressDetail.n1:Simplified.n1:StreetAddress",
                "required": True,
                "type": "string",
            },
            "city": {
                "path": "n1:City",
                "required": True,
                "type": "string",
            },
            "state": {
                "path": "n1:State",
                "required": True,
                "type": "string",
            }
        }
    }

    BRICR_STRUCT = {
        "root": "n1:Audits.n1:Audit",
        "return": {
            "address_line_1": {
                "path": "n1:Sites.n1:Site.n1:Address.n1:StreetAddressDetail.n1:Simplified.n1:StreetAddress",
                "required": True,
                "type": "string",
            },
            "city": {
                "path": "n1:Sites.n1:Site.n1:Address.n1:City",
                "required": True,
                "type": "string",
            },
            "state": {
                "path": "n1:Sites.n1:Site.n1:Address.n1:State",
                "required": True,
                "type": "string",
            },
            "longitude": {
                "path": "n1:Sites.n1:Site.n1:Longitude",
                "required": True,
                "type": "double"
            },
            "latitude": {
                "path": "n1:Sites.n1:Site.n1:Latitude",
                "required": True,
                "type": "double",
            },
            "property_name": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.@ID",
                "required": True,
                "type": "string",
            },
            "year_built": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:YearOfConstruction",
                "required": True,
                "type": "integer",
            },
            "floors_above_grade": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:FloorsAboveGrade",
                "required": True,
                "type": "integer",
            },
            "floors_below_grade": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:FloorsBelowGrade",
                "required": True,
                "type": "integer",
            },
            "premise_identifier": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:PremisesIdentifiers.n1:PremisesIdentifier",
                "key_path_name": "n1:IdentifierLabel",
                "key_path_value": "Assessor parcel number",
                "value_path_name": "n1:IdentifierValue",
                "required": True,
                "type": "string",
            },
            "custom_id_1": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:PremisesIdentifiers.n1:PremisesIdentifier",
                "key_path_name": "n1:IdentifierCustomName",
                "key_path_value": "BRICR Custom ID 1",
                "value_path_name": "n1:IdentifierValue",
                "required": True,
                "type": "string",
            },
            "gross_floor_area": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:FloorAreas.n1:FloorArea",
                "key_path_name": "n1:FloorAreaType",
                "key_path_value": "Gross",
                "value_path_name": "n1:FloorAreaValue",
                "required": True,
                "type": "double",
            },
            "net_floor_area": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:FloorAreas.n1:FloorArea",
                "key_path_name": "n1:FloorAreaType",
                "key_path_value": "Net",
                "value_path_name": "n1:FloorAreaValue",
                "required": False,
                "type": "double",
            },
            "footprint_floor_area": {
                "path": "n1:Sites.n1:Site.n1:Facilities.n1:Facility.n1:FloorAreas.n1:FloorArea",
                "key_path_name": "n1:FloorAreaType",
                "key_path_value": "Footprint",
                "value_path_name": "n1:FloorAreaValue",
                "required": False,
                "type": "double",
            },
        }
    }

    def __init__(self):
        self.filename = None
        self.data = None
        self.raw_data = {}

    @property
    def pretty_print(self):
        """
        Print the JSON to the screen
        :return: None
        """
        print(json.dumps(self.raw_data, indent=2))

    def import_file(self, filename):
        self.filename = filename

        if os.path.isfile(filename):
            with open(filename, 'rU') as xmlfile:
                self.raw_data = xmltodict.parse(
                    xmlfile.read(),
                    process_namespaces=True,
                    namespaces={
                        'http://nrel.gov/schemas/bedes-auc/2014': 'n1',
                        'http://www.w3.org/2001/XMLSchema-instance': 'xsi',
                    }
                )
        else:
            raise Exception("File not found: {}".format(filename))

        return True

    def export(self, property_state, process_struct=ADDRESS_STRUCT):
        """Export BuildingSync file from an existing BuildingSync file (from import), property_state and
        a process struct.

        :param property_state: object, PropertyState to merge into BuildingSync
        :param process_struct: dict, mapping from PropertyState to BuildingSync
        :return: string, as XML
        """

        # if property state is not defined, then just return the BuildingSync unparsed
        if not property_state:
            return xmltodict.unparse(self.raw_data, pretty=True).replace('\t', '  ')

        # parse the property_state and merge it with the raw data
        new_dict = copy.deepcopy(self.raw_data)
        if new_dict == {}:
            _log.debug("BuildingSync raw data is empty, adding in header information")
            # new_dict[]
            new_dict = OrderedDict(
                [
                    (
                        u'n1:Audits', OrderedDict(
                            [
                                (u'@xsi:schemaLocation',
                                 u'http://nrel.gov/schemas/bedes-auc/2014 https://github.com/BuildingSync/schema/releases/download/v0.3/BuildingSync.xsd'),
                                ('@xmlns', OrderedDict(
                                    [
                                        (u'n1', u'http://nrel.gov/schemas/bedes-auc/2014'),
                                        (u'xsi', u'http://www.w3.org/2001/XMLSchema-instance')
                                    ]
                                ))
                            ]
                        )
                    )
                ]
            )

        for field, v in process_struct['return'].items():
            value = None
            try:
                property_state._meta.get_field(field)
                value = getattr(property_state, field)
            except FieldDoesNotExist:
                _log.debug("Field {} is not a db field, trying read from extra data".format(field))
                value = property_state.extra_data.get(field, None)

            # set the value in the new_dict (if none, then remove the field)
            # TODO: remove the field if the value is None
            # TODO: handle the setting of the complex fields (with key_path_names, identifiers)
            if value:
                full_path = "{}.{}".format(process_struct['root'], v['path'])

                if v.get('key_path_name', None) and v.get('value_path_name', None) and v.get('key_path_value', None):
                    # iterate over the paths and find the correct node to set
                    self._set_compound_node(
                        full_path,
                        new_dict,
                        v['key_path_name'],
                        v['key_path_value'],
                        v['value_path_name'],
                        value
                    )
                else:
                    if not self._set_node(full_path, new_dict, value):
                        _log.debug("Unable to set path")

        return xmltodict.unparse(new_dict, pretty=True).replace('\t', '  ')

    def _set_node(self, path, data, value):
        """
        Set the value in the dictionary based on the path. If there are more than one paths, then
        it will only set the first path for now. The future could allow a variable to pass in the
        index (or other constraint) before setting the value.

        :param path: string, path which to navigate to set the value
        :param data: dict, dictionary to process
        :param value: value to set, could be any type at the moment.
        :return: boolean, true if successful
        """

        path = path.split(".")
        for idx, p in enumerate(path):
            if p == '':
                return False
            elif idx == len(path) - 1:
                if value is None:
                    del data[p]
                else:
                    data[p] = value
                return True
            else:
                prev_node = path.pop(0)
                new_node = data.get(prev_node)
                new_path = '.'.join(path)
                if new_node is None:
                    # create the new node because it doesn't exist
                    data[prev_node] = {}
                    new_node = data[prev_node]

                if isinstance(new_node, list):
                    _log.debug("Unable to iterate over lists at the moment")
                    return False
                elif isinstance(new_node, dict):
                    return self._set_node(new_path, new_node, value)
                else:
                    # can't recurse futher into new_node because it is not a dict
                    break

    def _set_compound_node(self, list_path, data, key_path_name, key_path_value, value_path_name,
                           value):
        """
        If the XML is a list of options with a key field at the same level as the value, then use
        this method. The example belows show how the XML will be structured. To set the
        Gross floor area, then pass in the following

            _set_compound_node("...FloorAreas", "FloorAreaType", "Gross", "FloorAreaValue", 1000)

        .. code:

            <n1:FloorAreas>
                <n1:FloorArea>
                    <n1:FloorAreaType>Gross</n1:FloorAreaType>
                    <n1:FloorAreaValue>25000</n1:FloorAreaValue>
                </n1:FloorArea>
                <n1:FloorArea>
                    <n1:FloorAreaType>Net</n1:FloorAreaType>
                    <n1:FloorAreaValue>22500</n1:FloorAreaValue>
                </n1:FloorArea>
            </n1:FloorAreas>

        :param list_path: String, path to where the list of items start in the dictionary
        :param data: Dict, data to act on
        :param key_path_name: String, name of the element to contrain check on
        :param key_path_value: String, name of the value of the element to check on
        :param value_path_name: String, name of the element that will be set
        :param value: undefined, Value to set
        :return: Boolean
        """

        path = list_path.split(".")
        for idx, p in enumerate(path):
            if p == '':
                return False
            elif idx == len(path) - 1:
                # We have arrived at the location where the compound data needs to be set
                # Make sure that the key_path_name and key_path_value are not already there
                if data.get(p):
                    if isinstance(data[p], dict):
                        if data[p].get(key_path_name) == key_path_value:
                            data[p][value_path_name] = value
                        else:
                            # need to convert the dict to a list and then add the new one.
                            data[p] = [data[p]]
                            new_sub_item = {key_path_name: key_path_value, value_path_name: value}
                            data[p].append(new_sub_item)
                    elif isinstance(data[p], list):
                        for sub in data[p]:
                            if sub.get(key_path_name, None) == key_path_value:
                                sub[value_path_name] = value
                                break
                        else:
                            # Not found, create a new one
                            new_sub_item = {key_path_name: key_path_value, value_path_name: value}
                            data[p].append(new_sub_item)
                else:
                    if isinstance(value, ureg.Quantity):
                        data[p] = {key_path_name: key_path_value, value_path_name: value.magnitude}
                    else:
                        data[p] = {key_path_name: key_path_value, value_path_name: value}

                return True
            else:
                prev_node = path.pop(0)
                new_node = data.get(prev_node)
                new_path = '.'.join(path)
                if new_node is None:
                    # create the new node because it doesn't exist
                    data[prev_node] = {}
                    new_node = data[prev_node]

                if isinstance(new_node, list):
                    _log.debug("Unable to iterate over lists at the moment")
                    return False
                elif isinstance(new_node, dict):
                    return self._set_compound_node(new_path, new_node, key_path_name,
                                                   key_path_value, value_path_name, value)
                else:
                    # can't recurse futher into new_node because it is not a dict
                    break

    def _get_node(self, path, node, results=[], kwargs={}):
        """
        Return the values from a dictionary based on a path delimited by periods. If there
        are more than one results, then it will return all the results in a list.

        The method handles nodes that are either lists or either dictionaries. This method is
        recursive as it nagivates the tree.

        :param path: string, path which to navigate to in the dictionary
        :param node: dict, dictionary to process
        :param results: list or value, results
        :return: list, results
        """
        path = path.split(".")

        for idx, p in enumerate(path):
            if p == '':
                if node:
                    results.append(node)
                break
            elif idx == len(path) - 1:
                value = node.get(p)
                if value:
                    results.append(node.get(p))
                break
            else:
                new_node = node.get(path.pop(0))
                new_path = '.'.join(path)
                if isinstance(new_node, list):
                    # grab the values from each item in the list or iterate
                    for nn in new_node:
                        self._get_node(new_path, nn, results)
                    break
                elif isinstance(new_node, dict):
                    self._get_node(new_path, new_node, results)
                    break
                else:
                    # can't recurse futher into new_node because it is not a dict
                    break

        if len(results) == 0:
            return []
        elif len(results) == 1:
            return results[0]
        else:
            return results

    def _process_struct(self, struct, data):
        """
        Take a dictionary and return the `return` object with values filled in.

        :param struct: dict, object to parse and fill from BuildingSync file
        :param data: dict, data to parse and fill
        :return: list, the `return` value, if all paths were found, and list of messages
        """

        def _lookup_sub(node, key_path_name, key_path_value, value_path_name):
            items = [node] if isinstance(node, dict) else node
            for item in items:
                found = False
                for k, v in item.items():
                    if k == key_path_name and v == key_path_value:
                        found = True

                    if found and k == value_path_name:
                        return v

        res = {'measures': [], 'scenarios': []}
        messages = []
        errors = False
        for k, v in struct['return'].items():
            path = ".".join([struct['root'], v['path']])
            value = self._get_node(path, data, [])

            try:
                if v.get('key_path_name', None) and v.get('value_path_name', None) and v.get(
                        'key_path_value', None):
                    value = _lookup_sub(
                        value,
                        v.get('key_path_name'),
                        v.get('key_path_value'),
                        v.get('value_path_name'),
                    )

                    # check if the value is not defined and if it is required
                    if not value:
                        if v.get('required'):
                            messages.append(
                                "Could not find required value for sub-lookup of {}:{}".format(
                                    v.get('key_path_name'), v.get('key_path_value')))
                            errors = True
                            continue
                        else:
                            continue

                if value:
                    # catch some errors
                    if isinstance(value, list):
                        messages.append("Could not find single entry for '{}'".format(path))
                        errors = True
                        continue

                    # type cast the value
                    if v['type'] == 'double':
                        value = float(value)
                    elif v['type'] == 'integer':
                        value = int(value)
                    elif v['type'] == 'dict':
                        value = dict(value)
                    elif v['type'] == 'string':
                        value = str(value)
                    else:
                        messages.append("Unknown cast type of {} for '{}'".format(v['type'], path))

                    res[k] = value
                else:
                    if v['required']:
                        messages.append("Could not find required value for '{}'".format(path))
                        errors = True
            except Exception as err:
                message = "Error processing {}:{} with error: {}".format(k, v, err)
                messages.append(message)
                errors = True

        # manually add in parsing of measures and reports because they are a bit different than
        # a straight mapping
        measures = self._get_node('n1:Audits.n1:Audit.n1:Measures.n1:Measure', data, [])
        for m in measures:
            cat_w_namespace = m['n1:TechnologyCategories']['n1:TechnologyCategory'].keys()[0]
            category = cat_w_namespace.replace('n1:', '')
            new_data = {
                'property_measure_name': m.get('@ID'),  # This will be the IDref from the scenarios
                'category': _snake_case(category),
                'name': m['n1:TechnologyCategories']['n1:TechnologyCategory'][cat_w_namespace][
                    'n1:MeasureName']
            }
            for k, v in m.items():
                if k in ['@ID', 'n1:PremisesAffected', 'n1:TechnologyCategories']:
                    continue
                new_data[_snake_case(k.replace('n1:', ''))] = v

            # fix the names of the measures for "easier" look up... doing in separate step to
            # fit in single line. Cleanup -- when?
            new_data['name'] = _snake_case(new_data['name'])
            res['measures'].append(new_data)

        # <n1:Scenario>
        #   <n1:ScenarioName>Lighting Only</n1:ScenarioName>
        #   <n1:ScenarioType>
        #     <n1:PackageOfMeasures>
        #       <n1:ReferenceCase IDref="Baseline"/>
        #       <n1:MeasureIDs>
        #         <n1:MeasureID IDref="Measure1"/>
        #       </n1:MeasureIDs>
        #       <n1:AnnualSavingsSiteEnergy>162654.89601696888</n1:AnnualSavingsSiteEnergy>
        #     </n1:PackageOfMeasures>
        #   </n1:ScenarioType>
        # </n1:Scenario>
        scenarios = self._get_node('n1:Audits.n1:Audit.n1:Report.n1:Scenarios.n1:Scenario',
                                   data, [])
        for s in scenarios:
            new_data = {
                'id': s.get('@ID'),
                'name': s.get('n1:ScenarioName'),
            }

            if s.get('n1:ScenarioType'):
                node = s['n1:ScenarioType'].get('n1:PackageOfMeasures')
                if node:
                    ref_case = self._get_node('n1:ReferenceCase', node, [])
                    if ref_case and ref_case.get('@IDref'):
                        new_data['reference_case'] = ref_case.get('@IDref')
                    new_data['annual_savings_site_energy'] = node.get('n1:AnnualSavingsSiteEnergy')

                    new_data['measures'] = []
                    measures = self._get_node('n1:MeasureIDs.n1:MeasureID', node, [])
                    if isinstance(measures, list):
                        for measure in measures:
                            if measure.get('@IDref', None):
                                new_data['measures'].append(measure.get('@IDref'))
                    else:
                        if isinstance(measures, (str, unicode)):
                            # the measure is there, but it does not have an idref
                            continue
                        else:
                            if measures.get('@IDref', None):
                                new_data['measures'].append(measures.get('@IDref'))

            res['scenarios'].append(new_data)

        return res, errors, messages

    def process(self, process_struct=ADDRESS_STRUCT):
        """Process the BuildingSync file based ont he process structure.

        :param process_struct: dict, structure on how to extract data from file and save into dict
        :return: list, [dict, list, list], [results, list of errors, list of messages]
        """
        # API call to BuildingSync Selection Tool on other server for appropriate use case
        # prcess_struct = new_use_case (from Building Selection Tool)
        return self._process_struct(process_struct, self.raw_data)
