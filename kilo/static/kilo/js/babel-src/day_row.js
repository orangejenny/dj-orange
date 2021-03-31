export class DayRow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      day: props.day,
      notes: props.notes,
      pretty_day: props.pretty_day,
      activities: props.workouts.map((workout) => <li key={workout.id}>{workout.activity}</li>),
      summaries: props.workouts.map((workout) => <li key={workout.id}>{workout.summary}</li>),
      editing: false,
    };

    this.saveDayEntry = this.saveDayEntry.bind(this);
    this.showDayEntry = this.showDayEntry.bind(this);
    this.clearDayEntry = this.clearDayEntry.bind(this);

    this.handleNotesChange = this.handleNotesChange.bind(this);
  }

  handleNotesChange(e) { this.setState({notes: e.target.value}) }

  saveDayEntry () {
    console.log("save day " + this.state.id);
    var self = this;
    $.ajax({
        method: 'POST',
        data: {
          csrfmiddlewaretoken: $("#csrf-token").find("input").val(),
          day: JSON.stringify(this.state),
        },
        success: function (data) {
          // TODO
          alert("done successfully");
          this.setState({editing: false});
        },
        error: function () {
          // TODO
          alert("had a problem");
        },
    });
  }

  showDayEntry () {
    this.setState({editing: true});
  }

  clearDayEntry () {
    this.setState({editing: false});
    console.log("TODO: clear attributes");
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
        <td className="col-5">
          {this.state.editing &&
          <textarea className="form-control" rows="3" name="notes" placeholder="How was today?"
                    value={this.state.notes} onChange={this.handleNotesChange} />}
          {!this.state.editing && this.state.notes}
        </td>
        <td className="col-1">
          {this.state.editing && <div>
            <button type="button" className="pull-right btn btn-primary" onClick={this.saveDayEntry}>
              Save
            </button>
            <button type="button" className="pull-right btn btn-outline-secondary" onClick={this.clearDayEntry}>
              Cancel
            </button>
          </div>}
          {!this.state.editing && <button type="button" className="pull-right btn btn-outline-secondary" onClick={this.showDayEntry}>
            Edit
          </button>}
        </td>
      </tr>
    );
  }
}