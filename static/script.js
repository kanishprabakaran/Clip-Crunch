document.getElementById("summaryButton").addEventListener("click", getSummary);

function getSummary() {
  const urlInput = document.getElementById('youtubeUrl').value;
  const videoId = extractVideoId(urlInput);
  console.log("API Called !!!")
  if (videoId) {
    // Show the video player
    document.getElementById('videoPlayer').src = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;

    // Show loading spinner and hide summary text while loading
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('summaryText').style.display = 'none';

    fetch('/get_summary', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: urlInput }),
    })
    .then(response => response.json())
    .then(data => {
      console.log(data.summary); // Check this in the console
      document.getElementById('loadingSpinner').style.display = 'none';
      document.getElementById('summaryText').style.display = 'block';
      document.getElementById('summaryText').innerText = data.summary;
  })
  
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('loadingSpinner').style.display = 'none';
      document.getElementById('summaryText').style.display = 'block';
      document.getElementById('summaryText').innerText = 'Error retrieving summary. Please try again.';
    });
  } else {
    alert('Please enter a valid YouTube URL.');
  }
}

function extractVideoId(url) {
  const videoIdMatch = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|.+\?v=)|youtu\.be\/)([^&?\/\s]{11})/);
  return videoIdMatch ? videoIdMatch[1] : null;
}
