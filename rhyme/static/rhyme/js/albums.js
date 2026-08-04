$(function() {
    var $albums = $('.albums');

    $albums.on('dragenter', '.cover-art', function(e) {
        e.preventDefault();
        $(this).closest('.album').find('.accepting-drop').show();
    });

    $albums.on('dragover', '.cover-art, .accepting-drop', function(e) {
        e.preventDefault();
    });

    $albums.on('dragleave', '.accepting-drop', function(e) {
        if (!$(this).closest('.album')[0].contains(e.relatedTarget)) {
            $(this).hide();
        }
    });

    $albums.on('drop', '.cover-art, .accepting-drop', function(e) {
        e.preventDefault();
        var $album = $(this).closest('.album');
        $album.find('.accepting-drop').hide();

        var file = e.originalEvent.dataTransfer.files[0];
        if (!file) return;

        var formData = new FormData();
        formData.append('image', file);
        formData.append('csrfmiddlewaretoken', $("#csrf-token").find("input").val());
        formData.append('album_id', $album.data('id'));

        $.ajax({
            method: 'POST',
            url: reverse('album_art_upload'),
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data.cover_art_filename) {
                    ko.dataFor($album[0]).cover_art_filename(data.cover_art_filename);
                }
            },
        });
    });
});
