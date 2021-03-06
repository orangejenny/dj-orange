function filterModel (options) {
    AssertArgs(options, ['model', 'lhs', 'op', 'rhs']);
    var self = _.extend({}, options);

    self.serialize = function () {
        return self.lhs + self.op + self.rhs
    };

    self.readOnly = function () {
        var op = self.op;
        op = {
            '=': 'is',
            '*=': 'contains',
            '<=': 'at most',
            '>=': 'at least',
        }[op] || op;

        var rhs = self.rhs;
        if (_.isNaN(parseInt(rhs))) {
            rhs = '"' + rhs + '"';
        }

        return self.lhs + ' ' + op + ' ' + rhs;
    };

    return self;
}

function AlbumModel(options) {
    var self = _.extend({}, options);
    self.songs = ko.observableArray();

    self.exportPlaylist = function (config) {
        ExportPlaylist({
            config: config,
            album_id: self.id,
            filename: self.artist + " - " + self.name,
            model: 'album',
        });
    };

    return self;
}

function SongModel(options) {
    return _.extend({}, options);
}

function rhymeModel (options) {
    AssertArgs(options, ['model'], ['url']);

    var self = {};

    self.model = options.model;
    self.url = options.url;
    self.page = ko.observable(1);
    self.allowScroll = ko.observable(true);
    self.items = ko.observableArray();
    self.filters = ko.observableArray();
    self.count = ko.observable(0);
    self.isLoading = ko.observable(true);
    self.omniFilter = ko.observable('');

    self.modalAlbum = ko.observable();
    self.modalDiscs = ko.observableArray();

    self.page.subscribe(function (newValue) {
        self.goToPage(newValue);
    });

    self.nextPage = function() {
        if (self.allowScroll()) {
            self.page(self.page() + 1);
        }
    };

    self.goToPage = function (page) {
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
    };

    self.addFilter = function (model, lhs, op, rhs) {
        self.filters.push(filterModel({
            model: model,
            lhs: lhs,
            op: op,
            rhs: rhs,
        }));
        self.goToPage(1);
    };

    self.omniFilter.subscribe(_.throttle(function (newValue) {
        self.goToPage(1);
    }, {leading: false}));

    self.getFilterValue = function (e) {
        var $input = $(e.target).closest(".form-group").find("input, select");
        if (!$input.length) {
            $input = $(e.target).closest(".modal").find("input, select");
        }
        var value = $input.val();
        if (_.isArray(value)) {
            value = value.join(",");
        }
        return value;
    };

    self.getTimeFilterValue = function (e) {
        var value = $(e.target).closest(".form-group").find("input").val(),
            match = value.match(/^(\d+):(\d+)$/);
        if (!match) {
            alert("Invalid time, please enter MM:SS value")
        }
        return match[1] * 60 + match[2] * 1;
    };

    self.removeFilter = function (filter) {
        self.filters.remove(filter);
        self.goToPage(1);
    };

    self.focusFilter = function (model, e) {
        $modal = $(e.target);
        $modal.find("input, select").each(function(index, input) {
            $(input).val('').trigger('change');
        });
        $modal.find("input:first").focus();
    };

    self.serializeFilters = function () {
        return {
            album_filters: self.albumFilters(),
            song_filters: self.songFilters(),
            omni_filter: self.omniFilter(),
        };
    };

    self.conjunction = ko.observable("&&");

    self.albumFilters = ko.computed(function () {
        return _.map(_.where(self.filters(), {model: 'album'}), function(f) { return f.serialize() }).join(self.conjunction());
    });

    self.songFilters = ko.computed(function () {
        return _.map(_.where(self.filters(), {model: 'song'}), function(f) { return f.serialize() }).join(self.conjunction());
    });

    self.toggleConjunction = function () {
        if (self.conjunction() === "&&") {
            self.conjunction("||");
        } else {
            self.conjunction("&&");
        }
        self.goToPage(1);
    };

    self.useAnd = ko.computed(function () {
        return self.conjunction() === "&&";
    });

    self.useOr = ko.computed(function () {
        return self.conjunction() === "||";
    });

    self.exportPlaylist = function (config) {
        ExportPlaylist(_.extend({
            config: config,
            model: self.model,
        }, self.serializeFilters()));
    };

    self.showModal = function () {
        var album = this;
        self.modalAlbum(album);
        self.modalDiscs([]);

        var $modal = $("#song-list");
        $modal.modal();
        $.ajax({
            method: 'GET',
            url: reverse('song_list'),
            data: {
                album_id: album.id,
            },
            success: function (data) {
                album.songs(data.items);
                self.modalDiscs(data.disc_names);
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

    var model = rhymeModel({
        model: document.location.href.indexOf("albums") == -1 ? 'song' : 'album',
        url: $itemPage.data("url"),
    });
    ko.applyBindings(model);

    // TODO: move to knockout
    $itemPage.scroll(function(e) {
        var overflowHeight = $itemPage.find(".infinite-scroll-container").height() - $itemPage.height()
        if ($itemPage.scrollTop() / overflowHeight > 0.8) {
            model.nextPage();
        }
    });

    // TODO: move to knockout
    $(".select2.in-modal").each(function (index, element) {
        var $element = $(element),
            data = $element.data(),
            options = {
                dropdownParent: $element.closest(".modal"),
                width: "100%",
            };
        if (data.url) {
            options.ajax = {
                url: reverse(data.url),
                dataType: 'json',
                processResults: function (data) {
                    return {
                        results: data.items,
                        pagination: {
                            more: false,
                        },
                    };
                },
            };
        }
        $element.select2(options);
    });
});
