/**
 * :copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.service.measure', [])
  .factory('measure_service', [
    '$http',
    'user_service',
    function ($http, user_service) {
      var measure_service = {};
	  
      /** Returns an array of measures.
       @param {object} meausre   A list of measures objects 

       @return {object}        Returns a promise object which will resolve
       with either a success if the measure was deleted,
       or an error if not.
       */

      measure_service.get_measures = function (params) {
		  params.organization_id = user_service.get_organization().id
        return measure_service.get_measures_for_org(params);
      };

      measure_service.get_measures_for_org = function (params) {
        return $http.get('/api/v2/measures/', {
          params: params
        }).then(function (response) {
  		return response.data;
        });
      };

      /** Returns an array of measure categories.
       @param {object} meausre   A list of measure categories 

       @return {object}        Returns a promise object which will resolve
       with either a success if the measure was deleted,
       or an error if not.
       */

      measure_service.get_measures_categories = function () {
        return measure_service.get_measures_categories_for_org(user_service.get_organization().id);
      };

      measure_service.get_measures_categories_for_org = function (org_id) {
        return $http.get('/api/v2/measures/categories/', {
          params: {
            organization_id: org_id
          }
        }).then(function (response) {
		  return response.data;
        });
      };
	  
      /*  Delete an existing a property measure in an organization

       @param {object} meausre   A property measure object to delete on server.

       @return {object}        Returns a promise object which will resolve
       with either a success if the measure was deleted,
       or an error if not.
       */
      measure_service.delete_property_measure = function (property_measure_id) {
        return measure_service.delete_property_measure_for_org(property_measure_id, user_service.get_organization().id);
      };

      measure_service.delete_property_measure_for_org = function (property_measure_id, org_id) {
        return $http.delete('/api/v2/property_measures/' + property_measure_id + '/', {
  		params: {
            organization_id: org_id
          }
        }).then(function (response) {
          return response.data;
        });
      };
	  
      /*  Add a measure to a property

       @param {object} measure       Measure object to use for creating measure on server.

       @return {object}            Returns a promise object which will resolve
       with either a success if the measure was created
       on the server, or an error if the certification could not be
       created on the server.

       */
      measure_service.create_property_measure = function (property_measure) {
        return measure_service.create_property_measure_for_org(property_measure, user_service.get_organization().id);
      };

      measure_service.create_property_measure_for_org = function (property_measure, org_id) {
		  console.log(property_measure)
        return $http.post('/api/v2/property_measures/', property_measure, {
          params: {
            organization_id: org_id
          }
        }).then(function (response) {
		  console.log(response)
          return response.data;
        });
      };
	  	  
      return measure_service;
    }
  ]);