import { Star } from "./babel-prod/star.js";
import { Tags } from "./babel-prod/tags.js";

ko.bindingHandlers.react = {
    init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
        var options = valueAccessor(),
            component = {
                "star": Star,
                "tags": Tags,
            }[options.component];
        delete options.component;
        ReactDOM.render(React.createElement(component, options), element);
    },
};

var iconClasses = {
    'rating': 'fa-star',
    'energy': 'fa-fire',
    'mood': 'fa-heart',
};

$(document).ready(function() {
    var selector = "[contenteditable=true][data-field]",
        $body = $("body"),
        oldValue = undefined;

    // TODO: move to knockout
    $body.on("focus", selector, function() {
        var $editable = $(this);
        if ($editable.find(".rating").length) {
            $editable = $editable.find(".rating");
        }
        if ($editable.hasClass("rating")) {
            oldValue = $editable.find(".fas:not(.blank)").length;
            $editable.html(StringMultiply("*", oldValue));
        }
        else {
            oldValue = $editable.text().trim();
        }
    });

    // TODO: move to knockout
    $body.on("blur", selector, function() {
        var $editable = $(this),
            field = $editable.data("field"),
            $container = $editable.closest("[data-song-id]"),
            value = $editable.text().trim();
        if ($editable.hasClass("rating")) {
            value = value.length;
            $editable.html(ratingHTML(iconClasses[field], value || oldValue));
        }
        if (value && oldValue != value) {
            var id = $container.data("song-id");

            // Update server
            $editable.addClass("update-in-progress");
            $.ajax({
                method: 'POST',
                url: reverse('song_update'),
                data: {
                    csrfmiddlewaretoken: $("#csrf-token").find("input").val(),
                    id: id,
                    field: field,
                    value: value,
                },
                success: function (data) {
                    $editable.removeClass("update-in-progress");
                },
                error: function () {
                    $editable.addClass("danger");
                },
            });
        }
        oldValue = undefined;
    });
});

function ratingHTML(iconClass, number) {
    return StringMultiply("<span class='fas " + (number ? "" : "blank ") + iconClass + "'></span>", number || 5);
} 