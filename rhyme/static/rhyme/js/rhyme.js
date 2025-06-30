function pluralize(count, stem) {
    return +count === 1 ? stem : stem + "s";
}

function filterTypeModel (options) {
    AssertArgs(options, ['lhs', 'root']);

    let self = {};
    self.lhs = options.lhs;
    self.root = options.root;

    self.relevantFilters = ko.computed(function () {
        return _.filter(self.root.filters(), function (f) {
            return f.lhs === self.lhs;
        });
    });

    self.filterText = ko.computed(function () {
        return _.map(self.relevantFilters(), function (f) {
            return f.readOnly();
        }).join(", ");
    });

    self.removeFilters = function () {
        _.each(self.relevantFilters(), function (f) {
            self.root.removeFilter(f);
        });
    };

    return self;
}

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

        return op + ' ' + rhs;
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

    self.starred = ko.observable(self.starred);
    self.updateInProgress = ko.observable(false);
    self.hasError = ko.observable(false);

    self.starOnClasses = self.activePlaylistName ? 'fa-check-square far' : 'fa-star fas';
    self.starOffClasses = self.activePlaylistName ? 'fa-square far' : 'fa-star far';
    self.starClass = ko.computed(function () {
        return self.starred() ? self.starOnClasses : self.starOffClasses;
    });

    self.toggleStar = function () {
        // Update markup
        self.starred(!self.starred());

        // Update server data
        self.updateInProgress(true);
        $.ajax({
            method: 'POST',
            url: reverse('song_update'),
            data: {
                csrfmiddlewaretoken: $("#csrf-token").find("input").val(),
                id: self.id,
                field: 'starred',
                value: self.starred() ? 1 : 0,
                playlist_name: this.activePlaylistName,
            },
            success: function (data) {
                self.updateInProgress(false);
            },
            error: function () {
                self.updateInProgress(false);
                self.hasError(true);
            },
        });
    }

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

    self.activePlaylistName = ko.observable('');
    self.starOnClasses = ko.computed(function () {
        return self.activePlaylistName() ? 'fa-check-square far' : 'fa-star fas';
    });
    self.starOffClasses = ko.computed(function () {
        return self.activePlaylistName() ? 'fa-square far' : 'fa-star far';
    });

    self.modalName = ko.observable("");
    self.modalHeaders = ko.observableArray();
    self.modalSongs = ko.observableArray();     // flat list, even for multi-disc albums
    self.songListParams = ko.observable();
    self.songListCount = ko.observable(0);

    self.refresh = function(page) {
        if (!self.url) {
            return;
        }

        page = page || 1;
        self.allowScroll(false);
        self.isLoading(true);
        console.log(decodeURIComponent(new URLSearchParams(self.serializeFilters()).toString()));
        $.ajax({
            method: 'GET',
            url: self.url,
            data: _.extend({
                page: page,
                omni_filter: self.omniFilter(),
                conjunction: self.conjunction(),
                active_playlist_name: self.activePlaylistName(),
            }, self.serializeFilters()),
            success: function(data) {
                if (data.omni_filter !== self.omniFilter()) {
                    return;
                }

                self.isLoading(false);
                self.count(data.count);

                var wrappedItems = _.map(data.items, function (item) {
                    if (self.model == 'album') {
                        return AlbumModel(item);
                    } else {
                        return SongModel(_.extend(item, {
                            activePlaylistName: self.activePlaylistName(),
                        }));
                    }
                });
                if (page === 1) {
                    self.items(wrappedItems);
                } else {
                    self.items(self.items().concat(wrappedItems));
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

    self.filterTypeModels = {};
    self.getFilterTypeModel = function(lhs) {
         if (!self.filterTypeModels[lhs]) {
            self.filterTypeModels[lhs] = new filterTypeModel({
                lhs: lhs,
                root: self,
            });
        }
        return self.filterTypeModels[lhs];
    }

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

    let knownPlaylistNames = [];
    $(document).ready(function () {
        knownPlaylistNames = $("#active-playlist option:not(:first)").toArray().map((o) => o.innerText);
    });
    self.activePlaylistName.subscribe(function (newValue) {
        _.each(self.filters(), function (f) {
            if (f.lhs === 'playlist') {
                self.removeFilter(f);
            }
        });
        if (newValue && knownPlaylistNames.find((p) => p === newValue)) {
            self.addFilter(self.model, 'playlist', "*=", newValue);
        } else {
            knownPlaylistNames.push(newValue);
            self.refresh();
        }
    });

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

    self.exportPlaylist = function (config, model, additionalParams) {
        var params = {
            config: config,
            model: model,
        };
        if (self.modalName()) {
            params = _.extend(params, {
                filename: self.modalName(),
            }, self.songListParams());
        } else {
            params = _.extend(params, self.serializeFilters());
        }
        params = _.extend(params, additionalParams);

        ExportPlaylist(params);
    };

    self.resetModal = function () {
        self.modalName("");
        self.modalHeaders([]);
        self.modalSongs([]);
        self.songListParams({});
        self.songListCount(0);
    };

    self.showModal = function (name, songListParams) {
        self.resetModal();
        self.modalName(name);
        self.songListParams(songListParams);

        var $modal = $("#song-list");
        self.isLoading(true);
        const modal = new bootstrap.Modal($modal.get(0));
        modal.show();
        songListParams.songs_per_page = 100;
        $.ajax({
            method: 'GET',
            url: reverse('song_list'),
            data: _.extend({
                active_playlist_name: self.activePlaylistName(),
            }, songListParams),
            success: function (data) {
                self.isLoading(false);
                self.modalSongs(_.map(data.items, SongModel));
                self.songListCount(data.items.length);
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
                    self.resetModal();
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
    document.querySelectorAll(".choices-js").forEach(e => {
        const data = e.dataset;
        let widget = new Choices(e, {
            itemSelectText: "",
        });
        if (data.url) {
            $.ajax({
                method: 'GET',
                url: reverse(data.url),
                success: function (items) {
                    widget.setChoices(items.items, 'id', 'text');
                },
            });
        }
    });
});
