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
});
