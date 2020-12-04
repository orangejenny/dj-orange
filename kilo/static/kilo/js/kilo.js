var KiloModel = function () {
    var self = {};

    self.recent_days = ko.observableArray();
    self.stats = ko.observableArray();

    self.activity = ko.observable();
    self.updateActivity = function (model, e) {
        self.activity($(e.currentTarget).data("activity"));
    };
    self.activity.subscribe(function (newValue) {
        self.getPanel(newValue);
    });

    self.getPanel = function (activity) {
        $.ajax({
            url: '/kilo/panel',
            method: 'GET',
            data: {
                activity: activity,
            },
            success: function (data) {
                self.recent_days(data.recent_days);
                self.stats(data.stats);
            },
        });
    };

    self.getPanel();

    return self;
};

$(function () {
    ko.applyBindings(KiloModel());
});
