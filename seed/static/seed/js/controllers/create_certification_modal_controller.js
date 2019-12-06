/**
 * :copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.create_certification_modal', [])
  .controller('create_certification_modal_controller', [
    '$scope',
    '$uibModalInstance',
	'Notification',
    'certification_service',
    'certification',
	'certifications',
	  function ($scope, $uibModalInstance, Notification, certification_service, certification, certifications) {
      $scope.certification = certification;
	  $scope.certifications = certifications;
	  
      $scope.create_certification = function () {
		if (isCertificationNameUsed(certification.name)) {
		  alert('Certification name already exists');
		} else {
  		  delete certification.disabled;
          certification_service.create_certification(certification).then(function () {
            $uibModalInstance.close();
	        var msg = 'Created new Certification ' + certification.name;
	        Notification.primary(msg);
          });
	    }
      };

      $scope.cancel = function () {
        $uibModalInstance.dismiss();
      };
	  
      function isCertificationNameUsed (newCertificationName) {
        return _.some($scope.certifications, function (obj) {
          return obj.name === newCertificationName;
        });
      }
	  
    }]);
