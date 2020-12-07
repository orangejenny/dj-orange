var DayModel = function (options) {
    var today = new Date();
    var self = ko.mapping.fromJS($.extend({
        id: undefined,
        day: today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + (today.getDate()),
        notes: undefined,
        workouts: [],
    }, options));

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
        self.workouts.push(WorkoutModel());
    };

    return self;
};

// Only used to set defaults. DayModel's workouts property is plain objects, not WorkoutModels
var WorkoutModel = function (options) {
    var self = ko.mapping.fromJS($.extend({
        id: undefined,
        activity: undefined,
        distance: undefined,
        distance_unit: undefined,
        seconds: undefined,
        sets: undefined,
        reps: undefined,
        weight: undefined,
    }, options));
    return self;
};

var KiloModel = function () {
    var self = {};

    self.recentDays = ko.observableArray();
    self.workoutTemplates = ko.observableArray();
    self.stats = ko.observableArray();
    self.currentDay = ko.observable();
    self.activity = ko.observable();

    // Populate templates for new day
    self.recentDays.subscribe(function (newValue) {
        var templates = [];
        var index = 0;
        while (index < newValue.length && templates.length < 3) {
            var workout = newValue[index].workouts()[0];
            if (!workout) {
                continue;
            }
            workout = ko.mapping.toJS(workout);
            var template = $.extend({}, workout);
            delete template.seconds;
            if (!templates.find(t => t.activity === template.activity && t.distance === template.distance)) {
                templates.push(template);
            }
            index++;
        }
        self.workoutTemplates(templates);
    });

    self.getPanel = function (activity) {
        $.ajax({
            url: '/kilo/panel',
            method: 'GET',
            data: {
                activity: self.activity(),
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
        var data = $(e.currentTarget).data();
        if (data.id) {
            self.currentDay(self.recentDays().find(d => d.id() === data.id));
        } else {
            var workout = WorkoutModel({
                activity: self.activity(),
            });
            if (data.template) {
                workout = data.template;
            }
            self.currentDay(DayModel({
                workouts: [workout],
            }));
        }
        $("#edit-day").modal();
    };

    $(function () {
        self.activity($(".navbar .navbar-nav .nav-item.active").data("activity"));
        self.getPanel(self.activity());
    });

    return self;
};

$(function () {
    ko.applyBindings(KiloModel());
});
