$(document).ready(function() {
    loadLibrary();
    $('#searchQuery').keypress(function(event) {
        if (event.which === 13) {
            event.preventDefault();
            performSearch();
        }
    });
});

function performSearch() {
    let query = document.getElementById('searchQuery').value;
    $.ajax({
        type: 'POST',
        url: '/search',
        contentType: 'application/json',
        data: JSON.stringify({ query: query }),
        success: function(searchResults) {
            renderResults(searchResults, 'search-results');
        }
    });
}
function renderResults(results, tableId ) {
    const resultsContainer = document.getElementById(tableId);
    resultsContainer.innerHTML = ''; // Clear previous results

    // Create a table element
    let table = document.createElement('table');

    // Create the header row
    let headerRow = document.createElement('tr');

    // Define header titles and their respective widths
    const headers = [
        { title: 'Title', width: '30%' },
        { title: 'Author(s)', width: '30%' },
        { title: 'Genre(s)', width: '30%' },
        { title: ' ', width: '10%' }
    ];

    headers.forEach(header => {
        let th = document.createElement('th');
        th.innerText = header.title;
        th.style.width = header.width; // Apply the width
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Add rows for each result
    results.forEach(result => {
        let row = document.createElement('tr');
        row.innerHTML = `<td>${result.title}</td>
                         <td>${result.author}</td>
                         <td>${result.genre}</td>
                         <td><button onclick="goToReading(${result.id})">Select</button></td>`;
        table.appendChild(row);
    });

    // Append the table to the results container
    resultsContainer.appendChild(table);
}
function goToReading(id) {
    window.location.href = `reading.html?book_id=${id}`;
}

function loadLibrary() {
    $.ajax({
        type: 'GET',
        url: '/library',
        success: function(libraryResults) {
            renderResults(libraryResults, 'library-results');
        }
    });
}