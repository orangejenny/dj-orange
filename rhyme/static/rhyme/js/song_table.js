var iconClasses = {
    'rating': 'fa-star',
    'energy': 'fa-fire',
    'mood': 'fa-heart',
};

jQuery(document).ready(function() {
    var selector = "[contenteditable=true][data-key]",
        $body = $("body"),
        oldValue = undefined;

    $body.on("focus", selector, function() {
        var $editable = jQuery(this);
        if ($editable.hasClass("rating")) {
            oldValue = $editable.children(".fas:not(.blank)").length;
            $editable.html(StringMultiply("*", oldValue));
        }
        else {
            oldValue = $editable.text().trim();
        }
    });

    $body.on("blur", selector, function() {
        var $editable = jQuery(this),
            key = $editable.data("key"),
            $container = $editable.closest("[data-song-id]"),
            value = $editable.text().trim();
        if ($editable.hasClass("rating")) {
            value = value.length;
            $editable.html(ratingHTML(iconClasses[key], value));
        }
        if (oldValue != value) {
            var id = $container.data("song-id");
            var args = {
                id: id,
            }
            args[key] = value;
            $body.trigger('song-update', {
                id: id,
                value: value,
                oldValue: oldValue,
                key: key,
            });

            // Update server
            $editable.addClass("update-in-progress");
            CallRemote({
                SUB: 'Flavors::Data::Song::Update', 
                ARGS: args, 
                FINISH: function(data) {
                    $editable.removeClass("update-in-progress");
                }
            });
        }
        oldValue = undefined;
    });

    $(".song-table").on("click", ".icon-cell .fa-star", function() {
        var $star = $(this);
        toggleStar($star, $star.closest("tr").data("song-id"));
    });
});

function ratingHTML(iconClass, number) {
    return StringMultiply("<span class='fas " + (number ? "" : "blank ") + iconClass + "'></span>", number || 5);
}

function toggleStar($star, id, sub) {
    var isstarred = $star.hasClass("fas") ? 0 : 1;

    // Update markup
    $star.toggleClass("far");
    $star.toggleClass("fas");

    // Update server data
    $star.addClass("update-in-progress");
    $.ajax({
        method: 'POST',
        url: 'songs/update/',    // TODO: client-side reverse
        data: {
            csrfmiddlewaretoken: $("#csrf-token").find("input").val(),
            id: id,
            field: 'starred',
            value: isstarred,
        },
        success: function (data) {
            $star.removeClass("update-in-progress");
        },
        error: function () {
            $star.closest("td").addClass("danger");
        },
    });
}
