export class WorkoutEntry extends React.Component {
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