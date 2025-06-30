function getFrequencyGraphOptions() {
    return getGraphOptions();
}

function getPaceGraphOptions() {
    let options = getGraphOptions();
    if (options?.axis?.y?.tick) {
        options.axis.y.tick.format = getTime;
    }
    if (options?.axis?.y2?.tick) {
        options.axis.y2.tick.format = getTime;
    }
    return options;
}

function getGraphOptions() {
    return JSON.parse(document.getElementById('graph-options').innerHTML);
}

function getTime(seconds) {
  let hours = 0;
  if (seconds > 3600) {
      hours = Math.floor(seconds / 3600);
      seconds = seconds - hours * 3600;
  }

  let minutes = Math.floor(seconds / 60);
      seconds = seconds % 60;

  if (Math.floor(seconds * 10) !== seconds * 10) {
      // Account for floating point math that screws up rounding
      seconds = Math.floor(seconds * 10) / 10;
  }

  if (hours && minutes < 10) {
      minutes = "0" + minutes;
  }
  if (seconds < 10) {
      seconds = "0" + seconds;
  }

  if (hours) {
      return [hours, minutes, seconds].join(":")
  }
  return [minutes, seconds].join(":");
}

function initDropdowns(event) {
    const dropdowns = event.detail.elt.querySelectorAll("select");
    dropdowns.forEach(d => new Choices(d, {
        itemSelectText: "",
    }));
}
