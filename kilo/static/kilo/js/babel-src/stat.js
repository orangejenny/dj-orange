export class Stat extends React.Component {
    render() {
        return (
          <div className="card text-center">
            <div className="card-header">{this.props.name}</div>
            <div className="card-body">
                <h1>{this.props.primary}</h1>
                {this.props.secondary}
            </div>
          </div>
        );
    }
}