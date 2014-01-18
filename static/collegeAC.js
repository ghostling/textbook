  $(function() {
    var availableTags = [];
    var file = "/static/colleges.txt";
    $.get(file, function(data) {
        availableTags = data.split('\n');
        $( "#school" ).autocomplete({
          source: availableTags
        });
    });
  });
