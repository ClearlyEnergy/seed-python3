/**
 * :copyright (c) 2014 - 2021, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
// data_quality services
angular.module('BE.seed.service.data_quality', []).factory('data_quality_service', [
  '$http',
  '$q',
  '$timeout',
  'user_service',
  'naturalSort',
  function ($http, $q, $timeout, user_service, naturalSort) {
    var data_quality_factory = {};

    /**
     * get_data_quality_results
     * return data_quality results from the ID of the storage.
     * @param  {int} org_id the id of the organization
     * @param  {int} data_quality_id, ID of the data quality results
     */
    data_quality_factory.get_data_quality_results = function (org_id, run_id) {
      return $http.get('/api/v3/data_quality_checks/results/?organization_id=' + org_id + '&run_id=' + run_id).then(function (response) {
        return response.data.data;
      });
    };

    /**
     * return data_quality results in CSV format.
     * @param  {int} org_id the id of the organization
     * @param  {int} run_id, ID of the data quality results
     */
    data_quality_factory.get_data_quality_results_csv = function (org_id, run_id) {
      return $http.get('/api/v3/data_quality_checks/results_csv/?organization_id=' + org_id + '&run_id=' + run_id).then(function (response) {
        return response.data;
      });
    };

    /**
     * gets the data quality rules for an org
     * @param  {int} org_id the id of the organization
     */
    data_quality_factory.data_quality_rules = function (org_id) {
      return $http.get('/api/v3/data_quality_checks/' + org_id + '/rules/').then(function (response) {
        return response.data;
      });
    };

    /**
     * resets default data data_quality rules for an org and destroys custom rules
     * @param  {int} org_id the id of the organization
     */
    data_quality_factory.reset_all_data_quality_rules = function (org_id, dq_id) {
      return $http.put('/api/v3/data_quality_checks/' + org_id + '/rules/reset/', {data_quality_id: dq_id}).then(function (response) {
        return response.data;
      });
    };

    /**
     * create a data quality rule
     * @param  {int} org_id the ID of the organization
     * @param  {obj} rule the details of the rule
     */
    data_quality_factory.create_data_quality_rule = function (org_id, rule) {
      return $http.post('/api/v3/data_quality_checks/' + org_id + '/rules/', rule).then(function (response) {
        return response.data;
      });
    };

    /**
     * update a data quality rule
     * @param  {int} org_id the ID of the organization
     * @param  {int} rule_id the ID of the rule to update
     * @param  {obj} rule the details of the rule
     */
    data_quality_factory.update_data_quality_rule = function (org_id, rule_id, rule) {
      return $http.put('/api/v3/data_quality_checks/' + org_id + '/rules/' + rule_id + '/', rule).then(function (response) {
        return response.data;
      });
    };

    /**
     * delete a data quality rule
     * @param  {int} org_id the ID of the organization
     * @param  {obj} rule_id the ID of the rule to delete
     */
    data_quality_factory.delete_data_quality_rule = function (org_id, rule_id) {
      return $http.delete('/api/v3/data_quality_checks/' + org_id + '/rules/' + rule_id + '/').then(function (response) {
        return response.data;
      });
    };
	
	/**
	 * update name of data quality action
	 * @param {int} id of data quality action
	 * @param {char} new name of the new action
	 * @param {int} org_id the id of the organization
	 */
	data_quality_factory.update_data_quality = function (id, data){
		return $http.put('/api/v3/data_quality_checks/' + id + '/', data).then(function (response) {
			return response.data.data;
		})		
	}
	
	/**
	 * retrieve last data quality from local storage
	 * @param {int} org_id the id of the organization
	 */
    data_quality_factory.get_last_data_quality = function (organization_id) {
      return (JSON.parse(localStorage.getItem('data_qualities')) || {})[organization_id];
    };

	/**
	 * save last data quality to local storage
	 * @param {int} id of data quality
	 * @param {int} org_id the id of the organization
	 */
    data_quality_factory.save_last_data_quality = function (pk, organization_id) {
      data_qualities = JSON.parse(localStorage.getItem('data_qualities')) || {};
      data_qualities[organization_id] = _.toInteger(pk);
      localStorage.setItem('data_qualities', JSON.stringify(data_qualities));
    };

	/**
	 * creates new data quality action
	 * @param {char} name of the new action
	 * @param {int} org_id the id of the organization
	 */
    data_quality_factory.new_data_quality = function (data) {
      return $http.post('/api/v3/data_quality_checks/', {
		organization: data['organization'],
	    name: data['name'] 
      }).then(function (response) {
        return response.data.data;
      });
    };
	
	/**
	 * removes data quality action
	 * @param {int} id of the data quality action to remove
	 * @param {int} org_id the id of the organization
	 */
    data_quality_factory.remove_data_quality = function (id, org_id) {
      return $http.delete('/api/v3/data_quality_checks/' + id + '/', {
        params: {
		  organization_id: org_id
        }      	
      });
    };
	
    data_quality_factory.start_data_quality_checks_for_import_file = function (org_id, import_file_id) {
      return $http.post('/api/v3/import_files/' + import_file_id + '/start_data_quality_checks/?organization_id=' + org_id).then(function (response) {
        return response.data;
      });
    };

    //data_quality_factory.start_data_quality_checks = function (property_view_ids, taxlot_view_ids) {
    data_quality_factory.start_data_quality_checks = function (data_quality_id, property_view_ids, taxlot_view_ids) {
      // return data_quality_factory.start_data_quality_checks_for_org(user_service.get_organization().id, property_view_ids, taxlot_view_ids);
      return data_quality_factory.start_data_quality_checks_by_id(data_quality_id, property_state_ids, taxlot_state_ids);
    };

    data_quality_factory.start_data_quality_checks_for_org = function (org_id, property_view_ids, taxlot_view_ids) {
      return $http.post('/api/v3/data_quality_checks/' + org_id + '/start/', {
        property_view_ids: property_view_ids,
        taxlot_view_ids: taxlot_view_ids
      }).then(function (response) {
        return response.data;
      });
    };

    data_quality_factory.start_data_quality_checks_by_id = function (data_quality_id, property_state_ids, taxlot_state_ids) {
      return $http.post('/api/v3/data_quality_checks/?data_quality_id=' + data_quality_id, {
        property_state_ids: property_state_ids,
        taxlot_state_ids: taxlot_state_ids
      }).then(function (response) {
        return response.data;
      });
    };

    data_quality_factory.data_quality_checks_status = function (progress_key) {
      var deferred = $q.defer();
      checkStatusLoop(deferred, progress_key);
      return deferred.promise;
    };

    var checkStatusLoop = function (deferred, progress_key) {
      $http.get('/api/v3/progress/' + progress_key + '/').then(function (response) {
        $timeout(function () {
          if (response.data.progress < 100) {
            checkStatusLoop(deferred, progress_key);
          } else {
            deferred.resolve(response.data);
          }
        }, 750);
      }, function (error) {
        deferred.reject(error);
      });
    };

    return data_quality_factory;
  }]);
