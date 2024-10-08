import { DayRecord } from "./day_record.js";
import { Loading } from "./loading.js";
import { Nav } from "./nav.js";
import { Stat } from "./stat.js";
import { Workout } from "../workout.js";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      panel: "frequency",
      loading: true,
      records: [],
    };

    this.setPanel = this.setPanel.bind(this);
    this.getPanel = this.getPanel.bind(this);
  }

  setPanel(e) {
    var panel = "frequency";
    if (e) {
      panel = e.target.dataset.panel;
    }
    this.getPanel(panel);
  }

  componentDidMount() {
    this.setPanel();
  }

  getPanel(panel) {
      var self = this;
      self.setState({
        loading: true,
        panel: panel,
      });
      fetch("/kilo/" + (panel || ""), {
        method: "GET",
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => resp.json()).then(data => {
        // Forcibly clear records so that blank recent days, which don't have keys, get removed
        self.setState({
            records: [],
        });

        var newState = {
            loading: false,
            panel: panel,
            records: data.recent_days || [],
            stats: data.stats || [],
            templates: self.getTemplates(data.recent_days || []),
        };
        if (data.all_activities) {
            newState.all_activities = data.all_activities;
        }
        if (data.all_distance_units) {
            newState.all_distance_units = data.all_distance_units;
        }
        self.setState(newState);
        if (panel === "frequency") {
            self.loadFrequencyGraph(data);
        }
        if (panel === "pace") {
            self.loadPaceGraph(data);
        }
      });
  }

  getTime(seconds) {
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

  getTemplates(days) {
     var index = 0,
         templates = [];
     while (index < days.length && templates.length < 11) {
         var indexDay = days[index];
         index++;
         if (!indexDay.workouts.length) {
             continue;
         }
         var template = { ...indexDay.workouts[0] };
         if (!templates.find(t => t.activity === template.activity && t.distance === template.distance)) {
             delete template.id;
             delete template.seconds;
             templates.push(template);
         }
     }
     return templates;
  }

  loadFrequencyGraph(data) {
    let self = this,
        options = self.graphOptions(data);

    options.tooltip = {
        show: false,
        grouped: false,
    };
    options.legend = { show: true };
    options.point = { show: false };
    options.axis.y.max = 7;
    options.axis.y.tick = { count: 8 };

    c3.generate(options);
  }

  loadPaceGraph(data) {
    let self = this,
        options = self.graphOptions(data);

    options.tooltip = {
        show: true,
        grouped: false,
    };
    options.legend = { show: false };
    options.point = { show: true };
    options.axis.y.min = 0 * 60;
    options.axis.y.max = 11 * 60;
    options.axis.y.tick = {
        outer: false,
        format: self.getTime,
        values: [7, 8, 9, 10].map(x => x * 60),
    };
    options.axis.y2 = {
        show: true,
        min: 1.75 * 60,
        max: 2.5 * 60,
        tick: {
            outer: false,
            format: self.getTime,
            values: [105, 110, 115, 120, 125, 130, 135],
        },
    };

    c3.generate(options);
  }

  graphOptions(data) {
    return {
        bindto: "#graph",
        data: data,
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    count: data.columns[0].length,
                    fit: true,
                    format: '%b %d',
                    rotate: 90,
                },
            },
            y: {
                min: 0,
                padding: {
                    top: 0,
                    bottom: 0,
                },
            },
        },
    };
  }

  render() {
    return (
      <div>
        <Nav setPanel={this.setPanel} loading={this.state.loading} panel={this.state.panel} />
        <Loading show={this.state.loading} />
        <br />
        {(this.state.panel === "frequency" || this.state.panel === "pace") && <div id="graph"></div>}
        {this.state.panel === "stats" && <div className="row">{this.state.stats.map((stat_set) =>
          <div className="col" key={stat_set.title}>
            <Stat title={stat_set.title} stats={stat_set.stats} />
          </div>
        )}</div>}
        {(this.state.panel === "recent" || this.state.panel === "history") && <table class="table table-striped">
          <tbody>
            {this.state.records.map((day) =>
              <DayRecord key={day.id} {...day} panel={this.state.panel} templates={this.state.templates}
                         all_activities={this.state.all_activities} all_distance_units={this.state.all_distance_units} />
            )}
          </tbody>
        </table>}
      </div>
    );
  }
}

window.addEventListener('DOMContentLoaded', (event) => {
  ReactDOM.render(React.createElement(App), document.getElementById("app"));
});
