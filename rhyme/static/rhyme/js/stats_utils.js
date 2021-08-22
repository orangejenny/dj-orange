$(document).ready(function() {
    $("#song-list").on("hide hide.bs.modal", function() {
        d3.selectAll('.selected').classed("selected", false);
        setClearVisibility();
    });
});

function setClearVisibility() {
    if ($(".selected").length) {
        $(".selection-buttons").removeClass("hide");
    }
    else {
        $(".selection-buttons").addClass("hide");
    }
}

function attachTooltip(selector) {
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
}

function attachSelectionHandlers(selector, actsOn) {
    if (!actsOn) {
        actsOn = function(obj) {
            return d3.select(obj);
        };
    }

    $(selector).css("cursor", "pointer");
    highlightOnHover(selector, actsOn);
    selectOnClick(selector, actsOn);
    viewOnDoubleClick(selector, actsOn);
}

function highlightOnHover(selector, actsOn) {
    d3.selectAll(selector).on("mouseenter.highlight", function() {
        actsOn(this).classed("highlighted", true);
        actsOn(this).selectAll("rect, circle").classed("highlighted", true);
    });
    d3.selectAll(selector).on("mouseleave.highlight", function() {
        actsOn(this).classed("highlighted", false);
        actsOn(this).selectAll(".highlighted").classed("highlighted", false);
    });
}

function selectOnClick(selector, actsOn) {
    d3.selectAll(selector).on("click", function() {
        selectData(actsOn(this));
    });
}

function selectData(obj) {
    var isSelected = obj.classed("selected");
    obj.classed("selected", !isSelected);
    obj.selectAll("rect, circle").classed("selected", !isSelected);
    setClearVisibility();
}

function viewOnDoubleClick(selector, actsOn) {
    d3.selectAll(selector).on("dblclick", function(e) {
        var obj = actsOn(this),
            data = obj.data()[0];
        var condition = data.condition;
        if (condition) {
            showSongModal({
                TITLE: data.filename,
                SUB: 'Flavors::Data::Song::List', 
                FILTER: augmentFilter(condition),
                SIMPLEFILTER: $("#filter").val(),
                STARRED: $("#simple-filter .fas.fa-star").length,
            }, function() {
                selectData(obj);
            });
        }
        d3.event.preventDefault();
    });
}

function getSelectionCondition() {
    var selected = d3.selectAll("svg .selected");
    if (!selected.data().length) {
        alert("Nothing selected");
        return '';
    }
    return _.map(_.uniq(_.pluck(selected.data(), 'condition')), function(c) { return "(" + c + ")"; }).join(" or ");
}; 
