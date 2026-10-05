function rhymeStatsAcquisitionsModel(options) {
    options.init = false;
    var self = rhymeStatsModel(options);

    self.xAxisMargin = 20;
    self.barMargin = 0;
    self.selector = ".chart-container";
    self.svg = d3.select(self.selector + " svg");

    self.getSelectionFilter = function (selection) {
        return _.uniq(_.flatten(_.pluck(selection.data(), 'filter'))).join("||");
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
        const barSize = self.getBarSize(self.getMinMonthCount(data), self.getMaxMonthCount(data)),
            minYear = d3.min(_.pluck(data, "date")).getFullYear(),
            maxYear = d3.max(_.pluck(data, "date")).getFullYear(),
            xScale = d3.scaleLinear().range([0, self.width]).domain([minYear, maxYear + 1]);
        self.xAxis = d3.axisBottom(xScale)
                        .tickValues(_.map(_.range(minYear, maxYear + 1), function(t) { return t + 0.5; }))
                        .tickFormat(function(t) { return Math.floor(t); });

        self.svg.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0," + (self.height - self.xAxisMargin) + ")")
                .call(self.xAxis);
        self.svg.selectAll(".axis text").attr("y", 2);
    };

    self.getBarSize = function(minMonthCount, maxMonthCount) {
        return self.width / (maxMonthCount - minMonthCount + 1) - self.barMargin;
    };

    self.getMaxYear = function(data) {
        const allYears = _.pluck(data, 'year').sort();
        return +allYears[allYears.length - 1];
    };

    self.getMinYear = function(data) {
        const allYears = _.pluck(data, 'year').sort();
        return +allYears[0];
    };

    self.getMaxMonthCount = function(data) {
        return self.getMinMonthCount(data) + 12;
    };

    self.getMinMonthCount = function(data) {
        return d3.min(_.pluck(data, "date")).getFullYear() * 12;
    };

    self.getYScale = function(data) {
        var scale = d3.scaleLinear().range([0, self.height - self.xAxisMargin]);
        scale.domain([0, d3.max(_.pluck(data, 'count'))]);
        return scale;
    };

    self.drawBars = function (data) {
        const minYear = self.getMinYear(data),
            maxYear = self.getMaxYear(data),
            barSize = self.width / (maxYear - minYear + 1);
        // TODO
        /*let bars = self.svg.selectAll("g")
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
                .style("opacity", function(d) { return d.season === undefined ? 0.25 : 1; });*/
    };

    self.reformatData = function(data) {
        var dateFormat = d3.timeFormat("%b %Y");
        var dataAsList = []
        for (monthYear in data) {
            const date = new Date(monthYear + "-15"),
                text = dateFormat(date),
                count = data[monthYear],
                monthYearParts = monthYear.split("-");

            let thisYear = monthYearParts[0],
                thisMonth = parseInt(monthYearParts[1]);
            if (thisMonth === 12) {
                thisMonth = 1;
                thisYear += 1;
            } else {
                thisMonth += 1;
            }
            if (thisMonth < 10) {
                thisMonth = "0" + thisMonth;
            }

            dataAsList.push({
                date: date,
                month: date.getMonth() + 1,
                year: date.getFullYear(),
                count: count,
                filter: "date_acquired>=" + monthYear + "&&date_acquired<=" + [thisYear, thisMonth].join("-"),
                filename: "acquired " + text,
                description: text + "\n" + count + pluralize(count, " song"),
            });
        }
        var minMonthCount = self.getMinMonthCount(dataAsList);

        dataAsList = _.map(dataAsList, function(d) {
            return _.extend(d, {
                monthCount: d.date.getFullYear() * 12 + d.date.getMonth() - minMonthCount,
            });
        });

        return dataAsList;
    };

    self.refresh();

    return self;
}

$(function() {
    var model = rhymeStatsAcquisitionsModel({
        model: 'song',
        url: reverse('acquisitions_json'),
    });
    ko.applyBindings(model);
});
