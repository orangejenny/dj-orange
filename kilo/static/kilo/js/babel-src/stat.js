export class Stat extends React.Component {
    render() {
        return (
          <div className="card">
            <div className="card-header text-center">{this.props.title}</div>
            <div className="card-body">
              <table class="table table-striped">
              <tbody>
                {this.props.stats.map((stat, index) => (<tr key={index}>
                  <td>{stat.name}</td>
                  <td>{stat.primary}</td>
                  <td>{stat.secondary}</td>
                </tr>))}
              </tbody>
              </table>
            </div>
          </div>
        );
    }
}
