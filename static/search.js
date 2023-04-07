document.addEventListener("DOMContentLoaded", function(event) {

    let input = document.querySelector('.search');
    input.addEventListener('input', async function() {
        let response = await fetch('/search?q=' + input.value);
        let books = await response.json();
        let html = '';
        for (var i = 0; i < books.length; i++) {
            //console.log((books[i]));
            console.log(typeof books[i]);
            var book = JSON.parse(books[i]);
            console.log(book.title);
            html += '<li>' + book.title + '</li>';
        }
        document.querySelector('ul').innerHTML = html;
    });
});
