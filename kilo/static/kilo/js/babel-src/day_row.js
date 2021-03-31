export class DayRow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      year: props.day.split("-")[0],
      month: props.day.split("-")[1],
      dayOfMonth: props.day.split("-")[2],
      notes: props.notes,
      activities: props.workouts.map((workout) => <li key={workout.id}>{workout.activity}</li>),
      summaries: props.workouts.map((workout) => <li key={workout.id}>{workout.summary}</li>),
      editing: false,
    };

    this.day = this.day.bind(this);
    this.dayOfWeek = this.dayOfWeek.bind(this);
    this.monthText = this.monthText.bind(this);
    this.handleMonthChange = this.handleMonthChange.bind(this);
    this.handleDayOfMonthChange = this.handleDayOfMonthChange.bind(this);
    this.handleYearChange = this.handleYearChange.bind(this);

    this.saveDayEntry = this.saveDayEntry.bind(this);
    this.showDayEntry = this.showDayEntry.bind(this);
    this.clearDayEntry = this.clearDayEntry.bind(this);

    this.handleNotesChange = this.handleNotesChange.bind(this);
  }

  handleYearChange(e) { this.setState({year: e.target.value}) }
  handleMonthChange(e) { this.setState({month: e.target.value}) }
  handleDayOfMonthChange(e) { this.setState({dayOfMonth: e.target.value}) }
  handleNotesChange(e) { this.setState({notes: e.target.value}) }

  dayOfWeek() {
    return ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat"][(new Date(this.day())).getDay()];
  }

  monthText() {
    return ["Jan", "Feb", "March", "April", "May", "June",
            "July", "Aug", "Sept", "Oct", "Nov", "Dec"][(new Date(this.day())).getMonth()];
  }

  day() {
    return this.state.year + "-" + this.state.month + "-" + this.state.dayOfMonth;
  }

  saveDayEntry () {
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
          self.setState({editing: false});
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
        <td className="col-3">
          {this.state.editing && <div className="row g-1 align-items-center">
          <div className="col-3">
             {this.dayOfWeek()},
          </div>
          <div className="col-3">
             <label className="visually-hidden">Month</label>
             <input type="text" className="form-control" name="month"
                    value={this.state.month} onChange={this.handleMonthChange} />
          </div>
          <div className="col-3">
             <label className="visually-hidden">Day</label>
             <input type="text" className="form-control" name="day_of_month"
                    value={this.state.dayOfMonth} onChange={this.handleDayOfMonthChange} />
          </div>
          <div className="col-3">
             <label className="visually-hidden">Year</label>
             <input type="text" className="form-control" name="year"
                    value={this.state.year} onChange={this.handleYearChange} />
          </div>
          </div>}
          {!this.state.editing && <span>
            {this.dayOfWeek()}, {this.monthText()} {this.state.dayOfMonth}, {this.state.year}
          </span>}
        </td>
        <td className="col-2">
          <ul className="list-unstyled">{this.state.activities}</ul>
        </td>
        <td className="col-2">
          <ul className="list-unstyled">{this.state.summaries}</ul>
        </td>
        <td className="col-4">
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