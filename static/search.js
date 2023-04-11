document.addEventListener("DOMContentLoaded", function(event) {

    let input = document.querySelector('.search');
    input.addEventListener('input', async function() {
        let response = await fetch('/search?q=' + input.value);
        let books = await response.json();
        let results = '';
        for (var i = 0; i < books.length; i++) {
            // parse individual books into readable json
            var book = JSON.parse(books[i]);
            // create table row per book 
            results += '<tr>' + '<td>' + '<img class="cover" src="' + book.cover_id + '"' + ' alt="Book cover">' + '</td>' + '<td>' + '<a class="open-lib-link" href="https://openlibrary.org' + book.work_key + '">' + book.title + '</a>' + '</td>' + '<td>' + book.author + '</td>' + '<td>' + book.date + '</td>' + '<td>' + book.review + '</td>' + '</tr>';
        }
        // check for valid results
        if (results) {
            // define headers 
            document.getElementById("cover").innerHTML = "Cover";
            document.getElementById("title").innerHTML = "Title";
            document.getElementById("author").innerHTML = "Author";
            document.getElementById("date").innerHTML = "Publication Date";
            document.getElementById("review").innerHTML = "Review";
            // add data
            document.getElementById("results").innerHTML = results;
        }
    });
});
