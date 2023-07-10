//import {sendPostRequest} from './inout_button.js';
   
    /* let timer;
    let isRunning = false;

    function formatTime(seconds) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;

      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    function startTimer() {
      let timeLeft = 120; // 2 minutes in seconds

      function updateTimer() {
        if (timeLeft > 0) {
          document.getElementById('timer').innerText = 'Timer: ' + formatTime(timeLeft);
          timeLeft--;
        } else {
          clearInterval(timer);
          document.getElementById('timer').innerText = 'Timer has finished';
          document.getElementById('readotp-button').innerText = 'APP';
          isRunning = false;
        }
      }

      updateTimer();
      timer = setInterval(updateTimer, 1000);
    }

    function cancelTimer() {
      clearInterval(timer);
      document.getElementById('timer').innerText = 'Operation Canceled';

      // Hide the "Operation Canceled" timer after 3 seconds
      setTimeout(function() {
        document.getElementById('timer').innerText = '';
      }, 3000);

      document.getElementById('readotp-button').innerText = 'APP';
      isRunning = false;
    }

    function scanRFIDotp(){
      if (isRunning) {
        cancelTimer();
      } else {
        var isApp = true;
        sendPostRequest(None, isApp)
        document.getElementById('timer').innerText = '';
        document.getElementById('readotp-button').innerText = 'CANCEL';
        isRunning = true;
        startTimer();
      }
    } */
