/**
 * :copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.inventory_cycles', [])
  .controller('inventory_cycles_controller', [
    '$scope',
    '$filter',
    '$window',
    '$uibModal',
    '$sce',
    '$stateParams',
    'inventory_service',
    'user_service',
    'inventory',
    'cycles',
    'profiles',
    'current_profile',
    'all_columns',
    'urls',
    'spinner_utility',
    'naturalSort',
    'matching_criteria_columns',
    '$translate',
    'uiGridConstants',
    'uiGridGroupingConstants',
    'i18nService', // from ui-grid
    function (
      $scope,
      $filter,
      $window,
      $uibModal,
      $sce,
      $stateParams,
      inventory_service,
      user_service,
      inventory,
      cycles,
      profiles,
      current_profile,
      all_columns,
      urls,
      spinner_utility,
      naturalSort,
      matching_criteria_columns,
      $translate,
      uiGridConstants,
      uiGridGroupingConstants,
      i18nService
    ) {
      spinner_utility.show();
      $scope.inventory_type = $stateParams.inventory_type;

      // matching_criteria_columns identified here to (always) pin left on table
      if ($scope.inventory_type == "properties") {
        $scope.matching_criteria_columns = matching_criteria_columns.PropertyState;
      } else {
        $scope.matching_criteria_columns = matching_criteria_columns.TaxLotState;
      }

      // Establish all cycle options and initially included cycles
      $scope.included_cycle_ids = [];
      $scope.cycle_options = _.map(cycles.cycles, function(cycle) {
        $scope.included_cycle_ids.push(cycle.id);

        return {
          selected: true,
          label: cycle.name,
          value: cycle.id,
        };
      });

      // Checks for changes and refreshes grid objects if necessary
      $scope.cycle_selection_toggled = function (is_open) {
        if (!is_open) {
          var updated_selections = _.map(_.filter($scope.cycle_options, ['selected', true]), 'value');
          if (!_.isEqual($scope.included_cycle_ids, updated_selections)) {
            $scope.included_cycle_ids = updated_selections;
            $scope.refresh_objects();
          }
        }
      };

      // Takes raw cycle-partitioned records and returns array of cycle-aware records
      $scope.reformat_records = function(refreshed_inventory) {
        return _.reduce(refreshed_inventory, function(all_records, records, cycle_id) {
          var cycle = _.find($scope.cycle_options, { value: parseInt(cycle_id) });
          _.forEach(records, function(record) {
            record.cycle_name = cycle.label;
            all_records.push(record)
          })
          return all_records
        }, []);
      };

      $scope.refresh_objects = function() {
        spinner_utility.show();
        if ($scope.inventory_type == "properties") {
          inventory_service.properties_cycle($scope.currentProfile.id, $scope.included_cycle_ids).then(function(refreshed_inventory) {
            $scope.data = $scope.reformat_records(refreshed_inventory);
            spinner_utility.hide();
          });
        } else {
          // inventory_service.taxlots_cycle($scope.currentProfile.id, $scope.included_cycle_ids).then(function(refreshed_inventory) {
          //   $scope.data = $scope.reformat_records(refreshed_inventory);
          //   spinner_utility.hide();
          // });
        }
      };

      $scope.data = $scope.reformat_records(inventory);

      // set up i18n
      //
      // let angular-translate be in charge ... need
      // to feed the language-only part of its $translate setting into
      // ui-grid's i18nService
      var stripRegion = function (languageTag) {
        return _.first(languageTag.split('_'));
      };
      i18nService.setCurrentLang(stripRegion($translate.proposedLanguage() || $translate.use()));

      // List Settings Profile
      $scope.profiles = profiles;
      $scope.currentProfile = current_profile;

      if ($scope.currentProfile) {
        $scope.columns = [];
        _.forEach($scope.currentProfile.columns, function (col) {
          var foundCol = _.find(all_columns, {id: col.id});
          if (foundCol) {
            foundCol.pinnedLeft = col.pinned;
            $scope.columns.push(foundCol);
          }
        });
      } else {
        // No profiles exist
        $scope.columns = _.reject(all_columns, 'is_extra_data');
      }

      // Build out columnDefs
      var matching_field_value = function(aggregation, fieldValue) {
        aggregation.value = fieldValue;
      };

      var column_def_defaults = {
        headerCellFilter: 'translate',
        minWidth: 75,
        width: 150
      };

      _.map($scope.columns, function (col) {
        var options = {};
        if (col.data_type === 'datetime') {
          options.cellFilter = 'date:\'yyyy-MM-dd h:mm a\'';
        } // else if (['eui', 'interger'].includes(col.data_type)) {
        //   options.cellTemplate = '<div ng-if="row.groupHeader" class="ui-grid-cell-contents" tooltip-append-to-body="true" tooltip-popup-delay="500" title="TOOLTIP">[tooltip-placeholder?]</div>' +
        //     '<div ng-if="!row.groupHeader" class="ui-grid-cell-contents">{{COL_FIELD CUSTOM_FILTERS}}</div>'
        // }

        if ($scope.matching_criteria_columns.includes(col.column_name)) {
          col.pinnedLeft = true; // always overrides what's given
          options.customTreeAggregationFn = matching_field_value;
        }
        return _.defaults(col, options, column_def_defaults);
      });

      $scope.columns.unshift(
        {
          displayName: 'Linking ID',
          grouping: { groupPriority: 0 },
          name: 'id',
          sort: { priority: 0, direction: 'desc' },
          pinnedLeft: true,
          visible: false,
          minWidth: 75,
          width: 150
        },
        {
          name: "cycle_name",
          displayName: "Cycle",
          pinnedLeft: true,
          treeAggregationType: uiGridGroupingConstants.aggregation.COUNT,
          minWidth: 75,
          width: 150
        },
      )

      $scope.gridOptions = {
        data: 'data',
        columnDefs: $scope.columns,
        enableColumnResizing: true,
      };

      // console.log("currentProfile", $scope.currentProfile);
      // console.log("current_profile", current_profile);
      // console.log("data", $scope.data);
      // console.log("incoming cycles", cycles.cycles);
      // console.log("cycle_options", $scope.cycle_options);
      // console.log('inventory', inventory);
      // console.log('columns', $scope.columns);
      // console.log('matching_criteria_columns', $scope.matching_criteria_columns);
    }]);
