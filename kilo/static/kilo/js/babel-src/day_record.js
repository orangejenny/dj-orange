import { Workout } from "../workout.js";

export class DayRecord extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      isRecent: props.isRecent,
      year: props.day.split("-")[0],
      month: props.day.split("-")[1],
      dayOfMonth: props.day.split("-")[2],
      notes: props.notes,
      editing: props.editing || false,
      saving: false,
      workouts: props.workouts.map((w) => Workout(w)),
    };

    this.day = this.day.bind(this);
    this.dayOfWeek = this.dayOfWeek.bind(this);
    this.monthText = this.monthText.bind(this);

    this.activityIcon = this.activityIcon.bind(this);
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
    this.editDayEntry = this.editDayEntry.bind(this);
    this.editExistingDayEntry = this.editExistingDayEntry.bind(this);
    this.clearDayEntry = this.clearDayEntry.bind(this);

    this.handleNotesChange = this.handleNotesChange.bind(this);
  }

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

  activityIcon(workout) {
    let activity = {
        "erging": "fas fa-gears",
        "sculling": "fas fa-water",
        "running": "fas fa-running",
        "stairs": "fas fa-stairs",
        "circuits": "fas fa-heart-pulse",
        "crossfit": "fas fa-child-reaching",
        "biking": "fas fa-person-biking",
        "swimming": "fas fa-person-swimming",
        "lifting": "fas fa-dumbbell",
        "cleans": "fas fa-dumbbell",
        "overhead press": "fas fa-dumbbell",
        "bench press": "fas fa-dumbbell",
        "barbell rows": "fas fa-dumbbell",
    }[workout.activity];

    if (activity) {
        return activity;
    }

    if (workout.reps && workout.weight) {
        return "fas fa-dumbbell";
    }

    return "fas fa-circle-question";
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
    return ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat"][(new Date(this.day() + "T00:00:00")).getDay()];
  }

  monthText() {
    return ["Jan", "Feb", "March", "April", "May", "June",
            "July", "Aug", "Sept", "Oct", "Nov", "Dec"][(new Date(this.day() + "T00:00:00")).getMonth()];
  }

  day() {
    return this.state.year + "-" + this.state.month + "-" + this.state.dayOfMonth;
  }

  addWorkout() {
    this.setState(function (state, props) {
      var options = {};
      if (state.workouts.length) {
        options = { ...state.workouts[state.workouts.length - 1] };
        delete options.id;
        delete options.seconds;
        options.id = state.workouts.reduce((accumulator, workout) => ( Math.min(accumulator, workout.id) ), 0);
        options.id -= 1;
      } else {
        options.id = -1;
      }
      return {
        workouts: [ ...state.workouts, Workout(options) ],
      }
    });
  }

  removeWorkout(e) {
    var id = this.getWorkoutId(e.target);
    this.setState(function (state, props) {
      return {
        workouts: state.workouts.filter((w) => (w.id !== id)),
      }
    });
  }

  saveDayEntry () {
    var self = this;
    self.setState({saving: true});
    fetch("", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector("#csrf-token input").value,
      },
      body: JSON.stringify({
        day: this.state,
      }),
    }).then((resp) => resp.json()).then(data => {
      if  (data.success) {
        self.setState(function (state, props) {
          var newState = {
            ...data.day,
            editing: false,
          };
          newState.workouts = newState.workouts.map((w) => Workout(w));
          return newState;
        });
      } else if (data.error) {
        alert("Error: " + data.error);
      } else {
        alert("Unexpected error");
      }
      self.setState({saving: false});
    }).catch((error) => {
      self.setState({saving: false});
      alert('Unexpected error:', error);
    });
  }

  editExistingDayEntry () {
    return this.editDayEntry();
  }

  editDayEntry (template) {
    this.setState(function (state, props) {
      let newState = {
        originalDay: {
          day: [state.year, state.month, state.dayOfMonth].join("-"),
          notes: state.notes,
          workouts: state.workouts.map((w) => ( { ...w } )),
        },
        editing: true,
      };
      if (template) {
        newState.workouts = [Workout(template)];
      }
      return newState;
    });
  }

  clearDayEntry () {
    this.setState(function (state, props) {
      if (state.id < 0) {
        return {
          invisible: true,
        }
      }
      return {
        day: state.originalDay.day,
        notes: state.originalDay.notes,
        workouts: state.originalDay.workouts.map((w) => ( Workout(w) )),
        editing: false,
      };
    });
  }

  render () {
    if (this.state.invisible) {
      return null;
    }

    return (
      <tr className="row">
        <td className="col-2">
          {this.dayOfWeek()}, {this.monthText()} {this.state.dayOfMonth}, {this.state.year}
          <input type="hidden" name="year" value={this.state.year} />
          <input type="hidden" name="month" value={this.state.month} />
          <input type="hidden" name="day_of_month" value={this.state.dayOfMonth} />
        </td>
        <td className="col-4">
          <ul className="list-unstyled">
            {this.state.workouts.map((workout) => <li key={workout.id} data-id={workout.id}>
               {!this.state.editing && <span>
                 {this.activityIcon(workout) && <i class={this.activityIcon(workout)}></i>}
                 &nbsp;
                 {workout.activity} {workout.summary()}
               </span>}
               {this.state.editing && <div className="row g-1 mb-1 align-items-center">
                 <div className="col-3">
                   <select className="form-control" name="activity" value={workout.activity} onChange={this.handleActivityChange}>
                     {this.props.all_activities.map((a) => (
                      <option key={a}>{a}</option>
                     ))}
                   </select>
                 </div>
                 <div className="col-2">
                   <input type="text" className="form-control" name="distance" placeholder="distance" value={workout.distance} onChange={this.handleDistanceChange} />
                 </div>
                 <div className="col-2">
                   <select className="form-control" name="distance_unit" value={workout.distance_unit} onChange={this.handleDistanceUnitChange}>
                     {this.props.all_distance_units.map((u) => (
                      <option key={u}>{u}</option>
                     ))}
                   </select>
                 </div>
                 <div className="col-2">
                   <input type="text" className="form-control" placeholder="time" value={workout.time()} onChange={this.handleTimeChange} />
                 </div>
                 <div className="col-1">
                   <button type="button" class="btn btn-outline-secondary btn-sm" onClick={this.removeWorkout}>
                     <i className="fa fa-times"></i>
                   </button>
                 </div>
                 <div className="col-2">{workout.pace()}</div>
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
             </li>)}
             {this.state.editing && <button type="button" className="btn btn-outline-secondary btn-sm" onClick={this.addWorkout}>
               <i className="fa fa-plus"></i> Add Workout
             </button>}
          </ul>
        </td>
        <td className="col-5">
          {this.state.editing &&
          <textarea className="form-control" rows="3" name="notes" placeholder="How was today?"
                    value={this.state.notes} onChange={this.handleNotesChange} />}
          {!this.state.editing && this.state.notes}
        </td>
        <td className="col-1">
          {this.state.editing && <div className="btn-group" role="group">
            <button type="button" className="float-end btn btn-outline-success" onClick={this.saveDayEntry}>
              <i className={`fa ${this.state.saving ? "fa-spin fa-spinner" : "fa-check"}`}></i>
            </button>
            <button type="button" className="float-end btn btn-outline-danger" onClick={this.clearDayEntry}>
              <i className="fa fa-times"></i>
            </button>
          </div>}
          {!this.state.editing && !this.state.id && <div className="me-2">
             <div className="dropdown dropstart">
               <button className="btn btn-outline-secondary dropdown-toggle" id="add-workout-dropdown-btn" type="button"
                       data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                 Add
               </button>
               <ul class="dropdown-menu" aria-labelledby="add-workout-dropdown-btn">
                 {this.props.templates.map((template, index) => (<li key={index}>
                   <a className="dropdown-item" onClick={() => this.editDayEntry(template)}>
                     {template.activity} {template.distance} {template.distance_unit}
                   </a>
                 </li>))}
                 {!!this.props.templates.length && <div role="separator" className="dropdown-divider"></div>}
                 <li>
                   <a class="dropdown-item" href="#" onClick={this.editExistingDayEntry}>Blank Day</a>
                 </li>
               </ul>
             </div>
           </div>}
          {!this.state.editing && this.state.id && <button type="button" className="float-end btn btn-outline-secondary" onClick={this.editExistingDayEntry}>
            Edit
          </button>}
        </td>
      </tr>
    );
  }
}
