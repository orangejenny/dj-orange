$(function() {
    // TODO: Export single album from modal
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
