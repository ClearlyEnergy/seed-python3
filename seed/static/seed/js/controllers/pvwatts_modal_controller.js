angular.module('BE.seed.controller.pvwatts_modal', [])
  .controller('pvwatts_modal_controller', [
    '$scope',
    '$uibModalInstance',
    'pvwatts_service',
    'inventory_type',
    'org_id',
    'organization_service',
    'property_state_ids',
    'taxlot_state_ids',
    function ($scope, $uibModalInstance, pvwatts_service, inventory_type, org_id, organization_service, property_state_ids, taxlot_state_ids) {
      $scope.inventory_type = inventory_type;
      $scope.property_state_ids = _.uniq(property_state_ids);
      $scope.taxlot_state_ids = _.uniq(taxlot_state_ids);
      $scope.pvwatts_state = 'verify';
      $scope.total_selected_count = $scope.property_state_ids.length + $scope.taxlot_state_ids.length;

      pvwatts_service.calculation_results($scope.property_state_ids, $scope.taxlot_state_ids).then(function (result) {
          if (result.properties) {
            $scope.pre_properties_not_calculated = result.properties.not_calculated;

            $scope.pre_properties_calculated = result.properties.calculated;
          }

          if (result.tax_lots) {
            $scope.pre_tax_lots_not_calculated = result.tax_lots.not_calculated;

            $scope.pre_tax_lots_calculated = result.tax_lots.calculated;
          }
      });

      $scope.calculate_production = function () {
        if ($scope.property_state_ids) {
          pvwatts_service.calculate_production($scope.property_state_ids, $scope.taxlot_state_ids).then(function () {
            $scope.pvwatts_state = 'calculate';

            pvwatts_service.calculation_results($scope.property_state_ids, $scope.taxlot_state_ids).then(function (result) {
	            if (result.properties) {
	              $scope.properties_calculated = result.properties.calculated;
	              $scope.properties_not_calculated = result.properties.not_calculated;
	            }

	            if (result.tax_lots) {
	              $scope.tax_lots_calculated = result.tax_lots.calculated;
	              $scope.tax_lots_not_calculated = result.tax_lots.not_calculated;
	            }

	            $scope.pvwatts_state = 'result';
            });
          });
        }
      };

      /**
       * cancel: dismisses the modal
       */
      $scope.cancel = function () {
        $uibModalInstance.dismiss({
          pvwatts_state: $scope.pvwatts_state,
          property_state_ids: $scope.property_state_ids,
          taxlot_state_ids: $scope.taxlot_state_ids
        });
      };

      /**
       * close: closes the modal
       */
      $scope.close = function () {
        $uibModalInstance.close({
          pvwatts_state: $scope.pvwatts_state,
          property_state_ids: $scope.property_state_ids,
          taxlot_state_ids: $scope.taxlot_state_ids
        });
      };
    }
  ]);
