/**
 * :copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.delete_certification_modal', [])
  .controller('delete_certification_modal_controller', [
    '$scope',
    '$uibModalInstance',
    'certification_service',
    'certification',
    function ($scope, $uibModalInstance, certification_service, certification) {
      $scope.certification = certification;
      $scope.delete_certification = function () {
        certification_service.delete_certification($scope.certification.id).then(function () {
          $uibModalInstance.close();
        });
      };

      $scope.cancel = function () {
        $uibModalInstance.dismiss();
      };
    }]);
