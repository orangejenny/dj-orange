import { DayRow } from "./day_row.js";
import { Loading } from "./loading.js";
import { Nav } from "./nav.js";
import { Stat } from "./stat.js";
import { Workout } from "../workout.js";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activity: null,
      loading: true,
      rows: [],
      templates: [],
    };

    this.addDayRow = this.addDayRow.bind(this);
    this.setActivity = this.setActivity.bind(this);
    this.getPanel = this.getPanel.bind(this);
  }

  addDayRow(template) {
    var self = this,
      day = new Date();
    day = [
      day.getFullYear(),
      (day.getMonth() < 9 ? "0" : "") + (day.getMonth() + 1),
      (day.getDate() < 10 ? "0" : "") + day.getDate(),
    ].join("-");
    this.setState((state, props) => {
      var id = state.rows.reduce((accumulator, row) => ( Math.min(accumulator, row.props.id) ), 0) - 1,
        options = {
          key: id,
          id: id,
          day: day,
          workouts: template ? [Workout(template)] : [],
          editing: true,
          all_activities: self.state.all_activities,
          all_distance_units: self.state.all_distance_units,
        };
      return {
        rows: [<DayRow { ...options } />, ...this.state.rows],
      };
    });
  }

  setActivity(e) {
    var activity = null;
    if (e) {
      activity = e.target.dataset.activity;
    }
    this.getPanel(activity);
  }

  componentDidMount() {
    this.setActivity();
  }

  getPanel(activity) {
      var self = this;
      self.setState({
        loading: true,
        activity: activity,
      });
      fetch("/kilo/panel?activity=" + (activity || ""), {
        method: "GET",
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => resp.json()).then(data => {
        self.setState({
          all_activities: data.all_activities,
          all_distance_units: data.all_distance_units,
          loading: false,
          rows: data.recent_days.map((day) =>
            <DayRow key={day.id} {...day}
                    all_activities={data.all_activities} all_distance_units={data.all_distance_units} />
          ),
          stats: data.stats.map((stat) => 
            <div className="col" key={stat.name}>
              <Stat name={stat.name} primary={stat.primary} secondary={stat.secondary} />
            </div>
          ),
          templates: self.getTemplates(data.recent_days),
        });
        if (data.frequency_graph_data) {
            self.loadFrequencyGraph(data.frequency_graph_data);
        }
        if (data.pace_graph_data) {
            self.loadPaceGraph(data.pace_graph_data);
        }
      }).catch((error) => {
        alert('Unexpected error:', error);
      });
  }

  getTemplates(days) {
    var index = 0,
        templates = [];
    while (index < days.length && templates.length < 8) {
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

  loadFrequencyGraph(data) {
    let self = this,
        options = self.graphOptions(data);

    options.bindto = "#frequency-graph";
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

  // TODO: make graph legible
  loadPaceGraph(data) {
    let self = this,
        options = self.graphOptions(data);

    options.bindto = "#pace-graph";
    options.tooltip = {
        show: true,
        grouped: false,
    };
    options.legend = { show: false };
    options.point = { show: true };
    options.axis.y.tick = {
        format: self.getTime,
    };
    options.axis.y2 = {
        show: true,
        tick: {
            format: self.getTime,
        },
    };

    c3.generate(options);
  }

  graphOptions(data) {
    return {
        data: data,
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    count: data.columns[0].length,
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
        <Nav setActivity={this.setActivity} addDayRow={this.addDayRow} templates={this.state.templates} loading={this.state.loading} />
        <Loading show={this.state.loading} />
        <br />
        {!this.state.activity && <div className="row">
          <div class="col-6"><div id="frequency-graph"></div></div>
          <div class="col-6"><div id="pace-graph"></div></div>
        </div>}
        {this.state.activity && <div class="col-12">
          <div className="row">{this.state.stats}</div>
        </div>}
        <br /><br />
        <table className="table table-hover">
          <tbody>{this.state.rows}</tbody>
        </table>
      </div>
    );
  }
}

window.addEventListener('DOMContentLoaded', (event) => {
  ReactDOM.render(React.createElement(App), document.getElementById("app"));
});
