/**
 * :copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
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
    data_quality_factory.get_data_quality_results = function (org_id, data_quality_id) {
      return $http.get('/api/v2/data_quality_checks/results/?organization_id=' + org_id + '&data_quality_id=' + data_quality_id).then(function (response) {
        return response.data.data;
      });
    };

    /**
     * gets the data quality rules for an org
     * @param  {int} org_id the id of the organization
     */
    data_quality_factory.data_quality_rules = function (org_id) {
      return $http.get('/api/v2/data_quality_checks/data_quality_rules/?organization_id=' + org_id).then(function (response) {
        return response.data;
      });
    };

    /**
     * resets default data data_quality rules for an org and destroys custom rules
     * @param  {int} org_id the id of the organization
     */
    data_quality_factory.reset_all_data_quality_rules = function (org_id) {
      return $http.put('/api/v2/data_quality_checks/reset_all_data_quality_rules/?organization_id=' + org_id).then(function (response) {
        return response.data;
      });
    };

    /**
     * resets default data data_quality rules for an org
     * @param  {int} org_id the id of the organization
     */
    data_quality_factory.reset_default_data_quality_rules = function (org_id) {
      return $http.put('/api/v2/data_quality_checks/reset_default_data_quality_rules/?organization_id=' + org_id).then(function (response) {
        return response.data;
      });
    };

    /**
     * saves the organization data data_quality rules
     * @param  {int} org_id the id of the organization
     * @param  {obj} data_quality_rules the updated rules to save
     */
    data_quality_factory.save_data_quality_rules = function (org_id, data_quality_rules) {
      return $http.post('/api/v2/data_quality_checks/save_data_quality_rules/?organization_id=' + org_id, {
        data_quality_rules: data_quality_rules
      }).then(function (response) {
        return response.data;
      });
    };
	
	/**
	 * retrieves data quality actions
	 * @param {int} org_id the id of the organization
	 */
    data_quality_factory.get_data_qualities = function (org_id) {
      return $http.get('/api/v2/data_quality/?organization_id=' + org_id).then(function (response) {
        var data_qualities = _.filter(response.data.data, {
        }).sort(function (a, b) {
          return naturalSort(a.name, b.name);
        });

        _.forEach(data_qualities, function (dq) {
          // Remove exact duplicates - this shouldn't be necessary, but it has occurred and will avoid errors and cleanup the database at the same time
          dq.columns = _.uniqWith(dq.columns, _.isEqual);

          dq.columns = _.sortBy(dq.columns, ['order', 'column_name']);
        });
        return data_qualities;
      });
    };
	
    data_quality_factory.get_last_data_quality = function (organization_id) {
      return (JSON.parse(localStorage.getItem('data_qualities')) || {})[organization_id];
    };

    data_quality_factory.save_last_data_quality = function (pk, organization_id) {
      data_qualities = JSON.parse(localStorage.getItem('data_qualities')) || {};
	  console.log(data_qualities)
      data_qualities[organization_id] = _.toInteger(pk);
      localStorage.setItem('data_qualities', JSON.stringify(data_qualities));
    };

	/**
	 * creates new data quality action
	 * @param {char} name of the new action
	 * @param {int} org_id the id of the organization
	 */
    data_quality_factory.new_data_quality = function (data) {
      return $http.post('/api/v2/data_quality/', {
        organization: user_service.get_organization().id,
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
    data_quality_factory.remove_data_quality = function (id) {
      return $http.delete('/api/v2/data_quality/' + id + '/', {
        params: {
          organization_id: user_service.get_organization().id
        }
      });
    };

    data_quality_factory.start_data_quality_checks_for_import_file = function (org_id, import_file_id) {
      return $http.post('/api/v2/import_files/' + import_file_id + '/start_data_quality_checks/?organization_id=' + org_id).then(function (response) {
        return response.data;
      });
    };

    data_quality_factory.start_data_quality_checks = function (property_state_ids, taxlot_state_ids) {
      return data_quality_factory.start_data_quality_checks_for_org(user_service.get_organization().id, property_state_ids, taxlot_state_ids);
    };

    data_quality_factory.start_data_quality_checks_for_org = function (org_id, property_state_ids, taxlot_state_ids) {
      return $http.post('/api/v2/data_quality_checks/?organization_id=' + org_id, {
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
      $http.get('/api/v2/progress/' + progress_key + '/').then(function (response) {
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
