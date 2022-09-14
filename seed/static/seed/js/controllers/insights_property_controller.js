angular.module('BE.seed.controller.insights_property', [])
  .controller('insights_property_controller', [
    '$scope',
    '$stateParams',
    '$uibModal',
    'urls',
    'compliance_metrics',
    'compliance_metric_service',
    'spinner_utility',
    'cycles',
    function (
      $scope,
      $stateParams,
      $uibModal,
      urls,
      compliance_metrics,
      compliance_metric_service,
      spinner_utility,
      cycles
    ) {

      $scope.id = $stateParams.id;
      $scope.cycles = cycles.cycles;
      console.log("CYCLES: ", $scope.cycles);

      // compliance metric
      $scope.compliance_metric = {};
      // for now there should always be 1 (get_or_create_default function in compliance_metrics list api)
      // in the future there will be multiple
      if (compliance_metrics.length > 0) {
        $scope.compliance_metric = compliance_metrics[0];
      }
      console.log("COMPLIANCE METRIC: ", $scope.compliance_metric);

      // chart data
      $scope.data = {};
      $scope.chart_datasets = {};

      // default settings / dropdowns
      $scope.chart_cycle = _.last($scope.cycles).id;
      $scope.chart_metric = null;
      $scope.chart_xaxis = null;
      $scope.x_axis_options = [];
      $scope.y_axis_options = [];
      $scope.x_categorical = false;

      // load data
      let _load_data = function () {
        if (!$scope.compliance_metric) {
          spinner_utility.hide();
          return;
        }
        spinner_utility.show();
        let data = compliance_metric_service.evaluate_compliance_metric($scope.compliance_metric.id).then((data) => {
          $scope.data = data;
          spinner_utility.hide();
        }).then(() => {
          console.log( "DATA RETURNED: ", $scope.data)
          if ($scope.data) {
            // set options
            // x axis
            $scope.x_axis_options = $scope.data.metric.x_axis_columns;

            if (_.size($scope.x_axis_options) > 0) {
              $scope.chart_xaxis = _.first($scope.x_axis_options).id;
            }
            // y axis
            if ($scope.data.metric.energy_metric == true){
              $scope.y_axis_options.push({'id': 0, 'name': 'Energy Metric'})
            }
            if ($scope.data.metric.emission_metric == true){
              $scope.y_axis_options.push({'id': 1, 'name': 'Emission Metric'})
            }
            if (_.size($scope.y_axis_options) > 0) {
              $scope.chart_metric = _.first($scope.y_axis_options).id;
            }

          }
          _rebuild_datasets();

          // once
          _build_chart();

        })
      };

      $scope.update = function() {
        spinner_utility.show();

        console.log('chart_cycle is now: ', $scope.chart_cycle)
        console.log('xaxis is now: ', $scope.chart_xaxis)
        console.log('Metric is now: ', $scope.chart_metric)

        // redraw dataset
        _rebuild_datasets();
        // update chart
        _update_chart();

        spinner_utility.hide();
      }

      const _rebuild_datasets = () => {
        console.log("REBUILD DATASETS")

        $scope.x_categorical = false;

        let datasets = [{'data': [], 'label': 'compliant', 'pointStyle': 'circle'},
        {'data': [], 'label': 'non-compliant', 'pointStyle': 'triangle', 'radius': 7},
        {'data': [], 'label': 'unknown', 'pointStyle': 'rect'}]

        _.forEach($scope.data.properties_by_cycles[$scope.chart_cycle], function(prop) {
          //console.log("PROP: ", prop.property_view_id)
          item = {}
          // x axis is easy
          item['x'] = _.find(prop, function(v, k) {
            return _.endsWith(k, '_' + String($scope.chart_xaxis));
          });

          // is x axis categorical?
          if ($scope.x_categorical == false && isNaN(item['x'])) {
            $scope.x_categorical = true;
          }

          // y axis depends on metric selection
          if ($scope.chart_metric == 0) {

            // ENERGY
            item['y'] = _.find(prop, function(v, k) {
              return _.endsWith(k, '_' + String($scope.data.metric.actual_energy_column));
            });
            if ($scope.data.metric.energy_bool == false) {
              item['target'] = _.find(prop, function(v, k) {
                return _.endsWith(k, '_' + String($scope.data.metric.target_energy_column));
              });
            }
          } else if ($scope.chart_metric == 1) {
            // EMISSIONS
            item['y'] = _.find(prop, function(v, k) {
              return _.endsWith(k, '_' + String($scope.data.metric.actual_emission_column));
            });
            if ($scope.data.metric.emission_bool == false) {
              item['target'] = _.find(prop, function(v, k) {
                return _.endsWith(k, '_' + String($scope.data.metric.target_emission_column));
              });
            }
          }

          // place in appropriate dataset
          if (_.includes($scope.data.results_by_cycles[$scope.chart_cycle]['y'], prop.property_view_id)) {
            datasets[0]['data'].push(item);
          } else if (_.includes($scope.data.results_by_cycles[$scope.chart_cycle]['n'], prop.property_view_id)) {
            datasets[1]['data'].push(item);
          } else {
            datasets[2]['data'].push(item);
          }
        });

        console.log("DATASETS BUILT: ", datasets);
        console.log("CATEGORICAL X axis? ", $scope.x_categorical);
        $scope.chart_datasets = datasets;

      }

      // CHARTS
      var colors = {'compliant': '#77CCCB', 'non-compliant': '#A94455', 'unknown': '#EEEEEE'}

      const _build_chart = () => {
        console.log('BUILD CHART')
        if (!$scope.chart_datasets) {
          console.log('NO DATA')
          return
        }
        const canvas = document.getElementById('property-insights-chart')
        const ctx = canvas.getContext('2d')


        $scope.insightsChart = new Chart(ctx, {
          type: 'scatter',
          data: {
          },
          options: {
            elements: {
              point: {
                radius: 5
              }
            },
            plugins: {
              title: {
                display: true,
                align: 'start'
              },
              legend: {
                display: false
              },
            },
            scales: {
              x: {
                title: {
                  text: 'X',
                  display: true
                },
                ticks: {
                    callback: function(value, index, ticks) {
                      return this.getLabelForValue(value).replace(',', '')
                    }
                },
                type: 'linear'
              },
              y: {
                beginAtZero: true,
                stacked: true,
                position: 'left',
                display: true,
                title: {
                  text: 'Y',
                  display: true
                }
              }
            }
          }
        });

        // load data
        console.log('UPDATE CHART');
        _update_chart();
        console.log('BUILD CHART COMPLETE ')
        console.log("CHART DATA: ", $scope.insightsChart.data)

      }

      const _update_chart = () => {
        let x_index = _.findIndex($scope.data.metric.x_axis_columns, {'id': $scope.chart_xaxis});
        let x_axis_name = $scope.data.metric.x_axis_columns[x_index].display_name;

        let y_axis_name = null;
        if ($scope.chart_metric ==  0){
          y_axis_name = $scope.data.metric.actual_energy_column_name;
        } else if ($scope.chart_metric == 1){
          y_axis_name = $scope.data.metric.actual_emission_column_name;
        }

        // update axes
        $scope.insightsChart.options.scales.x.title.text = x_axis_name;
        $scope.insightsChart.options.scales.y.title.text = y_axis_name;

        // check if x-axis is categorical
        console.log("HEY: ")
        $scope.insightsChart.options.scales.x.type = $scope.x_categorical == true ? 'category' : 'linear'

        // update chart datasets

        $scope.insightsChart.data.datasets = $scope.chart_datasets;
        _.forEach($scope.insightsChart.data.datasets, function(ds) {
          ds['backgroundColor'] = colors[ds['label']]
        });

        //labels needed for categorical?
        //$scope.insightsChart.options.scales.x.labels = [];
        $scope.insightsChart.data.labels = [];

        if ($scope.x_categorical) {
          let labels = [];
          _.forEach($scope.chart_datasets, function(ds) {
            labels = _.uniq(_.concat(labels, _.map(ds['data'], 'x')))
          });
          labels = labels.filter(function( element ) {
             return element !== undefined;
          });
          //$scope.insightsChart.options.scales.x.labels = labels;
          $scope.insightsChart.data.labels = labels;
        }
        //console.log("LABELS: ", $scope.insightsChart.options.scales.x.labels)

        console.log("REFRESH CHART");
        $scope.insightsChart.update()
        console.log("HEY HEY")
        console.log($scope.insightsChart.data.labels)
      }

      _load_data();

    }

  ]);
