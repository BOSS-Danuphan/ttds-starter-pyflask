$( document ).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('message', function(data){
        $('#ws-log').append('<p>'+data.data+'</p>');
    });
    socket.on('feed', function(data){
        if ($('#ws-feed').find('p').length > 5) {
            $('#ws-feed').empty()
        }
        $('#ws-feed').append('<p>'+data.data+'</p>');
    });
})
