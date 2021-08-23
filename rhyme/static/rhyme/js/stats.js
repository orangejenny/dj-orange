function rhymeStatsModel(options) {
    options.init = false;
    var self = rhymeModel(options);

    self.viewSelection = function () {
        self.showModal(
            self.getSelectionFilename(d3.selectAll("svg .selected")),
            self.serializeFilters(d3.selectAll("svg .selected"))
        );
    };

    self.hideModal = function () {
        d3.selectAll('svg .selected').classed("selected", false);
        self.setClearVisibility();
        return true;
    };

    var super_serializeFilters = self.serializeFilters;
    self.serializeFilters = function (selection) {
        var filters = super_serializeFilters(),
            selectionFilter = self.getSelectionFilter(selection);
        if (!selectionFilter) {
            return filters;
        }
        if (filters.song_filters) {
            filters.song_filters += "&&" + selectionFilter;
        } else {
            filters.song_filters = selectionFilter;
        }
        return filters;
    };

    self.getSelectionFilter = function (selection) {
        if (!selection) {
            return '';
        }
        return "tag=" + _.uniq(_.flatten(_.pluck(selection.data(), 'tags'))).join(",");
    };

    self.getSelectionFilename = function (selection) {
        var filenames = _.uniq(_.pluck(selection.data(), 'filename'));
        if (filenames.length === 1) {
            return filenames[0];
        }
        return "";
    }

    self.clearSelection = function () {
        d3.selectAll(".selected").classed("selected", false);
        self.setClearVisibility();
    };

    self.setClearVisibility = function () {
        if ($("svg .selected").length) {
            $(".selection-buttons").removeClass("hide");
        } else {
            $(".selection-buttons").addClass("hide");
        }
    };

    self.attachTooltip = function (selector) {
        var positionTooltip = function() {
            var $tooltip = $("#tooltip");
            if (!$tooltip.is(":visible")) {
                return;
            }
            if (d3.event.pageX + 10 + $tooltip.width() > $("body").width()) {
                $tooltip.css("left", d3.event.pageX - $tooltip.width() - 10);
            }
            else {
                $tooltip.css("left", d3.event.pageX + 10);
            }
            if (d3.event.pageY + $tooltip.height() > $("body").height() - $(".post-nav").scrollTop()) {
                $tooltip.css("top", d3.event.pageY - $tooltip.height());
            }
            else {
                $tooltip.css("top", d3.event.pageY);
            }
        };

        d3.selectAll(selector).on("mouseenter.tooltip", function() {
            var data = d3.select(this).data()[0];
            var $tooltip = $("#tooltip");
            var show = false;

            $tooltip.html("");
            if (data.description) {
                show = true;
                var description = data.description;
                $tooltip.html(description);
            }

            if (show) {
                $tooltip.removeClass("hide");
                positionTooltip();
            }
        });
        d3.selectAll(selector).on("mouseleave.tooltip", function() {
            $("#tooltip").addClass("hide");
        });
        d3.selectAll(selector).on("mousemove.tooltip", function() {
            positionTooltip();
        });
    };

    self.attachSelectionHandlers = function (selector, actsOn) {
        if (!actsOn) {
            actsOn = function(obj) {
                return d3.select(obj);
            };
        }

        $(selector).css("cursor", "pointer");
        self.highlightOnHover(selector, actsOn);
        self.selectOnClick(selector, actsOn);
        self.viewOnDoubleClick(selector, actsOn);
    };

    self.highlightOnHover = function (selector, actsOn) {
        d3.selectAll(selector).on("mouseenter.highlight", function() {
            actsOn(this).classed("highlighted", true);
            actsOn(this).selectAll("rect, circle").classed("highlighted", true);
        });
        d3.selectAll(selector).on("mouseleave.highlight", function() {
            actsOn(this).classed("highlighted", false);
            actsOn(this).selectAll(".highlighted").classed("highlighted", false);
        });
    };

    self.viewOnDoubleClick = function (selector, actsOn) {
        d3.selectAll(selector).on("dblclick", function(e) {
            var obj = actsOn(this);
            self.showModal(
                self.getSelectionFilename(obj),
                self.serializeFilters(obj)
            );
            d3.event.preventDefault();
        });
    }

    self.selectOnClick = function (selector, actsOn) {
        d3.selectAll(selector).on("click", function() {
            self.selectData(actsOn(this));
        });
    };

    self.selectData = function (obj) {
        var isSelected = obj.classed("selected");
        obj.classed("selected", !isSelected);
        obj.selectAll("rect, circle").classed("selected", !isSelected);
        self.setClearVisibility();
    };

    // Initialize
    if (options.init || options.init === undefined) {
        self.refresh();
    }

    return self;
}
