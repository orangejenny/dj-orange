export function Workout(options) {
  var self = options;

  self.summary = function () {
    var text = "";
    if (self.sets) {
      text += self.sets + " x ";
    }
    if (self.reps) {
      text += self.reps + " ";
      if (self.distance || self.seconds) {
        text += "x ";
      }
    }
    if (self.distance) {
      text += self.distance + " " + self.distance_unit + " ";
      if (self.seconds) {
        text += "in ";
      }
    }
    if (self.seconds) {
      text += self.time();
      var pace = self.pace();
      if (pace) {
        text += " (" + pace + ") ";
      }
    }
    if (self.weight) {
      text += "@ " + self.weight + "lb";
    }
    return text.trim();
  };

  self.time = function (seconds) {
    if (!seconds) {
        seconds = self.seconds;
    }

    if (!seconds) {
        return undefined;
    }

    var remaining = seconds,
        hours = Math.floor(remaining / 3600);
    remaining -= hours * 3600;
    var minutes = Math.floor(remaining / 60);
    remaining -= minutes * 60;
    var seconds = Math.floor(seconds) === seconds ? Math.floor(remaining) : Math.floor(remaining * 10) / 10;

    hours = hours ? hours + ":" : "";
    minutes = (hours && minutes < 10 ? "0" + minutes : minutes) + ":";
    seconds = seconds < 10 ? "0" + seconds : seconds;
    return hours + minutes + seconds;
  };

  self.pace = function () {
    if (self.seconds && self.distance) {
        var pace = self.seconds / self.distance;
        if (self.activity === "erging") {
            // Paces for m workouts are given in km
            if (self.distance_unit === "m") {
                pace = pace * 1000;
            }
            // Paces for ergs are per 500m, not 1k
            if (self.distance_unit === "km" || self.distance_unit === "m") {
                pace = pace / 2;
            }
        }
        return self.time(pace);
    }
    return "";
  };

  return self;
}