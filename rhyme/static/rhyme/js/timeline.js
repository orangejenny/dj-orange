function rhymeStatsTimelineModel(options) {
    options.init = false;
    var self = rhymeStatsModel(options);

    self.seasonIndex = ['winter', 'spring', 'summer', 'autumn'];
    self.xAxisMargin = 20;
    self.selector = ".chart-container";
    self.svg = d3.select(self.selector + " svg");

    self.getSelectionFilter = function (selection) {
        var filters = _.uniq(_.map(selection.data(), function (s) { return "tag=" + s.year + (s.season ? "," + self.seasonIndex[s.season] : ""); }));
        if (filters.length > 1) {
            alert("TODO: handle multiple bars");
        }
        return filters[0];
    };

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
                self.drawAxes(data);
                self.attachTooltip(self.selector + " g");
                self.attachSelectionHandlers(self.selector + " g");
            },
        });
    };

    self.setDimensions = function () {
        self.width = $(self.selector).width();
        self.height = self.width / 3;
        self.svg.attr("width", self.width)
        self.svg.attr("height", self.height);
    };

    self.drawAxes = function (data) {
        self.xAxis = d3.axisBottom(self.getXScale(data))
                       .scale(self.getXScale(data))
                       .tickFormat(function(y) { return parseInt(y); })
                       .tickValues(_.map(_.range(self.getMinYear(data), self.getMaxYear(data) + 1), function(y) { return y + .5; }));
        self.svg.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0," + (self.height - self.xAxisMargin) + ")")
                .call(self.xAxis);
        self.svg.selectAll(".axis text").attr("y", 2);
    };

    self.getMaxYear = function(data) {
        const allYears = _.pluck(data, 'year').sort();
        return +allYears[allYears.length - 1];
    };

    self.getMinYear = function(data) {
        const allYears = _.pluck(data, 'year').sort();
        return +allYears[0];
    };

    self.getXScale = function(data) {
        var scale = d3.scaleLinear().range([0, self.width]);
        scale.domain([self.getMinYear(data), self.getMaxYear(data) + 1]);
        return scale;
    };

    self.getYScale = function(data) {
        var scale = d3.scaleLinear().range([0, self.height - self.xAxisMargin]);
        scale.domain([_.reduce(data, function(memo, d) { return Math.max(memo, d.count); }, 0), 0]);
        return scale;
    };

    self.drawBars = function (data) {
        const minYear = self.getMinYear(data),
            maxYear = self.getMaxYear(data),
            barSize = self.width / (maxYear - minYear + 1);
        let bars = self.svg.selectAll("g")
                                    .data(data)
                                    .enter().append("g")
                                    .attr("transform", function(d, i) {
                                        return "translate(" + self.getXScale(data).call(null, d.year) + ", 0)";
                                    });
        bars.append("rect")
                .attr("x", function(d) { return d.season === undefined ? 0 : d.season * (barSize / 4); })
                .attr("y", function(d) { return self.getYScale(data).call(null, d.count); })
                .attr("width", function(d) { return d.season === undefined ? barSize - 2 : (barSize - 8) / 4; })
                .attr("height", function(d) { return self.height - self.xAxisMargin - self.getYScale(data).call(null, d.count); })
                .style("opacity", function(d) { return d.season === undefined ? 0.25 : 1; });
    };

    self.reformatData = function(data) {
        const yearData = [];
        const seasonData = [];

        for (year in data) {
            let yearCount = 0;
            for (season in data[year]) {
                const seasonCount = data[year][season],
                    text = year + " " + season;
                seasonData.push({
                    year: +year,
                    season: self.seasonIndex.indexOf(season),
                    count: seasonCount,
                    description: seasonCount + " " + text + " " + pluralize(seasonCount.count, "song"),
                    filename: text,
                });
                yearCount += seasonCount;
            }
            yearData.push({
                year: +year,
                count: yearCount,
                description: yearCount + " " + year + " " + pluralize(yearCount, "song"),
                filename: year,
            });
        }

        return yearData.concat(seasonData);
    };

    self.refresh();

    return self;
}

$(function() {
    var model = rhymeStatsTimelineModel({
        model: 'song',
        url: reverse('timeline_json'),
    });
    ko.applyBindings(model);
});
