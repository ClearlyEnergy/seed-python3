angular.module('BE.seed.service.meter', [])
  .factory('meter_service', [
    '$http',
    function ($http) {
      var meter_factory = {};

      meter_factory.get_meters = function (property_view_id) {
        return $http.post('/api/v2/meters/property_meters/', {
          property_view_id: property_view_id
        }).then(function (response) {
          return response.data;
        });
      };

      meter_factory.property_meter_usage = function (property_view_id, organization_id, interval, excluded_meter_ids) {
        if (_.isUndefined(excluded_meter_ids)) excluded_meter_ids = [];
        return $http.post('/api/v2/meters/property_meter_usage/', {
          property_view_id: property_view_id,
          interval: interval,
          excluded_meter_ids: excluded_meter_ids
        }).then(function (response) {
          return response.data;
        });
      };

      return meter_factory;
    }
  ]);
