/**
 * :copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.service.certification', []).factory('certification_service', [
  '$http',
  'user_service',
  function ($http, user_service) {

    var certification_service = {};
    /** Certification Service:
     --------------------------------------------------
     Provides methods to add/edit certifications (green assessment) on the server.
     */


    /** Returns an array of certifications (green assessments).

     Returned certification objects should have the following properties

     id {integer}            The id of the Certification.
     name {string}           The text that appears in the Certification.
	 *** TO DO ***

     */

    certification_service.get_certifications = function () {
      return certification_service.get_certifications_for_org(user_service.get_organization().id);
    };

    certification_service.get_certifications_for_org = function (org_id) {
      return $http.get('/api/v2/green_assessments/', {
        params: {
          organization_id: org_id
        }
      }).then(function (response) {
		return response.data;
      });
    };


    /*  Add a certification (green assessment) to an organization's list of certifications

     @param {object} certification       Certification object to use for creating certification on server.

     @return {object}            Returns a promise object which will resolve
     with either a success if the certification was created
     on the server, or an error if the certification could not be
     created on the server.

     */
    certification_service.create_certification = function (certification) {
      return certification_service.create_certification_for_org(certification, user_service.get_organization().id);
    };

    certification_service.create_certification_for_org = function (certification, org_id) {
      return $http.post('/api/v2/green_assessments/', certification, {
        params: {
          organization_id: org_id
        }
      }).then(function (response) {
        return response.data;
      });
    };


    /*  Update an existing a certification (green assessment) in an organization

     @param {object} certification   A certification object with changed properties to update on server.
     The object must include property 'id' for certification ID.

     @return {object}        Returns a promise object which will resolve
     with either a success if the certification was updated,
     or an error if not.
     */
    certification_service.update_certification = function (certification) {
		return certification_service.update_certification_for_org(certification, user_service.get_organization().id);
    };

    certification_service.update_certification_for_org = function (certification, org_id) {
      return $http.put('/api/v2/green_assessments/' + certification.id + '/', certification, {
        params: {
          organization_id: org_id
        }
      }).then(function (response) {
        return response.data;
      });
    };

    /*  Delete an existing a certification (green assessment) in an organization

     @param {object} certification   A certification object to delete on server.
     The object must include property 'id' for certification ID.

     @return {object}        Returns a promise object which will resolve
     with either a success if the certification was deleted,
     or an error if not.
     */
    certification_service.delete_certification = function (certification_id) {
      return certification_service.delete_certification_for_org(certification_id, user_service.get_organization().id);
    };

    certification_service.delete_certification_for_org = function (certification_id, org_id) {
      return $http.delete('/api/v2/green_assessments/' + certification_id + '/', {
		params: {
          organization_id: org_id
        }
      }).then(function (response) {
        return response.data;
      });
    };

    /*  Delete an existing a green assessment in an organization

     @param {object} certification   A certification object to delete on server.
     The object must include property 'id' for certification ID.

     @return {object}        Returns a promise object which will resolve
     with either a success if the certification was deleted,
     or an error if not.
     */
    certification_service.delete_assessment = function (assessment_id) {
      return certification_service.delete_assessment_for_org(assessment_id, user_service.get_organization().id);
    };

    certification_service.delete_assessment_for_org = function (assessment_id, org_id) {
      return $http.delete('/api/v2/green_assessment_properties/' + assessment_id + '/', {
		params: {
          organization_id: org_id
        }
      }).then(function (response) {
        return response.data;
      });
    };
	
    /*  Delete an existing a green assessment URL in an organization

     @param {object} certification URL    A certification URL object to delete on server.
     The object must include property 'id' for certification ID.

     @return {object}        Returns a promise object which will resolve
     with either a success if the certification was deleted,
     or an error if not.
     */
    certification_service.delete_assessment_url = function (assessment_url_id) {
      return certification_service.delete_assessment_url_for_org(assessment_url_id, user_service.get_organization().id);
    };

    certification_service.delete_assessment_url_for_org = function (assessment_url_id, org_id) {
      return $http.delete('/api/v2/green_assessment_urls/' + assessment_url_id + '/', {
		params: {
          organization_id: org_id
        }
      }).then(function (response) {
        return response.data;
      });
    };
	
    /*  Update an existing a property green assessment in an organization

     @param {object} property assessment  A certification object with changed properties to update on server.
     The object must include property 'id' for certification ID.

     @return {object}        Returns a promise object which will resolve
     with either a success if the certification was updated,
     or an error if not.
     */
    certification_service.update_assessment = function (assessment) {
		return certification_service.update_assessment_for_org(assessment, user_service.get_organization().id);
    };

    certification_service.update_assessment_for_org = function (assessment, org_id) {
      return $http.put('/api/v2/green_assessment_properties/' + assessment.id + '/', assessment, {
        params: {
          organization_id: org_id
        }
      }).then(function (response) {
        return response.data;
      });
    };
	
    return certification_service;
  }]);
