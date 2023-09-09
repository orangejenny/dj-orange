/*
 * AssertArgs
 *
 * Description: Verify the presence of given properties in given object.
 * Parameters
 *    args: An object to check
 *    required: An array of strings that must be truthy properties of the object
 *  optional: An array of strings that may be falsy or not present
 */
function AssertArgs(args, required, optional) {
    if (!args) {
        args = {};
    }
    _.each(required, function(r) {
        if (_.isUndefined(args[r])) {
            throw("Missing argument in AssertArgs: " + r);
        }
    });
    var unexpected = _.keys(_.omit(args, required.concat(optional)));
    if (unexpected.length) {
        throw("Unexpected arguments in AssertArgs: " + unexpected.join(", "));
    }
}

function reverse(name) {
    return $("#rhyme-urls").find("[data-name='" + name + "']").data("url");
}

/*
 * StringMultiply
 *
 * Description: Python-style string multiplication
 *
 * Args
 *    String to manipulate and number of times to repeat it (non-negative integer)
 */
function StringMultiply(string, factor) {
    var returnValue = "";
    for (var i = 0 ; i < factor; i++) {
        returnValue += string;
    }
    return returnValue;
}

function ExportPlaylist(data) {
    data.filename = prompt("Playlist name?", data.filename || "rhyme");
    if (!data.filename) {
        return;
    }

    var params = [];
    for (var key in data) {
        var value = data[key] ? encodeURIComponent(data[key]) : '';
        params.push(key + '=' + value);
    }

    var url = reverse(data.model === "album" ? 'album_export' : 'song_export') + '?' + params.join('&');
    if (["plex", "rhyme"].find((x) => x === data.config)) {
        $.get(url, function (data) {
            alert("Playlist exported. " + JSON.stringify(data));
        });
    } else {
        document.location = url;
    }
}
