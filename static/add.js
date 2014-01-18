
$(window).load(function() {
    $('#addMoreBooks').click(function() {
       input = document.createElement('input');
       input.type = 'text';
       input.className = 'form-control pull-left input-lg isbn-field';
       input.placeholder = 'Add Book by ISBN...';
       $('#coursebooks')[0].appendChild(input);
    });
});
