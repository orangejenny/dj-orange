$(function() {
    var $postNav = $(".post-nav"),
        $itemPage = $postNav.find(".item-page");

    var model = rhymeModel({
        model: document.location.href.indexOf("albums") == -1 ? 'song' : 'album',
        url: $itemPage.data("url"),
    });
    ko.applyBindings(model);

    // TODO: move to knockout
    $itemPage.scroll(function(e) {
        var overflowHeight = $itemPage.find(".infinite-scroll-container").height() - $itemPage.height()
        if ($itemPage.scrollTop() / overflowHeight > 0.8) {
            model.nextPage();
        }
    });
});
