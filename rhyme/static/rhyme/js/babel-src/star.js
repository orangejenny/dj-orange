import { Editable } from "./editable.js";

export class Star extends Editable {
    onClick() {
        this.updateSong(!this.state.value);
    }

    render() {
        return (
            <td className="icon-cell is-starred">
              <i className={`fa-star ${this.state.value ? "fas" : "far"} ${this.state.saving ? "update-in-progress" : ""}`}
                 onClick={this.onClick}></i>
            </td>
        );
    }
}