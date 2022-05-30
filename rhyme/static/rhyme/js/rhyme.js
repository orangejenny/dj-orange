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
    return self;
}

function SongModel(options) {
    var self = _.extend({}, options);
    self.albums = _.map(options.albums, AlbumModel);
    return self;
}

function rhymeModel (options) {
    AssertArgs(options, ['model'], ['init', 'url']);

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

    self.modalName = ko.observable("");
    self.modalHeaders = ko.observableArray();
    self.modalSongs = ko.observableArray();     // flat list, even for multi-disc albums
    self.songListParams = ko.observable();

    self.refresh = function(page) {
        if (!self.url) {
            return;
        }

        page = page || 1;
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
                } else {
                    self.items(self.items().concat(data.items));
                }
                if (data.more) {
                    self.allowScroll(true);
                }
            },
        });
    };

    self.page.subscribe(function (newValue) {
        self.refresh(newValue);
    });

    self.nextPage = function() {
        if (self.allowScroll()) {
            self.page(self.page() + 1);
        }
    };

    self.addFilter = function (model, lhs, op, rhs) {
        self.filters.push(filterModel({
            model: model,
            lhs: lhs,
            op: op,
            rhs: rhs,
        }));
        self.refresh();
    };

    self.omniFilter.subscribe(_.throttle(function (newValue) {
        self.refresh();
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
        self.refresh();
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
        self.refresh();
    };

    self.useAnd = ko.computed(function () {
        return self.conjunction() === "&&";
    });

    self.useOr = ko.computed(function () {
        return self.conjunction() === "||";
    });

    self.exportPlaylist = function (config, additionalParams) {
        ExportPlaylist(_.extend({
            config: config,
            model: self.model,
        }, self.serializeFilters(), additionalParams));
    };

    self.showModal = function (name, songListParams) {
        self.modalName(name);
        self.modalHeaders([]);
        self.modalSongs([]);
        self.songListParams(songListParams);

        var $modal = $("#song-list");
        self.isLoading(true);
        $modal.modal();
        songListParams.songs_per_page = 100;    // TODO: paginate modal?
        $.ajax({
            method: 'GET',
            url: reverse('song_list'),
            data: songListParams,
            success: function (data) {
                self.isLoading(false);
                self.modalSongs(data.items);
                self.modalHeaders(data.disc_names.length > 1 ? data.disc_names.length : []);
                var $backdrop = $(".modal-backdrop.in"),
                    $image = $backdrop.clone();
                $image.css("background-color", "transparent")
                      .css("background-size", "cover")
                      .css("background-repeat", "no-repeat")
                      .css("background-position", "center");
                if (data.cover_art_filename) {
                    $image.css("background-image", "url('" + data.cover_art_filename + "')")
                }
                $backdrop.before($image);

                $modal.one("hide.bs.modal", function() {
                    $image.remove();
                });
            },
            error: function () {
                // TODO: error handling
            },
        });
    };

    self.hideModal = function () {
        // needed for subclasses
        return true;
    };

    // Initialize: go to first page
    if (options.init || options.init === undefined) {
        self.refresh();
    }

    return self;
}

$(function() {
    // TODO: move to knockout
    $(".select2").each(function (index, element) {
        var $element = $(element),
            data = $element.data(),
            options = {
                width: "100%",
            };
        if ($element.hasClass("in-modal")) {
            options.dropdownParent = $element.closest(".modal");
        }
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
