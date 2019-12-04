$(function() {
    var $postNav = $(".post-nav"),
        $infiniteScrollContainer = $postNav.children(".infinite-scroll-container");

    if ($infiniteScrollContainer.length) {
        var page = 1,
            allowScroll = true,
            filters = [];

        function getNextPage() {
            allowScroll = false;
            $.ajax({
                method: 'GET',
                url: $infiniteScrollContainer.data("url"),
                data: {
                    page: page,
                    filters: serializeFilters(),
                },
                success: function(data) {
                    var countSelector = $infiniteScrollContainer.data("count-element");
                    if (countSelector) {
                        $(countSelector).text(data.count);
                    }

                    var $dataContainer = $infiniteScrollContainer.find(".infinite-scroll-data"),
                        template = _.template($($infiniteScrollContainer.data("template")).text());
                    if (page === 1) {
                        $postNav.scrollTop(0);
                        $dataContainer.empty();
                    }
                    _.each(data.items, function(item) {
                        $dataContainer.append(template(item));
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
        $postNav.scroll(function(e) {
            if (!allowScroll) {
                return;
            }

            var overflowHeight = $infiniteScrollContainer.height() - $postNav.height()
            if ($postNav.scrollTop() / overflowHeight > 0.8) {
                getNextPage();
            }
        });
    }
});