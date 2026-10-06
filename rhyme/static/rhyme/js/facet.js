function rhymeStatsFacetModel(options) {
    options.init = false;
    var self = rhymeStatsModel(options);
    self.selector = ".chart-container";
    self.svg = d3.select(self.selector + " svg");

    self.facet = document.querySelector(self.selector).dataset.facet;
    self.icon = {
        'rating': 'star',
        'mood':  'heart',
        'energy': 'fire',
    }[self.facet]

    self.range = 5;    // number of bars
    self.barMargin = 10;
    self.barTextOffset = 4;

    self.getSelectionFilter = function (selection) {
        // TODO
    }

    self.refresh = function () {
        self.isLoading(true);
        $.ajax({
            method: 'GET',
            url: self.url,
            data: self.serializeFilters(),
            success: function(data) {
                self.isLoading(false);
                data = self.reformatData(data.stats);
                self.setDimensions();
                $(self.selector + " svg").empty();
                self.drawBars(data);
                self.drawLabels(data);
                self.attachTooltip(self.selector + " g");
                self.attachSelectionHandlers(self.selector + " g");
            },
        });
    };

    self.setDimensions = function () {
        self.width = $(self.selector).width();
        self.height = 250;
        self.svg.attr("width", self.width)
        self.svg.attr("height", self.height);
        self.barSize = self.width / self.range;
    };

    self.drawLabels = function (data) {
        // TODO
    }

    self.getYScale = function(data) {
        var scale = d3.scaleLinear().range([self.height, 0]);
        scale.domain([0, d3.max(_.pluck(data, 'count'))])
        return scale;
    };

    self.drawBars = function (data) {
        let bars = self.svg.selectAll("g")
                                    .data(data)
                                    .enter().append("g")
                                    .attr("transform", function(d, i) { return "translate(" + i * self.barSize + ", 0)"; });
        let yScale = self.getYScale(data);
        bars.append("rect")
                .attr("y", function(d) { return yScale(d.count); })
                .attr("width", self.barSize - self.barMargin)
                .attr("height", function(d) { return self.height - yScale(d.count); });
    }

    self.reformatData = function(data) {
        let dataAsList = [];
        _.each(_.range(1, 6), function (value) {
            const count = data[value];
            dataAsList.push({
                value: value,
                filter: self.facet + '=' + value,
                count: count,
                description: count + " " + _.map(_.range(value), x => "<span class='fas fa-" + self.icon + "'></span>").join(""),
            });
        });
        return dataAsList;
    }

    self.refresh();

    return self;
}

$(function() {
    var model = rhymeStatsFacetModel({
        model: 'song',
        url: reverse('facet_json') + '?facet=' + self.facet,
    });
    ko.applyBindings(model);
});
