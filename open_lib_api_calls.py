import requests

def open_lib_isbn(isbn):
    """ get data back from open library api via isbn """
    # add isbn into url
    url = f"https://openlibrary.org/isbn/{isbn}.json"
    
    # get response as json
    response = requests.get(url)
    response_dict = response.json()

    # get title and edition pub date
    title = response_dict['title']
    pub_date = response_dict['publish_date']
    
    # authors goes via different page
    authors = response_dict['authors']

    if len(authors) == 1:
        author_key = authors[0]['key']
        author_url = "https://openlibrary.org" + author_key + ".json"
        
        response = requests.get(author_url)
        response_dict = response.json()
        author = response_dict['name']
    else:
        authors = ""

        for count, author in enumerate(authors):
            author_key = authors[count]['authors']

            author_url = "https://openlibrary.org" + author_key + ".json" 
            response = requests.get(author_url)
            response_dict = response.json()
            author = response_dict['name']
            authors = authors + ", " + author
        # reset numerous authors as one author value
        author = authors
    return(title, author, pub_date)


def open_lib_search(search_via, term):
    """ get data using general open library search api """
    url = "https://openlibrary.org/search.json"
    
    search_via_options = ['title', 'isbn']
    if search_via not in search_via_options: 
        search_via = "" 
    # create url query 
    search_url = url + "?" + search_via + "=" + term + "&limit=10"

    response = requests.get(search_url)
    response_dict = response.json()
    
    unique_works = []
    results = []

    # get top five unique results
    for num in range(len(response_dict['docs'])):
    
        # if response_dict['docs'][num]['ebook_access'] == 'no_ebook':
          #  pass
        # add work key to unique works if not already there
        work_key = response_dict['docs'][num]['key']
        
        if work_key not in unique_works:
            unique_works.append(work_key)
            
            # get basic biblographic data
            title = response_dict['docs'][num]['title'] 
            author = response_dict['docs'][num]['author_name']
            
            # handle multiple authors
            if len(author) == 1:
                author = author[0]
            else:
                author = ', '.join(author)
            
            # handle values that caused key errors on rarer books in testing 
            
            # librarything id can be added to url like:
            # https://www.librarything.com/work/1060
            try:
                num_of_pages = response_dict['docs'][num]['number_of_pages_median']
            except KeyError:
                num_of_pages = 1
            try:
                librarything_ids = response_dict['docs'][num]['id_librarything']
                librarything_id = librarything_ids[0]
                
            except KeyError:
                librarything_id = "n/a"
            try:
                first_publish_date = response_dict['docs'][num]['first_publish_year'] 
            except KeyError:
                first_publish_date = "n/a"

            # cover id can be added to url like: 
            # https://covers.openlibrary.org/b/id/525391-S.jpg - change S to L or M for different sizes
            cover_id_num = response_dict['docs'][num]['cover_i']
            cover_id = f"https://covers.openlibrary.org/b/id/{cover_id_num}-S.jpg"

            results.append({'work_key': work_key, 'title': title, 
                            'pub_date': first_publish_date, 'num_of_pages': num_of_pages,
                            'author': author, 'librarything_id': librarything_id, 
                            'cover_id': cover_id, 'searched_via': search_via,
                            'search_term': term}) 
            
            # enforce limit on number of results 
            if len(results) == 10:
                break
    return results
