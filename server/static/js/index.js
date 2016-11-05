require(['lib/jquery', 'js/views/dashboard/dashboard.view'],
    function($, DashboardView) {

    $('.navbar-menu').click(function(){
        $('.navbar-items').animate({height: 'toggle'}, 200);
    });

    var generalDashboard = new DashboardView();

    $('.dashboard-container').html(generalDashboard.render().el);

});