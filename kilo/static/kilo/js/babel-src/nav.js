export class Nav extends React.Component {
    constructor (props) {
        super(props);
        this.state = { ...props };
    }

    // TODO: extract single link
    render() {
        return (
          <nav className="navbar navbar-expand-lg navbar-light bg-light d-flex">
            <ul className="navbar-nav flex-grow-1">
              <li className="nav-item">
                <a className={`navbar-brand nav-link ${this.props.panel === "recent" ? 'active' : ''}`} href="#"
                   data-panel="recent" onClick={this.props.setPanel}>
                  Kilo
                </a>
              </li>
              <li className="nav-item">
                <a className={`nav-link ${this.props.panel === "frequency" ? 'active' : ''}`} href="#"
                   data-panel="frequency" onClick={this.props.setPanel}>
                  Consistency
                </a>
              </li>
              <li className="nav-item">
                <a className={`nav-link ${this.props.panel === "pace" ? 'active' : ''}`} href="#"
                   data-panel="pace" onClick={this.props.setPanel}>
                  Speed
                </a>
              </li>
              <li className="nav-item">
                <a className={`nav-link ${this.props.panel === "history" ? 'active' : ''}`} href="#"
                   data-panel="history" onClick={this.props.setPanel}>
                  History
                </a>
              </li>
              <li className="nav-item">
                <a className={`nav-link ${this.props.panel === "stats" ? 'active' : ''}`} href="#"
                   data-panel="stats" onClick={this.props.setPanel}>
                  Stats
                </a>
              </li>
            </ul>
            {!this.props.loading && <div className="me-2">
              <div className="dropdown dropstart">
                <button className="btn btn-outline-secondary dropdown-toggle" id="add-workout-dropdown-btn" type="button"
                        data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  Add
                </button>
                <ul class="dropdown-menu" aria-labelledby="add-workout-dropdown-btn">
                  {this.props.templates.map((template, index) => (<li key={index}>
                    <a className="dropdown-item" onClick={() => this.props.addDayRecord(template)}>
                      {template.activity} {template.distance} {template.distance_unit}
                    </a>
                  </li>))}
                  {!!this.props.templates.length && <div role="separator" className="dropdown-divider"></div>}
                  <li>
                    <a class="dropdown-item" href="#" onClick={this.props.addDayRecord}>Blank Day</a>
                  </li>
                </ul>
              </div>
            </div>}
          </nav>
        );
    }
}
