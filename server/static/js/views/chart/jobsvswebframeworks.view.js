define(['lib/jquery', 'lib/underscore', 'lib/chartjs',
        'js/views/chart/chart.view'],
	function($, _, Chart, ChartView){

    var JobsVsWebFrameworks = ChartView.extend({

        initialize: function(options) {
            options = options || {};
            options.data = options.data || {};

            options.data = {
                'card-icon': options.data.icon || 'fa fa-pie-chart',
                'title': options.data.title || 'Most Web Frameworks'
            };

            ChartView.prototype.initialize.apply(this, [options]);
        },

        drawChart: function(){
            var ctx = this.$(".card-chart")[0];

			Chart.defaults.global.fontFamily = '"Roboto", sans-serif';

            $.post('/api/jobs-vs-web-frameworks-stat', '', function(response){
                var frameworks = _.sortBy(response.data, function(framework){
                    return framework.jobs;
                }).reverse();

                var labels = [];
                var data = [];

                _.each(frameworks, function(framework){
                    if (labels.length <= 7){
                        labels.push(framework.name);
                    }
                    if (data.length <= 7){
                        data.push(framework.jobs)
                    }
                });

                setTimeout(function(){
                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: labels,
                            datasets: [{
                                data: data,
                                backgroundColor: [
                                    "#FF6384",
                                    "#36A2EB",
                                    "#FFCE56",
                                    "#F7464A",
                                    "#46BFBD",
                                    "rgba(75,192,192,0.4)",
                                    "#196c32"
                                ],
                                hoverBackgroundColor: [
                                    "#FF6384",
                                    "#36A2EB",
                                    "#FFCE56",
                                    "#F7464A",
                                    "#46BFBD",
                                    "rgba(75,192,192,0.4)",
                                    "#196c32"
                                ]
                            }]
                        },
                        options: {
                            legend: {
                                display: true
                            },
                            animation: {
                                duration: 1000
                            },
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }, 0);
            });
        }

    });

    return JobsVsWebFrameworks;

});