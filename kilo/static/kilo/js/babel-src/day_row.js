import { Workout } from "../workout.js";

export class DayRow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      year: props.day.split("-")[0],
      month: props.day.split("-")[1],
      dayOfMonth: props.day.split("-")[2],
      notes: props.notes,
      editing: false,
      workouts: props.workouts.map((w) => Workout(w)),
    };

    this.day = this.day.bind(this);
    this.dayOfWeek = this.dayOfWeek.bind(this);
    this.monthText = this.monthText.bind(this);
    this.handleMonthChange = this.handleMonthChange.bind(this);
    this.handleDayOfMonthChange = this.handleDayOfMonthChange.bind(this);
    this.handleYearChange = this.handleYearChange.bind(this);

    this.handleWorkoutChange = this.handleWorkoutChange.bind(this);
    this.handleActivityChange = this.handleActivityChange.bind(this);
    this.handleDistanceChange = this.handleDistanceChange.bind(this);
    this.handleDistanceUnitChange = this.handleDistanceUnitChange.bind(this);
    this.handleTimeChange = this.handleTimeChange.bind(this);
    this.handleSetsChange = this.handleSetsChange.bind(this);
    this.handleRepsChange = this.handleRepsChange.bind(this);
    this.handleWeightChange = this.handleWeightChange.bind(this);
    this.addWorkout = this.addWorkout.bind(this);
    this.removeWorkout = this.removeWorkout.bind(this);

    this.saveDayEntry = this.saveDayEntry.bind(this);
    this.showDayEntry = this.showDayEntry.bind(this);
    this.clearDayEntry = this.clearDayEntry.bind(this);

    this.handleNotesChange = this.handleNotesChange.bind(this);
  }

  handleYearChange(e) { this.setState({year: e.target.value}) }
  handleMonthChange(e) { this.setState({month: e.target.value}) }
  handleDayOfMonthChange(e) { this.setState({dayOfMonth: e.target.value}) }
  handleNotesChange(e) { this.setState({notes: e.target.value}) }

  getSeconds(time) {
    if (!time) {
        return undefined;
    }

    var parts = time.split(":"),
        seconds = 0,
        index = 0;
    while (index < parts.length) {
        seconds += parts[index] * Math.pow(60, parts.length - index - 1);
        index++;
    }

    return seconds;
  }

  getWorkoutId(el) {
    var value = el.dataset.id;
    while (!value && el.parentElement) {
      el = el.parentElement;
      value = el.dataset.id;
    }
    return value ? parseInt(value) : value;
  }

  handleWorkoutChange(attr, id, value) {
    this.setState(function (state, props) {
      return {
        workouts: state.workouts.map(function (w) {
          if (w.id === id) {
            w[attr] = value;
          }
          return w;
        }),
      }
    });
  }
  handleActivityChange(e) { this.handleWorkoutChange("activity", this.getWorkoutId(e.target), e.target.value); }
  handleDistanceChange(e) { this.handleWorkoutChange("distance", this.getWorkoutId(e.target), e.target.value); }
  handleDistanceUnitChange(e) { this.handleWorkoutChange("distance_unit", this.getWorkoutId(e.target), e.target.value); }
  handleTimeChange(e) {
    var value = this.getSeconds(e.target.value);
    this.handleWorkoutChange("seconds", this.getWorkoutId(e.target), value);
  }
  handleSetsChange(e) { this.handleWorkoutChange("sets", this.getWorkoutId(e.target), e.target.value); }
  handleRepsChange(e) { this.handleWorkoutChange("reps", this.getWorkoutId(e.target), e.target.value); }
  handleWeightChange(e) { this.handleWorkoutChange("weight", this.getWorkoutId(e.target), e.target.value); }

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

  addWorkout() {
    console.log("TODO: add workout");
  }

  removeWorkout() {
    console.log("TODO: remove workout");
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
        <td className="col-4">
          <ul className="list-unstyled">
            {this.state.workouts.map((workout) => <li key={workout.id} data-id={workout.id}>
               {!this.state.editing && <span>
                 {workout.activity} {workout.summary()}
               </span>}
               {this.state.editing && <div className="row g-1 mb-1 align-items-center">
                 <div className="col-3">
                   <select className="form-control" name="activity" value={workout.activity} onChange={this.handleActivityChange}>
                     <option>running</option>/* TODO: pull from server */
                     <option>erging</option>
                     <option>lifting</option>
                   </select>
                 </div>
                 <div className="col-2">
                   <input type="text" className="form-control" name="distance" placeholder="distance" value={workout.distance} onChange={this.handleDistanceChange} />
                 </div>
                 <div className="col-2">
                   <select className="form-control" name="distance_unit" value={workout.distance_unit} onChange={this.handleDistanceUnitChange}>
                     <option>mi</option>/* TODO: pull from server */
                     <option>km</option>
                     <option>m</option>
                   </select>
                 </div>
                 <div className="col-2">
                   <input type="text" className="form-control" placeholder="time" value={workout.time()} onChange={this.handleTimeChange} />
                 </div>
                 <div className="col-2">{workout.pace()}</div>
                 <div className="col-1">
                   <button type="button" class="btn btn-outline-secondary btn-sm" onClick={this.removeWorkout}>
                     <i className="fa fa-times"></i>
                   </button>
                 </div>
               </div>}
              {this.state.editing && workout.activity === "lifting" && <div className="row g-1 mb-1">
                  <div className="col-3"></div>
                  <div className="col-2">
                    <input type="text" className="form-control" name="sets" placeholder="sets"
                           value={workout.sets} onChange={this.handleSetsChange} />
                  </div>
                  <div className="col-2">
                    <input type="text" className="form-control" name="reps" placeholder="reps"
                           value={workout.reps} onChange={this.handleRepsChange} />
                  </div>
                  <div className="col-2">
                    <input type="text" className="form-control" name="weight" placeholder="weight"
                           value={workout.weight} onChange={this.handleWeightChange} />
                  </div>
               </div>}
               {this.state.editing && <button type="button" className="btn btn-outline-secondary btn-sm" onClick={this.addWorkout}>
                 <i className="fa fa-plus"></i> Add Workout
               </button>}
             </li>)}
          </ul>
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