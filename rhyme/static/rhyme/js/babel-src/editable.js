export class Editable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            id: this.props.id,
            value: this.props.value,
            saving: false,
            editing: false,
            serializeValue: (value) => value,
        };

        this.onBlur = this.onBlur.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onClick = this.onClick.bind(this);
        this.updateSong = this.updateSong.bind(this);
    }

    onChange(e) {
        this.setState({
            value: this.state.serializeValue(e.target.value),
        });
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
      this.updateSong(e.target.value);
    }

    updateSong(newValue) {
        this.setState(function(state, props) {
            newValue = this.state.serializeValue(newValue);
            if (newValue === state.oldValue) {
                return;
            }
            console.log("sending " + newValue);
            fetch(reverse("song_update"), {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector("#csrf-token input").value,
                },
                body: JSON.stringify({
                    id: this.state.id,
                    field: props.field,
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
            <td className={`$(this.state.saving ? "update-in-progress" : ""} ${this.props.extraClasses}`}
                onClick={this.onClick}>
              {!this.state.editing && this.props.readView}
              {this.state.editing && (this.props.editView ||
                <input value={this.state.value} className="form-control" autoFocus type="text" onBlur={this.onBlur} onChange={this.onChange} />
              )}
            </td>
        );
    }
}