// Use Google Books API to pull top three books relevant to inputted text
// DO NOT DELETE COMMENTED CODE. MAY BE USEFUL FOR FUTURE.
/*
var fetchJSON = function(query) {
    if (query.length == 10 || query.length == 13) {
        var link = "https://www.googleapis.com/books/v1/volumes?q=" + query;
        $.getJSON(link, function(data) {
            var book = {'title': topThree[0]['volumeInfo']['title'],
                        'authors': topThree[0]['volumeInfo']['title'],
                        'thumbnail': topThree[0]['volumeInfo']['imageLinks']['thumbnail'],
                        'isbn': topThree[0]['industryIdentifiers']};
        }
    });
};
*/

$(window).load(function() {
    $('#addMoreBooks').click(function() {
       var input = document.createElement('input');
       input.type = 'text';
       input.className = 'form-control pull-left input-lg isbn-field';
       input.placeholder = 'Add Book by ISBN...';
       input.name = "book";
       $('#coursebooks')[0].appendChild(input);

       $(input).keyup(function() {
        fetchJSON(input.val());
       });
    });
    /*
    $('.isbn-field').each(function() {
        var field = $(this);
        field.keyup(function() {
            fetchJSON(field.val());
        });
    });
    */
});


