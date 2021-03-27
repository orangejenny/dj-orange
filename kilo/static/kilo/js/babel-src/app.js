import { DayEntry } from "./day_entry.js";
import { DayRow } from "./day_row.js";
import { Loading } from "./loading.js";
import { Stat } from "./stat.js";

export class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activity: props.activity,
      loading: true,
      current_day: {
        day: "2021-03-25",
        workouts: [
          {activity: "erging", distance: 6, distance_unit: "km", seconds: 24 * 60 + 53},
        ],
      },
    };
  }

  componentDidMount() {
    var self = this;
      $.ajax({
          url: '/kilo/panel',
          method: 'GET',
          data: {
              activity: this.state.activity,
          },
          success: function (data) {
              self.setState({
                loading: false,
                rows: data.recent_days.map((day) =>
                  <DayRow key={day.id} {...day} />
                ),
                stats: data.stats.map((stat) => 
                  <div className="col" key={stat.name}>
                    <Stat name={stat.name} primary={stat.primary} secondary={stat.secondary} />
                  </div>
                ),
              });
              if (data.graph_data) {
                self.loadGraph(data.graph_data);
              }
          },
      });
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
        <Loading show={this.state.loading} />
        <div className="row">{this.state.stats}</div>
        <br /><br />
        <div className="row">
          <div className="col-8">
            <table className="table table-hover">
              <tbody>{this.state.rows}</tbody>
            </table>
          </div>
          <div className="col-4">
            <DayEntry {...this.state.current_day} />
            <div id="graph"></div>
          </div>
        </div>
      </div>
    );
  }
}