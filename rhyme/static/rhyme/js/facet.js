function rhymeStatsFacetModel(options) {
    options.init = false;
    var self = rhymeStatsModel(options);
    self.selector = ".chart-container";
    self.facet = document.querySelector(self.selector).dataset.facet;
    self.svg = d3.select(self.selector + " svg");

    console.log("facet = " + self.facet);

    return self;
}

$(function() {
    var model = rhymeStatsFacetModel({
        model: 'song',
        url: reverse('facet_json') + '?facet=' + self.facet,
    });
    ko.applyBindings(model);
});
