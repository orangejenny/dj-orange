document.querySelectorAll('.playlist-checkbox').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        this.closest('tr').classList.toggle('table-active', this.checked);
        updateExportCount();
    });
});

document.querySelectorAll('.playlist-checkbox-cell').forEach(function(cell) {
    cell.addEventListener('click', function(e) {
        if (e.target.type !== 'checkbox') {
            var checkbox = this.querySelector('.playlist-checkbox');
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event('change'));
        }
    });
});

function updateExportCount() {
    var count = document.querySelectorAll('.playlist-checkbox:checked').length;
    document.getElementById('export-count').textContent = count;
}

function exportCheckedPlaylists(config) {
    var rows = Array.from(document.querySelectorAll('.playlist-checkbox:checked'))
        .map(function(cb) { return cb.closest('tr'); });
    if (!rows.length) {
        alert('No playlists selected.');
        return;
    }
    var ids = rows.map(function(row) { return row.dataset.id; }).join(',');
    var firstName = rows[0].dataset.name;
    ExportPlaylist({
        config: config,
        model: 'song',
        playlist_ids: ids,
        filename: firstName,
    });
}

document.querySelectorAll('.playlist-export-cell').forEach(function(cell) {
    cell.addEventListener('click', function() {
        var row = this.closest('tr');
        ExportPlaylist({
            config: this.dataset.config,
            model: 'song',
            song_filters: row.dataset.songFilters,
            album_filters: row.dataset.albumFilters,
            omni_filter: row.dataset.omniFilter,
            filename: row.dataset.name,
        });
    });
});

document.getElementById('playlist-filter').addEventListener('keyup', function() {
    var query = this.value.toLowerCase();
    document.querySelectorAll('tbody tr[data-id]').forEach(function(row) {
        var name = row.dataset.name.toLowerCase();
        var filters = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
        row.style.display = (name.includes(query) || filters.includes(query)) ? '' : 'none';
    });
});

document.querySelectorAll('.delete-playlist').forEach(function(el) {
    el.addEventListener('click', function(e) {
        e.preventDefault();
        var name = this.dataset.name;
        var url = this.dataset.url;
        var row = this.closest('tr');
        if (!confirm('Delete playlist "' + name + '"?')) return;
        fetch(url, {
            method: 'POST',
            headers: {'X-CSRFToken': $("#csrf-token").find("input").val()},
        }).then(function(r) {
            if (r.ok) row.remove();
        });
    });
});
