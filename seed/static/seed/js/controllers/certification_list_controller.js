/*
 * :copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */

angular.module('BE.seed.controller.certification', [])
  .controller('certification_list_controller', [
    '$scope',
    'urls',
    '$uibModal',
    'Notification',
    'certification_service',
    'certifications_payload',
	  function ($scope, urls, $uibModal, Notification, certification_service, certifications_payload) {
		$scope.certifications = certifications_payload.data;
        initialize_new_certification();
        $scope.columns = [{
          title: 'Certification Name'
        }, {
          title: 'Award Body'
        }, {
          title: 'Recognition Type'
        }, {
          title: 'Is Numeric?'
        }, {
          title: 'Valid For'
        }, {
          title: 'RESO Certification?'
        }, {
          title: 'Description'
        }];
		
        /**
         * Functions for dealing with editing a certifications' name
         */
		
        $scope.edit_certification_name = function (certification) {
          certification.edit_form_showing = true;
        };
        $scope.cancel_edit_name = function (certification) {
          certification.edit_form_showing = false;
        };
        $scope.save_certification_name = function (certification) {
		  var duration = (certification.validity_duration == null ? "" : certification.validity_duration);
  	      var cert = {
			  "name": certification.name, 
			  "award_body": certification.award_body,
			  "recognition_type": certification.recognition_type, 
			  "validity_duration": duration, 
			  "description": certification.description,
			  "id": certification.id
		  }

          certification_service.update_certification(cert).then(function () {
            refresh_certifications();
          });
          certification.edit_form_showing = false;
        };

        /**
         * open up modal to confirm create of certification, refresh list
         */

        $scope.confirm_create_certification = function (certification) {
          var modalInstance = $uibModal.open({
            templateUrl: urls.static_url + 'seed/partials/create_certification_modal.html',
            controller: 'create_certification_modal_controller',
            resolve: {
		      certification: certification,
			  certifications: function () {
                return $scope.certifications;
			  }
            }
          });

          modalInstance.result.finally(function () {
            initialize_new_certification();
            refresh_certifications();
          });
        };
		
        /**
         * open up modal to confirm delete of certification, refresh list
         */

        $scope.confirm_delete_certification = function (certification) {
          var modalInstance = $uibModal.open({
            templateUrl: urls.static_url + 'seed/partials/delete_certification_modal.html',
            controller: 'delete_certification_modal_controller',
            resolve: {
		      certification: certification
            }
          });

          modalInstance.result.finally(function () {
            refresh_certifications();
          });
        };
		
        /**
         * refresh_certifications: refreshes certification list
         */
        var refresh_certifications = function () {
          certification_service.get_certifications().then(function (certifications) {
	  		$scope.certifications = certifications.data;
          });
        };
		

        function initialize_new_certification () {
          $scope.certification = {
			  name: "", 
			  award_body: "",
			  recognition_type: "",
			  validity_duration: "",
			  description: "",
			  is_numeric_score: false,
			  is_reso_certification: true,
              disabled: function () {
              var name = $scope.certification.name || '';
              return name.length === 0;
            },		  
		  };
        }
    }
  ]);
