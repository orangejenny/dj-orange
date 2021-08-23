// Modified from https://bl.ocks.org/mbostock/4062045
function dragStarted(d, simulation) {
    if (!d3.event.active) {
        simulation.alphaTarget(0.3).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d, simulation) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragEnded(d, simulation) {
    if (!d3.event.active) {
        simulation.alphaTarget(0);
    }
    d.fx = null;
    d.fy = null;
}

function ticked(link, node) {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
}

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

    self.refresh = function () {
        var condition = function(tags) {
            return _.map(_.uniq(_.compact(tags)), function(t) { return "taglist like '% " + t + " %'" }).join(" and ");
        };
        var filename = function(tags) {
            return _.map(_.uniq(_.compact(tags)), function(t) { return "[" + t + "]"; }).join("");
        };
        var selector = ".chart-container",
            svg = d3.select(selector + " svg"),
            width = +svg.attr("width"),
            height = +svg.attr("height");

        svg.html("");
        svg.attr("viewBox", [0, 0, width, height]);

        var $filters = $("#network-controls"),
            category = $filters.find("[name='category']").val();
            strength = $filters.find("[name='strength']").val();
        self.isLoading(true);
        $.ajax({
            method: 'GET',
            url: self.url,
            data: $.extend({
                category: category,
                strength: strength,
            }, self.serializeFilters()),
            success: function(data) {
                self.isLoading(false);
                data.nodes = _.map(data.nodes, function(node) {
                    return _.extend(node, {
                        count: +node.count,
                        tags: [node.name],
                        filename: filename([node.name]),
                    });
                });
                var nodesById = _.indexBy(data.nodes, "id"),
                    nodeNameById = function (id) {
                        return nodesById[id].name;
                    };


                var simulation = d3.forceSimulation(data.nodes)
                    .force("link", d3.forceLink().id(function(d) { return d.id; }))
                    .force("charge", d3.forceManyBody().strength(-100))
                    .force("center", d3.forceCenter(width / 2, height / 2));

                data.links = _.map(data.links, function(link) {
                    return _.extend(link, {
                        tags: [nodeNameById(link.source), nodeNameById(link.target)],
                        filename: filename([nodeNameById(link.source), nodeNameById(link.target)]),
                    });
                });

                var link = svg.append("g")
                              .attr("class", "links")
                              .selectAll("line")
                              .data(data.links)
                              .enter().append("line")
                                      .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

                var count = function(n) { return n.count; },
                    rScale = d3.scaleLinear()
                               .range([5, 15])
                               .domain([d3.min(data.nodes, count), d3.max(data.nodes, count)]);
                var myColor = d3.scaleSequential().domain([1, _.max(_.pluck(data.nodes, 'category'))]).interpolator(d3.interpolateViridis);
                var node = svg.append("g")
                              .attr("class", "nodes")
                              .selectAll("circle")
                              .data(data.nodes)
                              .enter().append("circle")
                                      .attr("r", function(n) { return rScale(n.count); })
                                      .attr("fill", function(d){return myColor(d.category)})
                                      .call(d3.drag()
                                              .on("start", function(d) { dragStarted(d, simulation); })
                                              .on("drag", function(d) { dragged(d, simulation); })
                                              .on("end", function(d) { dragEnded(d, simulation); }));

                simulation.nodes(data.nodes)
                          .on("tick", function() { ticked(link, node); });
                simulation.force("link").links(data.links);

                self.attachTooltip(selector + " g circle, " + selector + " g line");
                self.attachSelectionHandlers(selector + " g circle, " + selector + " g line");
            },
        });
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
    self.refresh();

    return self;
}

$(function() {
    var model = rhymeStatsModel({
        model: 'song',
        url: reverse('network_json'),
    });
    ko.applyBindings(model);
});
