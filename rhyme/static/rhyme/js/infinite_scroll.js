function filterModel (options) {
    AssertArgs(options, ['lhs', 'op', 'rhs']);
    var self = _.extend({}, options);

    self.serialize = function () {
        return self.lhs + self.op + self.rhs
    };

    return self;
}

function itemPageModel(options) {
    AssertArgs(options, ['url']);

    var self = {};

    self.url = options.url;
    self.page = ko.observable(1);
    self.allowScroll = ko.observable(true);
    self.items = ko.observableArray();
    self.filters = ko.observableArray();
    self.count = ko.observable(0);
    self.isLoading = ko.observable(true);

    self.modalTitle = ko.observable('Songs');
    self.modalSongs = ko.observableArray();

    self.page.subscribe(function (newValue) {
        self.goToPage(newValue);
    });

    self.nextPage = function() {
        if (self.allowScroll()) {
            self.page(self.page() + 1);
        }
    };

    self.goToPage = function (page) {
        self.allowScroll(false);
        self.isLoading(true);
        $.ajax({
            method: 'GET',
            url: self.url,
            data: {
                page: page,
                filters: self.serializeFilters(),
            },
            success: function(data) {
                self.isLoading(false);
                self.count(data.count);

                if (page === 1) {
                    self.items(data.items);
                    //$postNav.scrollTop(0);    // TODO
                } else {
                    self.items(self.items().concat(data.items));
                }
                self.allowScroll(true);
            },
        });
    };

    self.addFilter = function (lhs, op, rhs) {
        self.filters.push(filterModel({
            lhs: lhs,
            op: op,
            rhs: rhs,
        }));
        self.goToPage(1);
    };

    self.getFilterValue = function (e) {
        return $(e.target).closest(".form-group").find("input").val();
    };

    self.removeFilter = function (filter) {
        self.filters.remove(filter);
        self.goToPage(1);
    };

    self.serializeFilters = function () {
        return _.map(self.filters(), function(f) { return f.serialize() }).join("&&");
    };

    self.showModal = function () {
        var album = this;
        self.modalTitle(album.name);

        var $modal = $("#song-list");
        $modal.modal();
        // TODO: loading indicator
        $.ajax({
            method: 'GET',
            url: reverse('song_list'),
            data: {
                album_id: album.id,
            },
            success: function (data) {
                self.modalSongs(data.items);
                var $backdrop = $(".modal-backdrop.in"),
                    $image = $backdrop.clone();
                $image.css("background-color", "transparent")
                      .css("background-size", "cover")
                      .css("background-repeat", "no-repeat")
                      .css("background-position", "center");
                if (album.cover_art_filename) {
                    $image.css("background-image", "url('" + album.cover_art_filename + "')")
                }
                $backdrop.before($image);
    
                $modal.one("hide.bs.modal", function() {
                    $image.remove();
                });
            },
            error: {
                // TODO: error handling
            },
        });
    };

    // Initialize: go to first page
    self.goToPage(1);

    return self;
}

$(function() {
    var $postNav = $(".post-nav"),
        $itemPage = $postNav.find(".item-page");
    if (!$itemPage.length) {
        return;
    }

    var model = itemPageModel({
        url: $itemPage.data("url"),
    });
    ko.applyBindings(model);

    $itemPage.scroll(function(e) {
        var overflowHeight = $itemPage.find(".infinite-scroll-container").height() - $itemPage.height()
        if ($itemPage.scrollTop() / overflowHeight > 0.8) {
            model.nextPage();
        }
    });

    // TODO: clear filter inputs
    $(".filter-modal").on('show.bs.modal', function(e) {
        $(e.currentTarget).find("input").each(function(index, input) {
            $(input).val('');
        });
    });
});
