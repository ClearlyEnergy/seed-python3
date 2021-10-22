# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2021, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author nicholas.long@nrel.gov
"""
from collections import OrderedDict
from rest_framework import serializers

from seed.models import (
    Measure,
    PropertyState,
    #    PropertyMeasure,
)
from helix.models import HELIXPropertyMeasure as PropertyMeasure
from seed.serializers.base import ChoiceField


class MeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measure
        fields = '__all__'


class PropertyMeasureSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='measure.id')
    measure = serializers.PrimaryKeyRelatedField(queryset=Measure.objects.all())
    property_state = serializers.PrimaryKeyRelatedField(queryset=PropertyState.objects.all())
    measure_id = serializers.SerializerMethodField('measure_id_name')
    name = serializers.ReadOnlyField(source='measure.name')
    display_name = serializers.ReadOnlyField(source='measure.display_name')
    category = serializers.ReadOnlyField(source='measure.category')
    category_display_name = serializers.ReadOnlyField(source='measure.category_display_name')
    implementation_status = ChoiceField(choices=PropertyMeasure.IMPLEMENTATION_TYPES)
    application_scale = ChoiceField(choices=PropertyMeasure.APPLICATION_SCALE_TYPES)
    category_affected = ChoiceField(choices=PropertyMeasure.CATEGORY_AFFECTED_TYPE)

    class Meta:
        model = PropertyMeasure

        fields = (
            'id',
            'measure',
            'property_state',
            'property_measure_name',
            'measure_id',
            'category',
            'name',
            'category_display_name',
            'display_name',
            'category_affected',
            'application_scale',
            'recommended',
            'implementation_status',
            'cost_mv',
            'description',
            'cost_total_first',
            'cost_installation',
            'cost_material',
            'cost_capital_replacement',
            'cost_residual_value',
            'useful_life',
            'current_financing',
            'ownership',
            'electric',
            'installer',
            'reference_id',
            'source',
        )

    def measure_id_name(self, obj):
        return "{}.{}".format(obj.measure.category, obj.measure.name)

    def create(self, validated_data):
        validated_data.pop('organization_id', None)
        property_measure = PropertyMeasure.objects.create(**validated_data)
        return property_measure


class PropertyMeasureReadOnlySerializer(serializers.BaseSerializer):
    """Simple read only Serializer describing Measures attached to
    property. Use with prefetch_related to avoid extra database calls.
    """
    implementation_status = ChoiceField(choices=PropertyMeasure.IMPLEMENTATION_TYPES)

    def to_representation(self, obj):
        """Serialize measures property"""
        measurements = [(
            measure.get_measurement_type_display(),
            measure.get_measurement_subtype_display(),
            measure.get_fuel_display(),
            measure.quantity,
            measure.get_unit_display(),
            measure.get_status_display(),
            measure.year) for measure in obj.measurements.all()]
        measure = OrderedDict((
            ('id', obj.measure.id),
            ('name', obj.measure.name)
        ))
        return OrderedDict((
            ('id', obj.id),
            ('name', obj.measure.name),
            ('display_name', obj.measure.display_name),
            ('category', obj.measure.category),
            ('category_display_name', obj.measure.category_display_name),
            ('description', obj.description),
            ('property_measure_name', obj.property_measure_name),
            ('implementation_status', obj.get_implementation_status_display()),
            ('recommended', obj.recommended),
            ('cost_mv', obj.cost_mv),
            ('cost_total_first', obj.cost_total_first),
            ('cost_installation', obj.cost_installation),
            ('cost_material', obj.cost_material),
            ('cost_capital_replacement', obj.cost_capital_replacement),
            ('cost_residual_value', obj.cost_residual_value),
            ('category_affected', obj.get_category_affected_display()),
            ('application_scale', obj.get_application_scale_display()),
            ('current_financing', obj.get_current_financing_display()),
            ('ownership', obj.get_ownership_display()),
            ('electric', obj.get_electric_display()),
            ('installer', obj.installer),
            ('reference_id', obj.reference_id),
            ('source', obj.get_source_display()),
            ('measure', measure),
            ('measurements', measurements)
        ))
