class Loading extends React.Component {
    render() {
        return (
          <div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <div className="spinner-grow text-secondary m-3" role="status"></div>
            <span className="visually-hidden">Loading...</span>
          </div>
        );
    }
}