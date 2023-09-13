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
          </nav>
        );
    }
}
