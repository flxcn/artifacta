(async function() {
    const terms = ["JavaScript", "Python", "Artificial Intelligence", "Machine Learning"]; // Add more key terms
    const baseUrl = "https://en.wikipedia.org/wiki/";

    function getWikipediaUrl(term) {
        return fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(term)}`)
            .then(response => response.ok ? baseUrl + encodeURIComponent(term) : null);
    }

    async function hyperlinkTerms() {
        const bodyText = document.body.innerHTML;
        let updatedText = bodyText;

        for (const term of terms) {
            const wikiUrl = await getWikipediaUrl(term);
            if (wikiUrl) {
                const regex = new RegExp(`\\b(${term})\\b`, "gi");
                updatedText = updatedText.replace(regex, `<a href="${wikiUrl}" target="_blank">$1</a>`);
            }
        }
        
        document.body.innerHTML = updatedText;
    }

    hyperlinkTerms();
})();
