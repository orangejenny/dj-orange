var DayModel = function (options) {
    var today = new Date();
    var self = ko.mapping.fromJS($.extend({
        id: undefined,
        day: today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + (today.getDate()),
        notes: undefined,
        workouts: [],
    }, options));

    // Manually map workouts to WorkoutModel
    self.workouts(self.workouts().map(w => WorkoutModel(w)));

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

var getTime = function (seconds) {
    if (!seconds) {
        return undefined;
    }

    var remaining = seconds,
        hours = Math.floor(remaining / 3600);
    remaining -= hours * 3600;
    var minutes = Math.floor(remaining / 60);
    remaining -= minutes * 60;
    seconds = Math.floor(seconds) === seconds ? Math.floor(remaining) : Math.floor(remaining * 10) / 10;

    hours = hours ? hours + ":" : "";
    minutes = (hours && minutes < 10 ? "0" + minutes : minutes) + ":";
    seconds = seconds < 10 ? "0" + seconds : seconds;
    return hours + minutes + seconds;
};

var getSeconds = function (time) {
    if (!time) {
        return undefined;
    }

    var parts = time.split(":"),
        seconds = 0,
        index = 0;
    while (index < parts.length) {
        seconds += parts[index] * Math.pow(60, parts.length - index - 1);
        index++;
    }

    return seconds;
};

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

    self.time = ko.observable(getTime(self.seconds()));
    self.time.subscribe(function (newValue) {
        self.seconds(getSeconds(newValue));
    });

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
                                count: data.graph_data.columns[0].length,
                                format: '%b %d',
                                rotate: 90,
                            },
                        },
                        y: {
                            min: 0,
                            max: activity ? undefined : 7,
                            tick: {
                                count: activity ? undefined : 8,
                                format: activity ? function (seconds) {
                                    return getTime(seconds);
                                } : undefined,
                            },
                            padding: {
                                top: 0,
                                bottom: 0,
                            },
                        },
                    },
                    legend: {
                        show: !activity,
                    },
                    point: {
                        show: !!activity,
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
