# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of any
required approvals from the U.S. Department of Energy) and contributors.
All rights reserved.  # NOQA
"""

from rest_framework import serializers

from seed.models.data_quality import (
    DataQualityCheck,
)


class RulesSubSerializer(serializers.Serializer):
    field = serializers.CharField(max_length=100)
    severity = serializers.CharField(max_length=100)


class RulesSubSerializerB(serializers.Serializer):
    field = serializers.CharField(max_length=100)
    enabled = serializers.BooleanField()
    data_type = serializers.CharField(max_length=100)
    min = serializers.FloatField()
    max = serializers.FloatField()
    severity = serializers.CharField(max_length=100)
    units = serializers.CharField(max_length=100)


class RulesIntermediateSerializer(serializers.Serializer):
    missing_matching_field = RulesSubSerializer(many=True)
    missing_values = RulesSubSerializer(many=True)
    in_range_checking = RulesSubSerializerB(many=True)


class RulesSerializer(serializers.Serializer):
    data_quality_rules = RulesIntermediateSerializer()


class DataQualityCheckSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'organization_id')
        model = DataQualityCheck

    def create(self, validated_data):
        obj = DataQualityCheck.objects.create(**validated_data)
        obj.initialize_rules()
        obj.save()
        return obj
