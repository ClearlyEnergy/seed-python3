/**
 * :copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.delete_measure_modal', [])
  .controller('delete_measure_modal_controller', [
    '$scope',
    '$uibModalInstance',
    'measure_service',
    'measure',
    function ($scope, $uibModalInstance, measure_service, measure) {
      $scope.measure = measure;
      $scope.delete_property_measure = function () {
        measure_service.delete_property_measure($scope.measure.id).then(function () {
          $uibModalInstance.close();
        });
      };

      $scope.cancel = function () {
        $uibModalInstance.dismiss();
      };
    }]);
