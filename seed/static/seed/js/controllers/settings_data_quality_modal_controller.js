/**
 * :copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.settings_data_quality_modal', [])
  .controller('settings_data_quality_modal_controller', [
    '$scope',
    '$uibModalInstance',
    'data_quality_service',
    'action',
    'data',
	  function ($scope, $uibModalInstance, data_quality_service, action, data) {
      $scope.action = action;
      $scope.data = data;

      $scope.rename_data_quality = function () {
        if (!$scope.disabled()) {
          var id = $scope.data.id;
          var data_quality = _.omit($scope.data, 'id');
          data_quality.name = $scope.newName;
          data_quality_service.update_data_quality(id, data_quality).then(function (result) {
            $uibModalInstance.close(result.name);
          });
        }
      };

      $scope.remove_data_quality = function () {
        data_quality_service.remove_data_quality($scope.data.id, $scope.data.organization).then(function () {
          $uibModalInstance.close();
        });
      };

      $scope.new_data_quality = function () {
        if (!$scope.disabled()) {
          data_quality_service.new_data_quality({
            name: $scope.newName,
			organization: $scope.data.org_id
          }).then(function (result) {
            $uibModalInstance.close(result);
          });
        }
      };

      $scope.disabled = function () {
        if ($scope.action === 'rename') {
          return _.isEmpty($scope.newName) || $scope.newName === $scope.data.name;
        } else if ($scope.action === 'new') {
          return _.isEmpty($scope.newName);
        }
      };

      $scope.cancel = function () {
        $uibModalInstance.dismiss();
      };
    }]);
