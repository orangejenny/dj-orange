$(function() {
    console.log($("#data-urls").data("song-list"));
    $.ajax({
        method: 'GET',
        url: $("#data-urls").data("song-list"),
        success: function(data) {
            $("#song-count").text(data.count);
            var $tbody = $("#song-table tbody"),
                template = _.template($("#song-row").text());
            _.each(data.songs, function(song) {
                $tbody.append(template(song));
            });
        },
    });
});
