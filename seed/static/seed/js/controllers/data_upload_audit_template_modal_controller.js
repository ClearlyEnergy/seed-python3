/**
 * :copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.data_upload_audit_template_modal', [])
  .controller('data_upload_audit_template_modal_controller', [
    '$scope',
    '$state',
    '$uibModal',
    '$uibModalInstance',
    'urls',
    'uiGridConstants',
    'spinner_utility',
    'organization',
    'cycle_id',
    'upload_from_file',
    'audit_template_service',
    'organization_service',
    'audit_template_building_id',
    'view_id',
    function (
      $scope,
      $state,
      $uibModal,
      $uibModalInstance,
      urls,
      uiGridConstants,
      spinner_utility,
      organization,
      cycle_id,
      upload_from_file,
      audit_template_service,
      organization_service,
      audit_template_building_id,
      view_id
    ) {
      $scope.stage = "UPLOAD_OPTIONS";
      $scope.organization = organization;
      $scope.view_id = view_id;
      $scope.cycle_id = cycle_id;
      $scope.upload_from_file = upload_from_file;
      $scope.error = '';
      $scope.fields = {
        'audit_template_building_id': audit_template_building_id,
        'at_api_token': organization.at_api_token
      };

      $scope.upload_from_file_and_close = function (event_message, file, progress) {
        $scope.close();
        console.log(event_message, file, progress);
        $scope.upload_from_file(event_message, file, progress);
      };

      $scope.display_import_form = function () {
        $scope.stage = "IMPORT_FORM";
      };

      $scope.cancel_import_form = function () {
        $scope.stage = "UPLOAD_OPTIONS";
        $scope.error = '';
      };

      $scope.confirm_import = function () {
        if (!$scope.fields.at_api_token || !$scope.fields.audit_template_building_id) {
          $scope.error = "An Audit Template building ID and API token is required.";
        } else {
          $scope.submit_request();
        }
      };

      $scope.submit_request = function () {
        $scope.stage = "AWAITING_REPONSE";
        $scope.error = '';
        spinner_utility.show();
        if ($scope.fields.at_api_token != $scope.organization.at_api_token) {
          $scope.organization.at_api_token = $scope.fields.at_api_token
        }
        return organization_service.save_org_settings($scope.organization).then(result => {
          audit_template_service.get_building_xml($scope.organization.id, $scope.fields.audit_template_building_id).then(result => {
            spinner_utility.hide();
            if (typeof(result) == 'object' && !result.success) {
              $scope.error = 'Error: ' + result.message
              $scope.stage = "IMPORT_FORM";
            } else {
              console.log(result)
              return audit_template_service.update_building_with_xml($scope.organization.id, $scope.cycle_id, $scope.view_id, result).then(result => {
                console.log(result)
                $scope.close();
              });
            }   
          });
        });
      };

      $scope.close = function () {
        $uibModalInstance.dismiss();
      };

      $scope.open_at_token_modal = function () {
        var modal = $uibModal.open({
          templateUrl: urls.static_url + 'seed/partials/at_token_modal.html',
          controller: 'at_token_modal_controller',
          resolve: {
            'organization': $scope.organization,
            'audit_template_service': audit_template_service
          }
        });
        modal.result.then(function (token) {
          $scope.fields.at_api_token = token;
          $scope.organization.at_api_token = token;
        });
      };

    }]);
