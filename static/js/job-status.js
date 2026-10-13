(() => {
    const pending = [...document.querySelectorAll('[data-job-id]')].filter(
        node => ['pending', 'processing'].includes(node.dataset.jobStatus)
    );
    if (!pending.length) return;

    const groups = new Map();
    for (const node of pending) {
        const url = node.dataset.jobStatusUrl;
        if (!groups.has(url)) groups.set(url, []);
        groups.get(url).push(node);
    }

    let delay = 4000;
    async function poll() {
        if (document.hidden) {
            window.setTimeout(poll, delay);
            return;
        }
        try {
            for (const [endpoint, nodes] of groups) {
                const url = new URL(endpoint, window.location.origin);
                url.searchParams.set('ids', nodes.map(node => node.dataset.jobId).join(','));
                const response = await fetch(url, {
                    credentials: 'same-origin', cache: 'no-store',
                    signal: AbortSignal.timeout(10000),
                });
                if (!response.ok || response.redirected) throw new Error('Status unavailable');
                const data = await response.json();
                if (nodes.some(node => data.statuses[node.dataset.jobId] !== node.dataset.jobStatus)) {
                    window.location.reload();
                    return;
                }
            }
            delay = 4000;
        } catch {
            delay = Math.min(delay * 2, 30000);
        }
        window.setTimeout(poll, delay);
    }
    window.setTimeout(poll, delay);
})();
