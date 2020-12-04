$(function () {
    $.ajax({
        url: '/miles/panel',    // TODO
        success: function (data) {
            ko.applyBindings({
                recent_days: data.recent_days,
                stats: data.stats,
            });
        },
    });
});
