$(function() {
    var $postNav = $(".post-nav"),
        $itemPage = $postNav.find(".item-page");

    var model = rhymeModel({
        model: document.location.href.indexOf("albums") == -1 ? 'song' : 'album',
        url: $itemPage.data("url"),
        refreshCallback: function(self, page) {
            if (!self.url) {
                return;
            }
    
            self.allowScroll(false);
            self.isLoading(true);
            $.ajax({
                method: 'GET',
                url: self.url,
                data: _.extend({
                    page: page,
                    omni_filter: self.omniFilter(),
                    conjunction: self.conjunction(),
                }, self.serializeFilters()),
                success: function(data) {
                    if (data.omni_filter !== self.omniFilter()) {
                        return;
                    }
    
                    self.isLoading(false);
                    self.count(data.count);
    
                    if (page === 1) {
                        self.items(_.map(data.items, self.model == 'album' ? AlbumModel : SongModel));
                        //$postNav.scrollTop(0);    // TODO
                    } else {
                        self.items(self.items().concat(data.items));
                    }
                    if (data.more) {
                        self.allowScroll(true);
                    }
                },
            });
        },
    });
    ko.applyBindings(model);

    // TODO: move to knockout
    $itemPage.scroll(function(e) {
        var overflowHeight = $itemPage.find(".infinite-scroll-container").height() - $itemPage.height()
        if ($itemPage.scrollTop() / overflowHeight > 0.8) {
            model.nextPage();
        }
    });
});
