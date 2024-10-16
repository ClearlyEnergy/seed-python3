angular.module('BE.seed.controller.pvwatts_modal', [])
  .controller('pvwatts_modal_controller', [
    '$scope',
    '$uibModalInstance',
    'pvwatts_service',
    'columns_service',
    'inventory_type',
    'org_id',
    'organization_service',
    'property_state_ids',
    'taxlot_state_ids',
    function ($scope, $uibModalInstance, pvwatts_service, columns_service, inventory_type, org_id, organization_service, property_state_ids, taxlot_state_ids) {
      $scope.inventory_type = inventory_type;
      $scope.property_state_ids = _.uniq(property_state_ids);
      $scope.taxlot_state_ids = _.uniq(taxlot_state_ids);
      $scope.pvwatts_state = 'verify';
      $scope.total_selected_count = $scope.property_state_ids.length + $scope.taxlot_state_ids.length;
      $scope.org_id = org_id;
      $scope.new_factor = {};

      $scope.available_calculations = [
         {label: 'Calculate Solar Production', color: 'gray', type: 'production'},
         {label: 'Calculate Solar Present Value', color: 'gray', type: 'npv'}, 
         {label: 'Calculate Solar Replacement Cost', color: 'gray', type: 'repl_cost'},
      ]

      $scope.calculate_production = function () {
		  if ($scope.new_factor.type == 'production') {
            mappings = [{
               'from_field': 'Measurement Production Quantity',
               'from_units': 'kWh',
               'to_field': 'Measurement Production Quantity',
               'to_field_display_name': 'Measurement Production Quantity',
               'to_table_name': 'PropertyState',
            }]
            if ($scope.property_state_ids) {
               $scope.pvwatts_state = 'calculate';
               columns_service.create_columns(mappings).then(
                  function (data) {
                     pvwatts_service.calculate_production($scope.property_state_ids, $scope.taxlot_state_ids, $scope.org_id).then(function (result) {
                     $scope.properties_calculated = result.calculated;
                     $scope.properties_exists = result.exists;
                     $scope.properties_not_calculated = result.not_calculated;
                     $scope.properties_errors = result.errors;
                     $scope.pvwatts_state = 'result';
                  });
               });
            };
         };
         if ($scope.new_factor.type == 'npv') {
             mappings = [{
                'from_field': 'Measurement Net Present Value Quantity',
                'from_units': 'kWh',
                'to_field': 'Measurement Net Present Value Quantity',
                'to_field_display_name': 'Measurement NPV Quantity',
                'to_table_name': 'PropertyState',
             }]
            if ($scope.property_state_ids) {
               $scope.pvwatts_state = 'calculate';
               columns_service.create_columns(mappings).then(
                  function (data) {
                     pvwatts_service.calculate_solar_npv($scope.property_state_ids, $scope.taxlot_state_ids, $scope.org_id).then(function (result) {
                     $scope.properties_calculated = result.calculated;
                     $scope.properties_exists = result.exists;
                     $scope.properties_not_calculated = result.not_calculated;
                     $scope.properties_errors = result.errors;
                     $scope.pvwatts_state = 'result';
                  });
               });
            };
         };
         if ($scope.new_factor.type == 'repl_cost') {
             mappings = [{
                'from_field': 'Measurement Replacement Cost Quantity',
                'from_units': 'kWh',
                'to_field': 'Measurement Replacement Cost Quantity',
                'to_field_display_name': 'Measurement Replacement Cost Quantity',
                'to_table_name': 'PropertyState',
             }]
            if ($scope.property_state_ids) {
               $scope.pvwatts_state = 'calculate';
               columns_service.create_columns(mappings).then(
                  function (data) {
                     pvwatts_service.calculate_solar_repl_cost($scope.property_state_ids, $scope.taxlot_state_ids, $scope.org_id).then(function (result) {
                     $scope.properties_calculated = result.calculated;
                     $scope.properties_exists = result.exists;
                     $scope.properties_not_calculated = result.not_calculated;
                     $scope.properties_errors = result.errors;
                     $scope.pvwatts_state = 'result';
                  });
               });
            };
         };
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
