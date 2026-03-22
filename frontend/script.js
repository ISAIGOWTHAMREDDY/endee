document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    const kSlider = document.getElementById('kSlider');
    const kValue = document.getElementById('kValue');
    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('resultsContainer');

    kSlider.addEventListener('input', (e) => {
        kValue.textContent = e.target.value;
    });

    const performSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        // UI State
        resultsContainer.innerHTML = '';
        loading.classList.remove('hidden');
        searchBtn.disabled = true;

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query, k: parseInt(kSlider.value) })
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();
            renderResults(data);
        } catch (error) {
            console.error(error);
            resultsContainer.innerHTML = `
                <div class="result-card">
                    <div class="result-title" style="color:#ef4444; margin-bottom: 0.5rem;"><i class="fa-solid fa-triangle-exclamation"></i> Search Connection Error</div>
                    <p class="result-abstract">${error.message}</p>
                </div>`;
        } finally {
            loading.classList.add('hidden');
            searchBtn.disabled = false;
        }
    };

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    function renderResults(data) {
        if (!data || !data.results || data.results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="result-card" style="text-align: center; color: var(--text-muted)">
                    <i class="fa-solid fa-folder-open" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <h3 style="font-size: 1.2rem; font-weight: 500; color: white;">No optimal matches found</h3>
                    <p style="margin-top: 0.5rem">Consider re-phrasing your search or reducing the top-k threshold.</p>
                </div>
            `;
            return;
        }

        const html = data.results.map((result, index) => {
            let meta = { title: "Unknown", authors: "N/A", abstract: "No abstract available" };
            try { 
                meta = JSON.parse(result.meta); 
            } catch (e) {
                console.warn("Could not parse meta", result.meta);
            }

            return `
                <div class="result-card" style="animation-delay: ${index * 0.1}s">
                    <div class="result-header">
                        <div class="result-title">${meta.title || meta.name || 'Untitled Paper'}</div>
                        <div class="result-score" title="Cosine similarity score"><i class="fa-solid fa-bullseye"></i> ${(result.score).toFixed(4)}</div>
                    </div>
                    <div class="result-meta">
                        <span><i class="fa-solid fa-users"></i> ${meta.authors || 'Unknown Authors'}</span>
                        <span><i class="fa-solid fa-fingerprint"></i> ${result.id}</span>
                    </div>
                    <div class="result-abstract">
                        ${meta.abstract || meta.description || 'No description available for this document.'}
                    </div>
                </div>
            `;
        }).join('');

        resultsContainer.innerHTML = html;
    }
});
