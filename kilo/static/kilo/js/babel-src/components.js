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

    this.showCurrentDay = this.showCurrentDay.bind(this);
  }

  showCurrentDay () {
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
          <button type="button" className="pull-right btn btn-primary" id={this.state.id} onClick={this.showCurrentDay}>
            Edit
          </button>
        </td>
      </tr>
    );
  }
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activity: props.activity,
      loading: true,
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
          <div className="col-4"></div>
        </div>
      </div>
    );
  }
}