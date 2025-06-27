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
        var contentHeight = _.reduce($(".item-page").children(), function (memo, child) { return memo + $(child).height(); }, 0),
            screenHeight = $itemPage.height();
        if (contentHeight - (screenHeight + $itemPage.scrollTop()) < 100) {     // 100 pixels from bottom, then scroll
            model.nextPage();
        }
    });
});
