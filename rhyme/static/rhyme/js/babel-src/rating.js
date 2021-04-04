import { Editable } from "./editable.js";

export class Rating extends Editable {
    constructor(props) {
        super(props);
        this.state.serializeValue = (value) => Math.min(value.length, 5);
    }

    onBlur(e) {
      this.setState({ editing: false });
      if (e.target.value) {
        this.updateSong(e.target.value);
      }
    }

    render() {
        return (
            <td className={`rating ${this.state.saving ? "update-in-progress" : ""}`} onClick={this.onClick}>
              {!this.state.editing && Array(this.state.value || 5).fill("x").map((x, i) => {
                return (
                  <span key={i} className={`fas fa-${this.props.icon} ${this.state.value ? "" : "blank"}`}></span>
                );
              })}
              {this.state.editing && <input autoFocus type="text" onBlur={this.onBlur} />}
            </td>
        );
    }
}