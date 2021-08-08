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
        if (!activity && data.graph_data) {
          self.loadGraph(data.graph_data);
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

  loadGraph(data) {
    c3.generate({
        bindto: '#graph',
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
                max: this.state.activity ? undefined : 7,
                tick: {
                    count: this.state.activity ? undefined : 8,
                    format: this.state.activity ? function (seconds) {
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
            show: !this.state.activity,
        },
        point: {
            show: !!this.state.activity,
        },
        tooltip: {
            show: !!this.state.activity,
            grouped: false,
            contents: this.state.activity ? function (points) {
                var point = points[0],
                    date = new Date(point.x).toLocaleDateString();
                return "<div style='background: #fff; padding: 5px; opacity: 0.9;'>" + date + " " + getTime(point.value) + "</div>";
            } : undefined,
        },
    });
  }

  render() {
    return (
      <div>
        <Nav setActivity={this.setActivity} addDayRow={this.addDayRow} templates={this.state.templates} loading={this.state.loading} />
        <Loading show={this.state.loading} />
        <br />
        <div className="row">
          {!this.state.activity && <div class="col-5">
            <div id="graph"></div>
          </div>}
          <div className={`${this.state.activity ? "col-12" : "col-7"}`}>
            <div className="row">
              {this.state.stats}
            </div>
          </div>
        </div>
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
