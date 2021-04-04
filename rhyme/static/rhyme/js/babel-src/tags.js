import { Editable } from "./editable.js";

export class Tags extends React.Component {
    render() {
        return (
            <Editable field="tags" extraClasses="tags" { ...this.props } />
        );
    }
}