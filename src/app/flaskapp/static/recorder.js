const socket = io('/image-processing');

socket.on('stream-image', image => {
  console.log(image);
  document.getElementById("streamed").src = image;
});

window.URL = window.URL || window.webkitURL;
navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
window.requestFileSystem = window.requestFileSystem || window.webkitRequestFileSystem;

var video = document.querySelector('video');
var canvas = document.querySelector('canvas');
var ctx = canvas.getContext('2d');
var localMediaStream = null;

function snapshot() {
  if (localMediaStream) {
      ctx.drawImage(video, 0, 0);
 
      var image = canvas.toDataURL('image/jpeg');
      var arr = image.split(',');
      var bstr = atob(arr[1]);
      // var mime = arr[0].match(/:(.*?);/)[1];
      // var n = bstr.length;
      // var u8arr = new Uint8Array(n);
      
      // while(n--){
      //   u8arr[n] = bstr.charCodeAt(n);
      // }
      
      socket.emit('receive-image', bstr);
  }
}

function startVideo() {
  video.addEventListener('click', snapshot, false);
  setInterval(snapshot, 500);
 
  navigator.getUserMedia({ video: true }, function(stream) {
      video.srcObject = stream;
      localMediaStream = stream;

      video.play();
      snapshot();
  }, function(e) {
      console.log("rejected", e);
  });
}

startVideo();