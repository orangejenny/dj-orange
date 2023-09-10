export class Nav extends React.Component {
    constructor (props) {
        super(props);
        this.state = { ...props };
        this.state.links = [{
            panel: "frequency",
            label: "Kilo",
        }, {
            panel: "recent",
            label: "Recent",
        }, {
            panel: "pace",
            label: "Speed",
        }, {
            panel: "stats",
            label: "Achievement",
        }, {
            panel: "history",
            label: "History",
        }];
    }

    render() {
        return (
          <nav className="navbar navbar-expand-lg navbar-light bg-light d-flex">
            <ul className="navbar-nav flex-grow-1">
              {this.state.links.map((link, index) => (
                <li key={index} className="nav-item">
                  <a className={`nav-link ${this.props.panel === link.panel ? 'active' : ''}`} href="#"
                     data-panel={link.panel} onClick={this.props.setPanel}>
                     {link.label}
                  </a>
                </li>))}
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
