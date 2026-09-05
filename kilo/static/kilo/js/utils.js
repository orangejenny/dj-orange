function getFrequencyGraphOptions() {
    return getGraphOptions();
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

function loadPaceChart(url) {
    fetch(url)
        .then(response => response.json())
        .then(options => {
            if (options?.axis?.y?.tick) {
                options.axis.y.tick.format = getTime;
            }
            document.getElementById('chart').innerHTML = '';
            c3.generate(options);
        });
}

function clearChart() {
    document.getElementById('chart').innerHTML = '';
}

function hideRecent() {
    document.getElementById('recent').style.display = 'none';
}

function showRecent() {
    document.getElementById('recent').style.display = '';
}

function initDropdowns(event) {
    const dropdowns = event.detail.elt.querySelectorAll("select");
    dropdowns.forEach(function (d) {
        new Choices(d, {
            itemSelectText: "",
            addChoices: d.dataset.addChoices,
        })
        if (d.name === "activity" ) {
            d.addEventListener(
                'choice',
                function(event) {
                    const el = event.detail.element;
                    let container = el;
                    do {
                        container = container.parentElement;
                    } while (
                        container
                        && container.nodeName.toLowerCase() != "li"
                        && container.nodeName.toLowerCase() != "body"
                    )

                    const setLastValue = function (name, value) {
                        const input = container.querySelector("input[name='" + name + "']");
                        if (input) {
                            input.value = value;
                        }
                    };

                    if (el.dataset.lastSets) {
                        setLastValue("sets", el.dataset.lastSets)
                    }
                    if (el.dataset.lastReps) {
                        setLastValue("reps", el.dataset.lastReps)
                    }
                    if (el.dataset.lastWeight) {
                        setLastValue("weight", el.dataset.lastWeight)
                    }
                },
                false,
            );
        }
    });
}

function navigateVisual(page, url, year) {
    if (page === "erging" || page === "running") {
        let url = document.getElementById('pace-url').innerHTML;
        loadPaceChart(url + '?activity=' + page + '&year=' + year);
    } else {
        clearChart();
    }
    hideRecent();
}
