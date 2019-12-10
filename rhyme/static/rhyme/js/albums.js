$(function() {
    $(".albums").on("click", ".album", function() {
        var $album = $(this),
            id = $album.data("id");
        showSongModal({
            album_id: id,
        }, function() {
            var $modal = $("#song-list");
            $modal.data("id", id);
            var $backdrop = $(".modal-backdrop.in"),
                $image = $backdrop.clone(),
                $covers = $album.find("img");
            $image.css("background-color", "transparent")
                  .css("background-size", "cover")
                  .css("background-repeat", "no-repeat")
                  .css("background-position", "center");
            if ($covers.length) {
                var src = $covers[parseInt(Math.random() * $covers.length)].src;
                $image.css("background-image", "url('" + src + "')")
            }
            $backdrop.after($image);

            $modal.one("hide.bs.modal", function() {
                $image.remove();
            });
        }, $album.find(".name").text());
    });

    // Export single album from modal
    $("body").on("click", "#song-list .export-dropdown [data-config]", function () {
        var album_id = $(this).closest("#song-list").data("id"),
            $album = $(".album[data-id='" + album_id + "']");
        ExportPlaylist({
            config: $(this).data("config"),
            album_id: album_id,
            filename: $album.find(".name").text(),
        });
    });
});
