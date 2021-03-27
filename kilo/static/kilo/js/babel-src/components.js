class Loading extends React.Component {
    render() {
      if (this.props.show) {
        return (
          <div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <span className="visually-hidden">Loading...</span>
          </div>
        );
      } else {
        return null;
      }
    }
}

class Stat extends React.Component {
    render() {
        return (
          <div className="card text-center">
            <div className="card-header">{this.props.name}</div>
            <div className="card-body">
                <h1>{this.props.primary}</h1>
                {this.props.secondary}
            </div>
          </div>
        );
    }
}

class Row extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      notes: props.notes,
      pretty_day: props.pretty_day,
      activities: props.workouts.map((workout) => <li key={workout.id}>{workout.activity}</li>),
      summaries: props.workouts.map((workout) => <li key={workout.id}>{workout.summary}</li>),
    };

    this.showDayEntry = this.showDayEntry.bind(this);
  }

  showDayEntry () {
    console.log("show day " + this.state.id);
  }

  render () {
    return (
      <tr className="row">
        <td className="col-2">{this.state.pretty_day}</td>
        <td className="col-2">
          <ul className="list-unstyled">{this.state.activities}</ul>
        </td>
        <td className="col-2">
          <ul className="list-unstyled">{this.state.summaries}</ul>
        </td>
        <td className="col-5">{this.state.notes}</td>
        <td className="col-1">
          <button type="button" className="pull-right btn btn-primary" id={this.state.id} onClick={this.showDayEntry}>
            Edit
          </button>
        </td>
      </tr>
    );
  }
}

class WorkoutEntry extends React.Component {
  constructor(props) {
    super(props);
    this.state = props;
    this.pace = this.pace.bind(this);
    this.time = this.time.bind(this);
    this.handleActivityChange = this.handleActivityChange.bind(this);
    this.handleDistanceChange = this.handleDistanceChange.bind(this);
    this.handleDistanceUnitChange = this.handleDistanceUnitChange.bind(this);
    this.handleSetsChange = this.handleSetsChange.bind(this);
    this.handleRepsChange = this.handleRepsChange.bind(this);
    this.handleWeightChange = this.handleWeightChange.bind(this);
    this.handleTimeChange = this.handleTimeChange.bind(this);
    this.remove = this.remove.bind(this);
  }

  handleActivityChange(e) { this.setState({activity: e.target.value}) }
  handleDistanceChange(e) { this.setState({distance: e.target.value}) }
  handleDistanceUnitChange(e) { this.setState({distance_unit: e.target.value}) }
  handleSetsChange(e) { this.setState({sets: e.target.value}) }
  handleRepsChange(e) { this.setState({reps: e.target.value}) }
  handleWeightChange(e) { this.setState({weight: e.target.value}) }
  handleTimeChange(e) { this.setState({seconds: e.target.value}) }  // TODO: convert to time

  pace() { return "PACE"; }   // TODO
  time() { return this.state.seconds; }   // TODO: display human-friendly-time

  remove() {
    console.log("TODO: remove workout");
  }

  render() {
    return (
      <div>
        <div className="row g-1 mb-1 align-items-center">
          <div className="col-3">
            <select className="form-control form-control-sm" name="activity" value={this.state.activity} onChange={this.handleActivityChange}>
              <option>running</option>/* TODO: pull from server */
              <option>erging</option>
            </select>
          </div>
          <div className="col-2">
            <input type="text" className="form-control form-control-sm" name="distance" placeholder="distance" value={this.state.distance} onChange={this.handleDistanceChange} />
          </div>
          <div className="col-2">
            <select className="form-control form-control-sm" name="distance_unit" value={this.state.distance_unit} onChange={this.handleDistanceUnitChange}>
              <option>mi</option>/* TODO: pull from server */
              <option>km</option>
              <option>m</option>
            </select>
          </div>
          <div className="col-2">
            <input type="text" className="form-control form-control-sm" placeholder="time" value={this.time()} onChange={this.handleTimeChange} />
          </div>
          <div className="col-2">{this.pace()}</div>
          <div className="col-1">
            <button type="button" class="btn btn-outline-secondary btn-sm" onClick={this.remove}>
              <i className="fa fa-times"></i>
            </button>
          </div>
        </div>
        {this.state.activity === "lifting" && <div className="row g-1 mb-1" data-bind="visible: isLifting">
          <div className="col-3"></div>
          <div className="col-2">
            <input type="text" className="form-control form-control-sm" name="sets" placeholder="sets" value={this.state.sets} onChange={this.handleSetsChange} />
          </div>
          <div className="col-2">
            <input type="text" className="form-control form-control-sm" name="reps" placeholder="reps" value={this.state.reps} onChange={this.handleRepsChange} />
          </div>
          <div className="col-2">
            <input type="text" className="form-control form-control-sm" name="weight" placeholder="weight"  value={this.state.weight} onChange={this.handleWeightChange} />
          </div>
        </div>}
      </div>
    );
  }
}

