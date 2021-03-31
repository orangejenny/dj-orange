import { WorkoutEntry } from "./workout_entry.js";

export class DayEntry extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      workouts: props.workouts,
    };
    this.addWorkout = this.addWorkout.bind(this);
  }

  addWorkout() {
    console.log("TODO addWorkout");
  }

  render() {
    const workouts = this.state.workouts.map((w) => <WorkoutEntry {...w} />)
    return (
          <div className="card">
            <div className="card-body">
                  <button type="button" className="btn btn-outline-secondary btn-sm" onClick={this.addWorkout}>
                    <i className="fa fa-plus"></i> Add Workout
                  </button>
              {workouts}
            </div>
          </div>
    );
  }
}