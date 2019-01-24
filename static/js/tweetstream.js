$(document).ready(function(){

    var namespace = '/demo_streaming';
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    socket.on('message', function(data){
        $('#tweet').append('<p>'+data.data+'</p>');
    });
    socket.on('stream_channel', function(data){
        console.log(data)
        if ($('#tweet').find('p').length > 10) {
            $('#tweet').empty()
        }
        $('#tweet').prepend('<p>'+data.data+'</p>');
    });
});