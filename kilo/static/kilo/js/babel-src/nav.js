export class Nav extends React.Component {
    constructor (props) {
        super(props);
        this.state = { ...props };
    }

    render() {
        return (
          <nav className="navbar navbar-expand-lg navbar-light bg-light d-flex">
            <ul className="navbar-nav flex-grow-1">
              <li className="nav-item">
                <a className={`navbar-brand nav-link ${!this.state.activity ? 'active' : ''}`} href="#"
                   onClick={this.props.setActivity}>
                  Kilo
                </a>
              </li>
              <li className="nav-item">
                <a className={`nav-link ${this.state.activity === "running" ? 'active' : ''}`} href="#"
                   data-activity="running" onClick={this.props.setActivity}>
                  Running
                </a>
              </li>
              <li className="nav-item">
                <a className={`nav-link ${this.state.activity === "erging" ? 'active' : ''}`} href="#"
                   data-activity="erging" onClick={this.props.setActivity}>
                  Erging
                </a>
              </li>
            </ul>
            <div className="me-2">
              <div className="dropdown dropstart">
                <button className="btn btn-outline-secondary dropdown-toggle" id="add-workout-dropdown-btn" type="button"
                        data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  Add
                </button>
                <ul class="dropdown-menu" aria-labelledby="add-workout-dropdown-btn">
                  {this.props.templates.map((template, index) => (<li key={index}>
                    <a className="dropdown-item" onClick={() => this.props.addDayRow(JSON.stringify(template))}>
                      {template.activity} {template.distance} {template.distance_unit}
                    </a>
                  </li>))}
                  <div role="separator" className="dropdown-divider"></div>
                  <li>
                    <a class="dropdown-item" href="#" onClick={this.props.addDayRow}>Blank Day</a>
                  </li>
                </ul>
              </div>
            </div>
          </nav>
        );
    }
}