class Loading extends React.Component {
    render() {
        return (
          <div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <span className="visually-hidden">Loading...</span>
          </div>
        );
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