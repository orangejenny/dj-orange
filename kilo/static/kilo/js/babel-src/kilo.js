import { App } from "./components.js"

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

    self.addWorkout = function () {
        var options = {};
        if (self.workouts().length) {
            var template = self.workouts()[self.workouts().length - 1];
            options = _.omit(ko.toJS(template), ['id', 'seconds']);
        }
        self.workouts.push(WorkoutModel(options));
    };

    self.removeWorkout = function (model) {
        self.workouts.remove(model);
    }

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

var getPace = function(workout) {
    if (workout.seconds() && workout.distance()) {
        var pace = workout.seconds() / workout.distance();
        if (workout.activity() === "erging") {
            // Paces for m workouts are given in km
            if (workout.distance_unit() === "m") {
                pace = pace * 1000;
            }
            // Paces for ergs are per 500m, not 1k
            if (workout.distance_unit() === "km" || workout.distance_unit() === "m") {
                pace = pace / 2;
            }
        }
        return getTime(pace);
    }
    return "";
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

    self.isLifting = ko.computed(function () {
        return self.activity() === "lifting";
    });

    self.pace = ko.computed(function () {
        return getPace(self);
    });

    return self;
};

var KiloModel = function () {
    var self = {};

    self.recentDays = ko.observableArray();
    self.workoutTemplates = ko.observableArray();
    self.currentDay = ko.observable();
    self.activity = ko.observable();

    // Populate templates for new day
    self.recentDays.subscribe(function (newValue) {
        var templates = [];
        var index = 0;
        while (index < newValue.length && templates.length < 3) {
            var workout = newValue[index].workouts()[0];
            index++;
            if (!workout) {
                continue;
            }
            workout = ko.mapping.toJS(workout);
            var template = $.extend({}, _.omit(workout, 'id'));
            delete template.seconds;
            if (!templates.find(t => t.activity === template.activity && t.distance === template.distance)) {
                templates.push(template);
            }
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
            },
        });
    };

    self.showCurrentDay = function (model, e) {
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
    };

    self.clearCurrentDay = function () {
        self.currentDay(undefined);
    };

    $(function () {
        self.activity($(".navbar .navbar-nav .nav-item.active").data("activity"));
        self.getPanel(self.activity());
    });

    return self;
};

$(function () {
    ko.applyBindings(KiloModel());

    var activity = $(".navbar .navbar-nav .nav-item.active").data("activity");
    ReactDOM.render(React.createElement(App, {activity: activity}), document.getElementById("app"));
});