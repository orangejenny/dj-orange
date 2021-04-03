import { Rating } from "./babel-prod/rating.js";
import { Star } from "./babel-prod/star.js";
import { Tags } from "./babel-prod/tags.js";

ko.bindingHandlers.react = {
    init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
        var options = valueAccessor(),
            component = {
                "rating": Rating,
                "star": Star,
                "tags": Tags,
            }[options.component];
        delete options.component;
        ReactDOM.render(React.createElement(component, options), element);
    },
};