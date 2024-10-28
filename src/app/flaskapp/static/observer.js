const socket = io('/image-processing');

socket.on('broadcasted-image', image => {
    document.getElementById("streamed").src = image;
});