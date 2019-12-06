function addSong(focus) {
    var $modal = $("#new-album");
    var lastArtist = $modal.find(".song [name='artist']:last").val();
    var $newSong = $modal.find(".song.hide").clone().removeClass("hide");
    $modal.find("#add-song").before($newSong);
    if (lastArtist) {
        $newSong.find("[name='artist']").val(lastArtist);
    }
    var $rows = $modal.find(".song:visible");
    _.each($rows, function(row, r) {
        _.each($(row).find("input"), function(input, i) {
            if (i < 2) {
                // First two columns: name and artist
                $(input).attr("tabindex", $rows.length * i + r + 1);
            } else {
                // Time columns
                $(input).attr("tabindex", $rows.length * 2 + r + i - 1);
            }
        });
    });
    if (focus) {
        $newSong.find("input:first").focus();
    }
    numberSongs();
}

function numberSongs() {
    $("#new-album .ordinal:visible").each(function(index) {
        $(this).html(index + 1 + '.');
    });
}

$(function () {
    $("#add-album").click(function() {
        var $modal = $("#new-album");
        $modal.modal();
        $modal.find("input:first").focus();
        if (!$modal.find(".song:visible").length) {
            addSong(false);
        }
    });

    $("#add-song input").focus(function() {
        $(this).select();
    });

    $("#new-album #add-song button").click(function() {
        var count = $("#add-song input").val();
        if (!parseInt(count)) {
            count = 1;
        }
        for (var i = 0; i < count; i++) {
            addSong(true);
        }
    });

    $("#new-album").on("click", ".fa-trash", function() {
        $(this).closest(".song").remove();
        numberSongs();
    });

    $("#cancel-add-album").click(function() {
        var $modal = $("#new-album");
        $modal.find(".song:visible").remove();
        $modal.find("input[type='text']").val("");
        $modal.find("input[type='checkbox']").attr("checked", false);
        $modal.modal('hide');
    });

    $("#save-album").click(function() {
        var data = {};
        var $modal = $("#new-album");
        var $header = $modal.find(".modal-header");
        var $name = $header.find("[name='album_name']");
        if (!$name.val()) {
            alert("Missing name");
            $name.focus();
        }

        var args = {
            NAME: $name.val(),
            ISMIX: $header.find("input[type='checkbox']").attr("checked"),
            SONGS: [],
        };
        var attributes = ['song_name', 'artist', 'minutes', 'seconds'];
        $modal.find(".song:visible").each(function() {
            var values = {};
            for (var i = 0; i < attributes.length; i++) {
                var $obj = $(this).find("[name='" + attributes[i] + "']");
                if (!$obj.val()) {
                    alert("Missing data");
                    $obj.focus();
                }
                values[attributes[i].toUpperCase()] = $obj.val();
            }
            if (values.SECONDS < 10) {
                values.SECONDS = '0' + values.SECONDS;
            }
            values.TIME = values.MINUTES + ':' + values.SECONDS;
            args.SONGS.push(values);
        });
        $(this).attr("disabled", true);
        $(this).closest("form").submit();
    });
});
