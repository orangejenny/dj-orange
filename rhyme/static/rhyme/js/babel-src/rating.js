export class Rating extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            id: this.props.id,
            value: this.props.value,
            saving: false,
            maxRating: 5,
            editing: false,
        };

        this.onBlur = this.onBlur.bind(this);
        this.onClick = this.onClick.bind(this);
        this.updateSong = this.updateSong.bind(this);
    }

    onClick() {
      this.setState({ editing: true });
    }

    onBlur(e) {
      this.setState({ editing: false });
      this.updateSong(e);
    }

    // TODO: DRY up with tags.js
    updateSong(e) {
        var newValue = Math.min(e.target.value.length, this.state.maxRating);
        if (!newValue || newValue === this.state.value) {
            return;
        }
        this.setState({ saving: true });
        fetch(reverse("song_update"), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector("#csrf-token input").value,
            },
            body: JSON.stringify({
                id: this.state.id,
                field: this.props.field,
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
    }

    render() {
        return (
            <td className={`rating ${this.state.saving ? "update-in-progress" : ""}`} onClick={this.onClick}>
              {!this.state.editing && Array(this.state.value || this.state.maxRating).fill("x").map((x, i) => {
                if (this.props.icon) {
                  return (
                    <span key={i} className={`fas fa-${this.props.icon} ${this.state.value ? "" : "blank"}`}></span>
                  );
                } else {
                  return "*";
                }
              })}
              {this.state.editing && <input autoFocus type="text" onBlur={this.onBlur} />}
            </td>
        );
    }
}