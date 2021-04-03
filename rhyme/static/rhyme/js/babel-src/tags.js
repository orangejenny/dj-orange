export class Tags extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            id: this.props.id,
            value: this.props.value,
            saving: false,
            editing: false,
        };

        this.onBlur = this.onBlur.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onClick = this.onClick.bind(this);
        this.updateSong = this.updateSong.bind(this);
    }

    onChange(e) {
        this.setState({value: e.target.value})
    }

    onClick() {
      this.setState(function(state, props) {
          return {
              editing: true,
              oldValue: state.value,
          };
        });
    }

    onBlur(e) {
      this.setState({ editing: false });
      this.updateSong(e);
    }

    updateSong(e) {
        this.setState(function(state, props) {
            var newValue = e.target.value;
            if (newValue === state.oldValue) {
                return;
            }
            fetch(reverse("song_update"), {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector("#csrf-token input").value,
                },
                body: JSON.stringify({
                    id: this.state.id,
                    field: 'tags',
                    value: newValue,
                }),
            }).then((resp) => resp.json()).then(data => {
                this.setState({
                    saving: false,
                    value: data.value,
                });
            }).catch((error) => {
                throw(error);
            });
            return { saving: true };
        });
    }

    render() {
        return (
            <div className={this.state.saving ? "update-in-progress" : ""} onClick={this.onClick}>
              {!this.state.editing && this.state.value}
              {this.state.editing &&
                <textarea value={this.state.value} className="form-control" autoFocus type="text" onChange={this.onChange} onBlur={this.onBlur}></textarea>
              }
            </div>
        );
    }
}