class DayEntry extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      year: props.day.split("-")[0],
      month: props.day.split("-")[1],
      dayOfMonth: props.day.split("-")[2],
      workouts: props.workouts,
    };
    this.day = this.day.bind(this);
    this.dayOfWeek = this.dayOfWeek.bind(this);
    this.handleMonthChange = this.handleMonthChange.bind(this);
    this.handleDayOfMonthChange = this.handleDayOfMonthChange.bind(this);
    this.handleYearChange = this.handleYearChange.bind(this);
    this.handleNotesChange = this.handleNotesChange.bind(this);
    this.addWorkout = this.addWorkout.bind(this);
    this.clearDayEntry = this.clearDayEntry.bind(this);
    this.saveDayEntry = this.saveDayEntry.bind(this);
  }

  addWorkout() {
    console.log("TODO addWorkout");
  }

  clearDayEntry() {
    console.log("TODO clearDayEntry");
  }

  saveDayEntry(e) {
    console.log("TODO saveDayEntry");
    e.preventDefault();
  }

  handleYearChange(e) { this.setState({year: e.target.value}) }
  handleMonthChange(e) { this.setState({month: e.target.value}) }
  handleDayOfMonthChange(e) { this.setState({dayOfMonth: e.target.value}) }
  handleNotesChange(e) { this.setState({notes: e.target.value}) }

  dayOfWeek() {
    return ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][(new Date(this.day())).getDay()];
  }

  day() {
    return this.state.year + "-" + this.state.month + "-" + this.state.dayOfMonth;
  }

  render() {
    const workouts = this.state.workouts.map((w) => <WorkoutEntry {...w} />)
    return (
        <form onSubmit={this.saveDayEntry}>
          <div className="card">
            <div className="card-header">
              <input type="hidden" name="day_id" value={this.state.id} />
              <div className="row g-1 align-items-center">
                <div className="col-3">{this.dayOfWeek()}</div>
                <div className="col-2">
                  <label className="visually-hidden" for="currentDayMonth">Month</label>
                  <input type="text" className="form-control" id="currentDayMonth" name="month" value={this.state.month} onChange={this.handleMonthChange} />
                </div>
                <div className="col-2">
                  <label className="visually-hidden" for="currentDayDay">Day</label>
                  <input type="text" className="form-control" id="currentDayDay" name="day_of_month" value={this.state.dayOfMonth} onChange={this.handleDayOfMonthChange} />
                </div>
                <div className="col-3">
                  <label className="visually-hidden" for="currentDayYear">Year</label>
                  <input type="text" className="form-control" id="currentDayYear" name="year" value={this.state.year} onChange={this.handleYearChange} />
                </div>
                <div className="col-1"></div>
                <div className="col-1">
                  <button type="button" className="btn btn-outline-secondary btn-sm" onClick={this.addWorkout}>
                    <i className="fa fa-plus"></i>
                  </button>
                </div>
              </div>
            </div>
            <div className="card-body">
              {workouts}
              <textarea className="form-control" name="notes" placeholder="How was today?" value={this.state.notes} onChange={this.handleNotesChange} rows="3" />
            </div>
            <div className="card-footer">
              <button type="submit" className="btn btn-primary">Save</button>
              &nbsp;
              <button type="button" className="btn btn-secondary" onClick={this.clearDayEntry}>Cancel</button>
            </div>
          </div>
        </form>
    );
  }
}

class App extends React.Component {
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
                  <Row key={day.id} {...day} />
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