export class Star extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            id: this.props.id,
            value: this.props.value,
            saving: false,
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
            }),
        }).then((resp) => resp.json()).then(data => {
            this.setState({
                saving: false,
                value: !this.state.value,
            });
        }).catch((error) => {
            throw(error);
        });
    }

    render() {
        return (
            <i className={`fa-star ${this.state.value ? "fas" : "far"} ${this.state.saving ? "update-in-progress" : ""}`}
               onClick={this.toggleStar}></i>
        );
    }
}