/**
 * :copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.create_measure_modal', [])
  .controller('create_measure_modal_controller', [
    '$scope',
    '$uibModalInstance',
	'Notification',
    'measure_service',
    'property_state',
	  function ($scope, $uibModalInstance, Notification, measure_service, property_state) {
//      $scope.property_measure = property_measure;
	  initialize_new_measure();
	  $scope.measure_status = ['Proposed', 'Evaluated', 'Selected', 'Initiated', 'Discarded', 'In Progress', 'Completed', 'MV', 'Verified', 'Unsatisfactory'];
	  $scope.measure_scale = ['Individual system', 'Multiple systems', 'Individual premise', 'Multiple premises', 'Entire facility', 'Entire site', 'Ground Mounted', 'Roof Mounted', 'Solar Canopy', 'Entire building', 'Common areas', 'Tenant areas']
	  $scope.category_affected = ['Air Distribution', 'Heating System', 'Cooling System', 'Other HVAC', 'Lighting', 'Domestic Hot Water', 'Cooking', 'Refrigeration', 
  'Dishwasher', 'Laundry', 'Pump', 'Fan', 'Motor', 'Heat Recovery', 'Wall', 'Roof', 'Ceiling', 'Fenestration', 'Foundation', 'General Controls and Operations', 'Critical IT System', 
  'Plug Load', 'Process Load', 'Conveyance', 'On-Site Storage, Transmission, Generation', 'On-Site Storage, Transmission, Generation', 'Pool', 'Water Use', 'Other']
	  $scope.financing =  [["LEASE","Leased Renewables"], ["PPA","Power Purchase Agreement"], ["PACE","Property-Assessed Clean Energy"]]
	  $scope.ownership = [["OWN", "Seller Owned"], ["3RD", "Third-Party Owned"]]
	  $scope.source = [["ADMIN", "Administrator"], ["ASSES", "Assessor"], ["BILDR", "Builder"], ["CONTR", "Contractor/Installer"], ["OTH", "Other"], ["OWN", "Owner"], ["SPNSR", "Program Sponsor"], ["VERIF", "Program Verifier"], ["PUBRE", "Public Records"]]
	  
	  measure_service.get_measures_categories().then(function(categories) {
		  $scope.measure_categories = categories.categories;
	  });
	  
	  $scope.update_category = function(){
		  params = {'category': $scope.category[0]}
		  measure_service.get_measures(params).then(function(measures) {
			  $scope.measures = measures;
		  });
	  }
	   
      $scope.create_measure = function () {
		  property_measure = $scope.measure
		  console.log($scope.measure)
		  property_measure.measure = property_measure.id.id
		  if ('current_financing' in $scope.measure) property_measure.current_financing = $scope.measure.current_financing[0] 
		  if ('ownership' in $scope.measure) property_measure.ownership = $scope.measure.ownership[0] 
		  if ('source' in $scope.measure) property_measure.source = $scope.measure.source[0] 
		  delete property_measure.id
		  property_measure.property_state = property_state
		  property_measure.property_measure_name = 'Test Name'
		  console.log(property_measure)		  
		  
        measure_service.create_property_measure(property_measure).then(function () {
          $uibModalInstance.close();
	      var msg = 'Created new measure ' + property_measure.description;
	      Notification.primary(msg);
        });
	  };

      $scope.cancel = function () {
        $uibModalInstance.dismiss();
      };
	  
      function initialize_new_measure () {
        $scope.property_measure = {
		  name: "", 
		  description: "",
	  };
      }
	  
    }]);