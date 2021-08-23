function rhymeStatsMatrixModel(options) {
    options.init = false;
    var self = rhymeStatsModel(options);

    self.refresh = function () {
        self.isLoading(true);
        $.ajax({
            method: 'GET',
            url: self.url,
            data: self.serializeFilters(),
            success: function(data) {
                self.isLoading(false);
                console.log("got the bubbles");
            },
        });
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
