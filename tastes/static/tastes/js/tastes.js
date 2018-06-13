$(function() {
    var page = 1,
        allowScroll = true,
        filters = [];
    var getNextPage = function() {
        allowScroll = false;
        $.ajax({
            method: 'GET',
            url: $("#data-urls").data("song-list"),
            data: {
                page: page,
                filters: serializeFilters(),
            },
            success: function(data) {
                $("#song-count").text(data.count);
                var $tbody = $("#song-table tbody"),
                    template = _.template($("#song-row").text());
                if (page === 1) {
                    $("#content-column").scrollTop(0);
                    $tbody.empty();
                }
                _.each(data.songs, function(song) {
                    $tbody.append(template(song));
                });
                page++;
                allowScroll = true;
            },
        });
    };

    var serializeFilters = function() {
        return _.map(filters, function(f) { return f.lhs + f.op + f.rhs }).join("&&");
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

    $(".filter-modal").on('show.bs.modal', function(e) {
        $(e.currentTarget).find("input").each(function(index, input) {
            $(input).val('');
        });
    });

    $(".filter-modal button").click(function(e) {
        var $button = $(e.currentTarget);
        filters.push({
            lhs: $button.closest("[data-lhs]").data("lhs"),
            op: $button.data("op"),
            rhs: $button.data("rhs") === undefined ? $button.closest(".form-group").find(".rhs").val() : $button.data("rhs"),
        });
        page = 1;
        getNextPage();
    });
});
