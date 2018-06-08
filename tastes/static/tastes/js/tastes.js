$(function() {
    var page = 1,
        allowScroll = true;
    var getNextPage = function() {
        allowScroll = false;
        $.ajax({
            method: 'GET',
            url: $("#data-urls").data("song-list"),
            data: {
                page: page,
            },
            success: function(data) {
                $("#song-count").text(data.count);
                var $tbody = $("#song-table tbody"),
                    template = _.template($("#song-row").text());
                _.each(data.songs, function(song) {
                    $tbody.append(template(song));
                });
                page++;
                allowScroll = true;
            },
        });
    };

    getNextPage();
    $("#content-column").scroll(function(e) {
        if (!allowScroll) {
            return;
        }

        var $column = $(e.currentTarget),
            overflowHeight = $column.children(".scroll-container").height() - $column.height()
        if ($column.scrollTop() / overflowHeight > 0.8) {
            getNextPage();
        }
    });
});
