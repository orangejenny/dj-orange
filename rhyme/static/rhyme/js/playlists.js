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
