(function () {
	var searchInput = document.getElementById('mm-search');
	var seriesFilter = document.getElementById('mm-series-filter');
	var rows = Array.prototype.slice.call(document.querySelectorAll('.catalog-row'));
	var emptyState = document.getElementById('mm-empty-state');
	var countEl = document.querySelector('[data-count]');

	if (!searchInput || !seriesFilter) return;

	function applyFilters() {
		var q = searchInput.value.trim().toLowerCase();
		var series = seriesFilter.value;
		var visible = 0;
		rows.forEach(function (row) {
			var matchesSearch = !q || (row.dataset.search || '').indexOf(q) !== -1;
			var matchesSeries = !series || (row.dataset.series || '').split('|').indexOf(series) !== -1;
			var show = matchesSearch && matchesSeries;
			row.hidden = !show;
			if (show) visible++;
		});
		if (emptyState) emptyState.hidden = visible !== 0;
		if (countEl) countEl.textContent = visible + ' sermon' + (visible === 1 ? '' : 's');
	}

	searchInput.addEventListener('input', applyFilters);
	seriesFilter.addEventListener('change', applyFilters);
})();
