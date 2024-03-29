export class Star extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            id: this.props.id,
            value: this.props.value,
            activePlaylistName: this.props.activePlaylistName,
            saving: false,
            error: false,
            onClasses: this.props.onClasses,
            offClasses: this.props.offClasses,
        };

        this.toggleStar = this.toggleStar.bind(this);
    }

    toggleStar() {
        this.setState({ saving: true });
        fetch(reverse("song_update"), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector("#csrf-token input").value,
            },
            body: JSON.stringify({
                id: this.state.id,
                field: 'starred',
                value: this.state.value ? 0 : 1,
                playlist_name: this.state.activePlaylistName,
            }),
        }).then((resp) => resp.json()).then(data => {
            this.setState({
                saving: false,
                value: !this.state.value,
            });
        }).catch((error) => {
            this.setState({
                saving: false,
                error: true,
                value: !this.state.value,
            });
            throw(error);
        });
    }

    render() {
        return (
            <i className={`${!this.state.value && !this.state.saving || this.state.error ? this.state.offClasses : this.state.onClasses} ${this.state.saving ? "update-in-progress" : ""} ${this.state.error ? "text-danger" : ""}`}
               onClick={this.toggleStar}></i>
        );
    }
}
