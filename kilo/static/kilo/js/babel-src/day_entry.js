import { WorkoutEntry } from "./workout_entry.js";

export class DayEntry extends React.Component {
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