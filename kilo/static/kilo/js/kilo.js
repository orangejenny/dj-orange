var DayModel = function (options) {
    if (!options.day) {
        throw new Error("DayModel must be given a day");
    }
    var self = ko.mapping.fromJS(options);

    var parts = self.day().split("-");
    self.year = ko.observable(parts[0]);
    self.month = ko.observable(parts[1]);
    self.day_of_month = ko.observable(parts[2]);

    self.date = ko.computed(function () {
        return new Date(self.year(), self.month() - 1, self.day_of_month());
    });

    self.dayOfWeek = ko.computed(function () {
        return ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][self.date().getDay()];
    });

    self.addWorkout = function () {
        self.workouts.push({
            id: undefined,
            activity: undefined,
            distance: undefined,
            distance_unit: undefined,
            seconds: undefined,
            sets: undefined,
            reps: undefined,
            weight: undefined,
        });
    };

    return self;
};

var KiloModel = function () {
    var self = {};

    self.recentDays = ko.observableArray();
    self.stats = ko.observableArray();
    self.currentDay = ko.observable();

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
                self.recentDays(data.recent_days.map(d => DayModel(d)));
                self.stats(data.stats);

                c3.generate({
                    bindto: '#graph',
                    data: data.graph_data,
                    axis: {
                        x: {
                            type: 'timeseries',
                            tick: {
                                format: '%Y-%m-%d'
                            }
                        }
                    },
                });
            },
        });
    };

    self.openModal = function (model, e) {
        var id = $(e.currentTarget).data("id");
        if (id) {
            self.currentDay(self.recentDays().find(d => d.id() === id));
        } else {
            var today = new Date();
            self.currentDay(DayModel({
                id: undefined,
                day: today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + (today.getDate()),
                notes: "",
                workouts: [],
            }));
        }
        $("#edit-day").modal();
    };

    self.getPanel();

    return self;
};

$(function () {
    ko.applyBindings(KiloModel());
});
