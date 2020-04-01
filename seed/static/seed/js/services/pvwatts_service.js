angular.module('BE.seed.service.pvwatts', [])
  .factory('pvwatts_service', [
    '$http',
    function ($http) {
      var pvwatts_factory = {};

      pvwatts_factory.calculate_production = function (property_state_ids, taxlot_state_ids, org_id) {
        return $http.post('/api/v2/pvwatts/pvwatts_by_ids/', {
          property_ids: property_state_ids,
          taxlot_ids: taxlot_state_ids,
          org_id: org_id
        }).then(function (response) {
			return response.data;
        });
      };

      return pvwatts_factory;
    }
  ]);
