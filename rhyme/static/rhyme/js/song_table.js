var iconClasses = {
    'rating': 'fa-star',
    'energy': 'fa-fire',
    'mood': 'fa-heart',
};

$(document).ready(function() {
    var selector = "[contenteditable=true][data-field]",
        $body = $("body"),
        oldValue = undefined;

    $body.on("focus", selector, function() {
        var $editable = $(this);
        if ($editable.hasClass("rating")) {
            oldValue = $editable.children(".fas:not(.blank)").length;
            $editable.html(StringMultiply("*", oldValue));
        }
        else {
            oldValue = $editable.text().trim();
        }
    });

    $body.on("blur", selector, function() {
        var $editable = $(this),
            field = $editable.data("field"),
            $container = $editable.closest("[data-song-id]"),
            value = $editable.text().trim();
        if ($editable.hasClass("rating")) {
            value = value.length;
            $editable.html(ratingHTML(iconClasses[field], value));
        }
        if (oldValue != value) {
            var id = $container.data("song-id");

            // Update server
            $editable.addClass("update-in-progress");
            $.ajax({                     // TODO: dry up with $.ajax below?
                method: 'POST',
                url: '/rhyme/songs/update/',    // TODO: client-side reverse
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

    $("body").on("click", ".song-table .icon-cell .fa-star", function() {
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
        url: '/rhyme/songs/update/',    // TODO: client-side reverse
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

function showSongModal(song_list_data, callback, title) {
    var $modal = $("#song-list"),
        $body = $modal.find(".modal-body");
    $body.html($("body .loading").clone().removeClass("hide"));
    $modal.find(".modal-title").text(title || "Songs");
    $modal.modal();
    $.ajax({
        method: 'GET',
        url: '/rhyme/songs/list/',    // TODO: client-side URLs
        data: song_list_data,
        success: function (data) {
            var $body = $("#song-list .modal-body"),
                $table = $("<table class='song-table'></table>"),
                count = 0,
                songTemplate = _.template($("#song-row").text());

            _.each(data.items, function(song) {
                $table.append(songTemplate(_.extend(song, {
                    // TODO: track number
                    TRACKNUMBER: ++count,
                    ISSTARREDHTML: "<span class='" + (parseInt(song.ISSTARRED) ? "fas" : "far") + " fa-star'></span>",
                    RATINGHTML: ratingHTML(iconClasses['rating'], song.RATING),
                    ENERGYHTML: ratingHTML(iconClasses['energy'], song.ENERGY),
                    MOODHTML: ratingHTML(iconClasses['mood'], song.MOOD),
                })));
            });
            $body.html($table);
            if (callback && _.isFunction(callback)) {
                callback.apply();
            }
        },
        error: {
            // TODO
        },
    });
}
