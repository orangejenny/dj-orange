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

  return self;
}
