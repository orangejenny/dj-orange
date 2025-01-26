import { DayRecord } from "./day_record.js";
import { Loading } from "./loading.js";
import { Nav } from "./nav.js";
import { Stat } from "./stat.js";
import { Workout } from "../workout.js";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      panel: "recent",
      loading: true,
      records: [],
    };

    this.setPanel = this.setPanel.bind(this);
    this.getPanel = this.getPanel.bind(this);
  }

  setPanel(e) {
    var panel = "recent";
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
            templates: self.getTemplates(data.recent_days || []),
        };
        if (data.all_activities) {
            newState.all_activities = data.all_activities;
        }
        if (data.all_distance_units) {
            newState.all_distance_units = data.all_distance_units;
        }
        self.setState(newState);
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

  render() {
    return (
      <div>
        <Nav setPanel={this.setPanel} loading={this.state.loading} panel={this.state.panel} />
        <Loading show={this.state.loading} />
        <br />
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
