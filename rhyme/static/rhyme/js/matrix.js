function rhymeStatsMatrixModel(options) {
    options.init = false;
    var self = rhymeStatsModel(options);
    self.range = 5;
    self.selector = ".chart-container";
    self.svg = d3.select(self.selector + " svg");

    self.getSelectionFilter = function (selection) {
        var conditions = _.uniq(_.map(selection.data(), function (s) { return "mood=" + s.mood + "&&energy=" + s.energy; }));
        if (conditions.length > 1) {
            alert("TODO: handle multiple bubbles");
        }
        return conditions[0];
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
                self.drawAxes();
                var bubbles = self.drawBubbles(data);
                self.drawLabels(bubbles);
                self.attachTooltip(self.selector + " g");
                self.attachSelectionHandlers(self.selector + " g");
            },
        });
    };

    self.setDimensions = function () {
        self.width = $(self.selector).width();
        self.height = self.width;
        self.bubbleSize = self.width / (self.range + 1);
        self.svg.attr("width", self.width)
        self.svg.attr("height", self.height);
    };

    self.drawAxes = function () {
        self.svg.append("line")
                .attr("class", "axis")
                .attr("x1", 0)
                .attr("y1", self.height / 2)
                .attr("x2", self.width)
                .attr("y2", self.height / 2);
        self.svg.append("line")
                .attr("class", "axis")
                .attr("x1", self.width / 2)
                .attr("y1", 0)
                .attr("x2", self.width / 2)
                .attr("y2", self.height);
    };

    self.drawBubbles = function (data) {
        var scale = self.getScale(data);
        var margin = self.bubbleSize / 2;
        var bubbles = self.svg.selectAll("g")
                                    .data(data)
                                    .enter().append("g")
                                    .attr("transform", function(d, i) {
                                        var x = self.bubbleSize * (d.energy - 1) + margin;
                                        var y = self.bubbleSize * (self.range - d.mood) + margin;
                                        return "translate(" + x + ", " + y + ")";
                                    });
    
        bubbles.append("circle")
                    .attr("cx", self.bubbleSize / 2)
                    .attr("cy", self.bubbleSize / 2)
                    .attr("r", function(d) { return scale(d.count) / 2; });
        return bubbles;
    };

    self.drawLabels = function (bubbles) {
        bubbles.append("text")
                    .attr("x", self.bubbleSize / 2)
                    .attr("y", self.bubbleSize / 2)
                    .attr("dy", "0.35em")
                    .text(function(d) { return d.count || ""; });
    };

    self.getScale = function (data) {
        var scale = d3.scaleLinear().range([0, self.bubbleSize * 2]);
        scale.domain([0, _.max(_.pluck(data, 'count'))]);
        return scale;
    };

    self.reformatData = function(data) {
        var moodDescriptions = ['very unhappy', 'unhappy', 'neutral', 'happy', 'very happy'];
        var energyDescriptions = ['very slow', 'slow', 'medium tempo', 'energetic', 'very energetic'];
        var bubbles = [];
        for (e = 1; e <= self.range; e++) {
            for (m = 1; m <= self.range; m++) {
                var relevant = _.filter(data, function(d) {
                    return d.energy == e && d.mood == m;
                });
                var bubble = {
                    energy: e,
                    mood: m,
                    count: _.reduce(relevant, function(memo, d) {
                        return memo + +d.count;
                    }, 0),
                    condition: 'mood=' + m + ' and energy=' + e,
                    filename: [moodDescriptions[m - 1], energyDescriptions[e - 1]].join(" "),
                };
                bubble.description = bubble.count + " " + bubble.filename + " " + pluralize(bubble.count, "song");
                bubbles.push(bubble);
            }
        }
        bubbles = _.sortBy(bubbles, 'count').reverse();
        return bubbles;
    };

    self.refresh();

    return self;
}

$(function() {
    var model = rhymeStatsMatrixModel({
        model: 'song',
        url: reverse('matrix_json'),
    });
    ko.applyBindings(model);
});
