import { DayRecord } from "./day_record.js";
import { Loading } from "./loading.js";
import { Nav } from "./nav.js";
import { Stat } from "./stat.js";
import { Workout } from "../workout.js";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isRecent: true,
      loading: true,
      records: [],
      templates: [],
    };

    this.addDayRecord = this.addDayRecord.bind(this);
    this.setIsRecent = this.setIsRecent.bind(this);
    this.getPanel = this.getPanel.bind(this);
  }

  addDayRecord(template) {
    var self = this,
      day = new Date();
    day = [
      day.getFullYear(),
      (day.getMonth() < 9 ? "0" : "") + (day.getMonth() + 1),
      (day.getDate() < 10 ? "0" : "") + day.getDate(),
    ].join("-");
    this.setState((state, props) => {
      var id = state.records.reduce((accumulator, row) => ( Math.min(accumulator, row.props.id) ), 0) - 1,
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
        records: [<DayRecord { ...options } />, ...this.state.records],
      };
    });
  }

  setIsRecent(e) {
    var isRecent = true;
    if (e) {
      isRecent = !!Number(e.target.dataset.isRecent);
    }
    this.getPanel(isRecent);
  }

  componentDidMount() {
    this.setIsRecent();
  }

  getPanel(isRecent) {
      var self = this;
      self.setState({
        loading: true,
        isRecent: isRecent,
      });
      fetch("/kilo/panel?is_recent=" + (isRecent || ""), {
        method: "GET",
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => resp.json()).then(data => {
        self.setState({
          all_activities: data.all_activities,
          all_distance_units: data.all_distance_units,
          loading: false,
          records: data.recent_days.map((day) =>
            <DayRecord key={day.id} {...day} isRecent={isRecent}
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
    // TODO: bring back .table and .table-hover styles for historical records
    return (
      <div>
        <Nav setIsRecent={this.setIsRecent} addDayRecord={this.addDayRecord} templates={this.state.templates} loading={this.state.loading} />
        <Loading show={this.state.loading} />
        <br />
        {this.state.isRecent && <div className="row">
          <div class="col-6"><div id="frequency-graph"></div></div>
          <div class="col-6"><div id="pace-graph"></div></div>
        </div>}
        {!this.state.isRecent && <div class="col-12">
          <div className="row">{this.state.stats}</div>
        </div>}
        <br /><br />
        <div>{this.state.records}</div>
      </div>
    );
  }
}

window.addEventListener('DOMContentLoaded', (event) => {
  ReactDOM.render(React.createElement(App), document.getElementById("app"));
});
