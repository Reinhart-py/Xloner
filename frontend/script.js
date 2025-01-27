document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('nav');

  menuToggle.addEventListener('click', function() {
    nav.classList.toggle('show');
  });
});

document.getElementById('downloadForm').addEventListener('submit', function(event) {
  event.preventDefault();
  const url = document.getElementById('urlInput').value;
  const progressBar = document.querySelector('.progress-bar::before');
  const progressContainer = document.getElementById('progress-container');
  const downloadLinkContainer = document.getElementById('downloadLinkContainer');
  const errorMessage = document.getElementById('error-message');
  const progressMessage = document.getElementById('progress-message');

  progressContainer.classList.remove('progress-hidden');
  downloadLinkContainer.classList.add('download-hidden');
  errorMessage.classList.add('error-hidden');
  progressBar.style.width = '0%';


  fetch('/download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url }),
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(errorData => {
          errorMessage.classList.remove('error-hidden');
          errorMessage.textContent = errorData.error;
          progressContainer.classList.add('progress-hidden');
        });
      }
      progressMessage.textContent = 'Processing...';
      return response.blob();

    })
    .then(blob => {
      if (blob) {
        progressMessage.textContent = 'Download Complete!'
        progressBar.style.width = '100%';
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = 'website-code.zip';
        downloadLink.textContent = 'Download ZIP';
        downloadLinkContainer.innerHTML = '';
        downloadLinkContainer.appendChild(downloadLink);
        downloadLinkContainer.classList.remove('download-hidden');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      errorMessage.classList.remove('error-hidden');
      errorMessage.textContent = "An unexpected error occurred, Please try again";
      progressContainer.classList.add('progress-hidden');
    });

  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    progressBar.style.width = `${progress}%`;

    if (progress >= 90) {
      clearInterval(interval)
    }
  }, 150);
});