export class Nav extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            activity: props.activity,
        };
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
          </nav>
        );
    }
}