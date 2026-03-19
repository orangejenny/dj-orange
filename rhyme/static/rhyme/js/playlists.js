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

var playlistPageModel = rhymeModel({model: 'song', init: false});
ko.applyBindings(playlistPageModel, document.getElementById('song-list'));

document.querySelectorAll('.playlist-name, .playlist-filters').forEach(function(cell) {
    cell.addEventListener('click', function() {
        var row = this.closest('tr');
        playlistPageModel.showModal(row.dataset.name, {playlist_id: row.dataset.id});
    });
});

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

var currentSortCol = null;
var currentSortDir = 1;

document.querySelectorAll('th[data-sort]').forEach(function(th) {
    th.addEventListener('click', function() {
        if (currentSortCol === this) {
            currentSortDir *= -1;
        } else {
            currentSortCol = this;
            currentSortDir = 1;
        }

        document.querySelectorAll('th[data-sort] .sort-indicator').forEach(function(el) {
            el.textContent = '';
        });
        this.querySelector('.sort-indicator').textContent = currentSortDir === 1 ? ' ▲' : ' ▼';

        var colIndex = this.cellIndex;
        var tbody = document.querySelector('tbody');
        var rows = Array.from(tbody.querySelectorAll('tr[data-id]'));
        rows.sort(function(a, b) {
            var aCell = a.cells[colIndex], bCell = b.cells[colIndex];
            var aVal = aCell.dataset.value !== undefined ? aCell.dataset.value : aCell.textContent.trim();
            var bVal = bCell.dataset.value !== undefined ? bCell.dataset.value : bCell.textContent.trim();
            var aNum = parseInt(aVal, 10), bNum = parseInt(bVal, 10);
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return currentSortDir * (aNum - bNum);
            }
            return currentSortDir * aVal.toLowerCase().localeCompare(bVal.toLowerCase());
        });
        rows.forEach(function(row) { tbody.appendChild(row); });
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
