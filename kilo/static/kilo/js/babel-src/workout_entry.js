export class WorkoutEntry extends React.Component {
  constructor(props) {
    super(props);
    this.state = props;
    this.handleSetsChange = this.handleSetsChange.bind(this);
    this.handleRepsChange = this.handleRepsChange.bind(this);
    this.handleWeightChange = this.handleWeightChange.bind(this);
  }

  handleSetsChange(e) { this.setState({sets: e.target.value}) }
  handleRepsChange(e) { this.setState({reps: e.target.value}) }
  handleWeightChange(e) { this.setState({weight: e.target.value}) }

  render() {
    return (
      <div>
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