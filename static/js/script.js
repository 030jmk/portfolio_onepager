const caseModal = document.getElementById('caseModal');
const caseModalLabel = document.getElementById('caseModalLabel');
const challenge = document.getElementById('challenge');
const solution = document.getElementById('solution');
const benefit = document.getElementById('benefit');
const subdomain = document.getElementById('subdomain');
const process = document.getElementById('process');
const technologies = document.getElementById('technologies');
const industries = document.getElementById('industries');

const subdomainFilters = document.querySelectorAll('#subdomain-filters input[type="checkbox"]');
const industryFilters = document.querySelectorAll('#industry-filters input[type="checkbox"]');
const technologyFilters = document.querySelectorAll('#technology-filters input[type="checkbox"]');
const searchInput = document.getElementById('search-input');
const clearFiltersButton = document.getElementById('clear-filters');
const activeFiltersText = document.getElementById('active-filters-text');

caseModal.addEventListener('show.bs.modal', event => {
    const card = event.relatedTarget;
    const caseData = JSON.parse(card.getAttribute('data-case'));

    caseModalLabel.textContent = caseData.name;
    challenge.textContent = caseData.Challenge;
    solution.textContent = caseData.solution;
    benefit.textContent = caseData.benefit;
    subdomain.textContent = caseData.subdomain;
    process.textContent = caseData.process;

    technologies.innerHTML = '';
    caseData.technologies
        .filter(tech => tech.value > 0)  // Only show technologies with value > 0
        .forEach(tech => {
            const li = document.createElement('li');
            li.textContent = tech.name;   // Use the name property
            technologies.appendChild(li);
        });

    industries.innerHTML = '';
    caseData.industries
        .filter(ind => ind.value > 0)    // Only show industries with value > 0
        .forEach(ind => {
            const li = document.createElement('li');
            li.textContent = ind.name;    // Use the name property
            industries.appendChild(li);
        });
});

function updateCards(filteredCases) {
    const caseCards = document.getElementById('case-cards');
    caseCards.innerHTML = '';
    if (filteredCases.length === 0) {
        const col = document.createElement('div');
        col.className = 'col';

        const card = document.createElement('div');
        card.className = 'card bg-dark text-white';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const text = document.createElement('p');
        text.className = 'card-text';
        text.textContent = 'No use cases found.';

        cardBody.appendChild(text);
        card.appendChild(cardBody);
        col.appendChild(card);
        caseCards.appendChild(col);
    } else {
        filteredCases.forEach(caseData => {
            const col = document.createElement('div');
            col.className = 'col';

            const card = document.createElement('div');
            card.className = 'card bg-dark text-white h-100'; // Added h-100 for consistent height
            card.setAttribute('data-bs-toggle', 'modal');
            card.setAttribute('data-bs-target', '#caseModal');
            card.setAttribute('data-case', JSON.stringify(caseData));
            card.style.cursor = 'pointer';

            const cardBody = document.createElement('div');
            cardBody.className = 'card-body d-flex flex-column';

            const title = document.createElement('h5');
            title.className = 'card-title mb-3';
            title.textContent = caseData.name;

            const pillsContainer = document.createElement('div');
            pillsContainer.className = 'mt-auto d-flex gap-2 flex-wrap';

            const subdomainPill = document.createElement('span');
            subdomainPill.className = 'badge rounded-pill bg-success';
            subdomainPill.textContent = caseData.subdomain;

            const processPill = document.createElement('span');
            processPill.className = 'badge rounded-pill bg-secondary';
            processPill.textContent = caseData.process;

            pillsContainer.appendChild(subdomainPill);  // Subdomain first
            pillsContainer.appendChild(processPill);    // Process second

            cardBody.appendChild(title);
            cardBody.appendChild(pillsContainer);
            card.appendChild(cardBody);
            col.appendChild(card);
            caseCards.appendChild(col);
        });
    }
}

function filterCases() {
    const selectedSubdomains = Array.from(subdomainFilters)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

    const selectedIndustries = Array.from(industryFilters)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

    const selectedTechnologies = Array.from(technologyFilters)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

    const searchTerm = searchInput.value.trim();
    
    const params = new URLSearchParams();
    
    selectedSubdomains.forEach(value => params.append('subdomains', value));
    selectedIndustries.forEach(value => params.append('industries', value));
    selectedTechnologies.forEach(value => params.append('technologies', value));
    
    if (searchTerm) {
        params.append('search', searchTerm);
    }

    const url = '/filter' + (params.toString() ? '?' + params.toString() : '');

    fetch(url)
        .then(response => response.json())
        .then(filteredCases => {
            updateCards(filteredCases);
            updateActiveFilters(selectedSubdomains, selectedIndustries, selectedTechnologies, searchTerm);
        })
        .catch(error => console.error(error));
}

function updateActiveFilters(selectedSubdomains, selectedIndustries, selectedTechnologies, searchTerm) {
    const activeFilters = [];

    if (selectedSubdomains.length > 0) {
        activeFilters.push(`Subdomains: ${selectedSubdomains.join(', ')}`);
    }

    if (selectedIndustries.length > 0) {
        activeFilters.push(`Industries: ${selectedIndustries.join(', ')}`);
    }

    if (selectedTechnologies.length > 0) {
        activeFilters.push(`Technologies: ${selectedTechnologies.join(', ')}`);
    }

    if (searchTerm) {
        activeFilters.push(`Search: ${searchTerm}`);
    }

    activeFiltersText.textContent = activeFilters.join(' | ') || 'No filters applied';
}

function clearFilters() {
    subdomainFilters.forEach(checkbox => checkbox.checked = false);
    industryFilters.forEach(checkbox => checkbox.checked = false);
    technologyFilters.forEach(checkbox => checkbox.checked = false);
    searchInput.value = '';
    filterCases();
}

subdomainFilters.forEach(checkbox => checkbox.addEventListener('change', filterCases));
industryFilters.forEach(checkbox => checkbox.addEventListener('change', filterCases));
technologyFilters.forEach(checkbox => checkbox.addEventListener('change', filterCases));
searchInput.addEventListener('input', filterCases);
clearFiltersButton.addEventListener('click', clearFilters);

// Fetch and render all use cases on page load
fetch('/filter')
    .then(response => response.json())
    .then(data => {
        updateCards(data);
    })
    .catch(error => console.error(error));

let inactivityTimer;
const TIMEOUT = 600000; // 600000 - 10 minutes in milliseconds

function resetTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
        // Clear filters before reload
        localStorage.clear(); // Clear any stored filter states
        clearFilters(); // Clear UI filters
        window.location.href = window.location.pathname; // Reload to base URL without query parameters
    }, TIMEOUT);
}

// User activity events to monitor
const events = [
    'mousedown',
    'mousemove',
    'keypress',
    'scroll',
    'touchstart',
    'click'
];

// Add event listeners for all tracked events
events.forEach(event => {
    document.addEventListener(event, resetTimer, true);
});

// Initial setup of timer when page loads
resetTimer();

// Clear filters when page loads if it was a reload
window.addEventListener('load', () => {
    if (performance.navigation.type === 1) { // Check if it's a reload
        clearFilters();
    }
});
