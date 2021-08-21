// Modified from https://bl.ocks.org/mbostock/4062045
$(document).ready(function() {
    // TODO: add song filters
    // TODO: add view/export modal
    $("#network-controls .btn").click(draw);
    draw();
});

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

function draw() {
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
    console.log("sent => " + category);    // TODO: spinner
    $.ajax({
        method: 'GET',
        url: reverse('network_json'),
        data: {
            category: category,
            strength: strength,
        },
        success: function(data) {
            console.log("got");
            data.nodes = _.map(data.nodes, function(node) {
                return _.extend(node, {
                    count: +node.count,
                    condition: condition([node.id]),
                    filename: filename([node.id]),
                });
            });

            var simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink().id(function(d) { return d.id; }))
                .force("charge", d3.forceManyBody())
                .force("center", d3.forceCenter(width / 2, height / 2));

            data.links = _.map(data.links, function(link) {
                return _.extend(link, {
                    condition: condition([link.source, link.target]),
                    filename: filename([link.source, link.target]),
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
            var node = svg.append("g")
                          .attr("class", "nodes")
                          .selectAll("circle")
                          .data(data.nodes)
                          .enter().append("circle")
                                  .attr("r", function(n) { return rScale(n.count); })
                                  .call(d3.drag()
                                          .on("start", function(d) { dragStarted(d, simulation); })
                                          .on("drag", function(d) { dragged(d, simulation); })
                                          .on("end", function(d) { dragEnded(d, simulation); }));
        
            simulation.nodes(data.nodes)
                      .on("tick", function() { ticked(link, node); });
            simulation.force("link").links(data.links);
        
            attachTooltip(selector + " g circle, " + selector + " g line");
            attachSelectionHandlers(selector + " g circle, " + selector + " g line");
        },
    });
}
