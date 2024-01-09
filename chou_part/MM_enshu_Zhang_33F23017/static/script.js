var globalBookContent = [];
var bookId=-1;
var currentPage=1;
$(document).ready(function() {
    bookId = getQueryParam('book_id');  
    if (bookId!=-1) {
        $.ajax({
            url: '/get_book_content',  // Flask route that returns book content
            type: 'GET',
            data: { 'book_id': bookId },
            success: function(response) {
                $('#book-title').text(response.book_title + ', by ' + response.book_author);
                globalBookContent = response.book_content;
                console.log("Global Book Content:", globalBookContent);
                updateTotalPages();
                getPage();
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
    

    $("#user-input").keypress(function(event) {
        if (event.which === 13) { // 13 is the Enter key
            event.preventDefault(); // Prevents the default action of the keypress
            sendMessage();
        }
    });
    $("#page-index").keypress(function(event) {
        if (event.which === 13) {
            event.preventDefault();
            getPage();
        }
    });
    $('#searchQuery').keypress(function(event) {
        if (event.which === 13) {
            event.preventDefault();
            performSearch();
        }
    });
});

function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

function updateTotalPages() {
    if (globalBookContent){
        document.getElementById('total-pages').innerText = "of "+ globalBookContent.length.toString();
    } else {
        document.getElementById('total-pages').innerText = 'Total count not available';
    }
}
function getPage() {
    var indexInput = document.getElementById('page-index');
    currentPage = parseInt(indexInput.value);
    currentPage = currentPage < 1 ? 1 : currentPage;
    currentPage = currentPage > globalBookContent.length ? globalBookContent.length : currentPage;
    var bookContentElement = document.getElementById("book-content");
    bookContentElement.innerText = globalBookContent[currentPage-1].join('\n\n');
    bookContentElement.scrollTop = 0;
}

function changePage(delta) {
    currentPage += delta;
    document.getElementById('page-index').value = currentPage;
    getPage();
}


function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:8000/chat",  // Flask route
        contentType: "application/json",
        data: JSON.stringify({ "message": userInput, "book_id": bookId, "page_id": currentPage}),
        success: function(response) {
            var chatMessages = document.getElementById('chat-window');
            chatMessages.innerHTML += '<div class="chat-message user-message">User: ' + userInput + '</div>';
            chatMessages.innerHTML += '<div class="chat-message bot-message">Bot: ' + response.response + '</div>';

            // Optional: Scroll to the bottom of the chat
            chatMessages.scrollTop = chatMessages.scrollHeight;
            document.getElementById('user-input').value = '';
        }
    });
}

function performSearch() {
    let query = document.getElementById('searchQuery').value;
    $.ajax({
        type: 'POST',
        url: '/search',
        contentType: 'application/json',
        data: JSON.stringify({ query: query }),
        success: function(searchResults) {
            renderResults(searchResults);
        }
    });
}

function renderResults(results) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // Clear previous results
    results.forEach(result => {
        let div = document.createElement('div');
        div.innerHTML = `${result.title} ${result.author} ${result.genre}<button onclick="goToReading(${result.id})">Select</button>`;
        resultsContainer.appendChild(div);
    });
}

function goToReading(id) {
    window.location.href = `reading.html?book_id=${id}`;
}
