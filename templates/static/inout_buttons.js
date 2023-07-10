async function scanRFIDin() {
    var button = document.getElementById("readin-button");
    if (button.innerHTML === "IN") {
        button.innerHTML = "...";
        sendPostRequest(true, false);
        console.log("Entering")
        await sleep(3000);
        button.innerHTML = "IN";
    } else {
        button.innerHTML = "IN";
    }
}

async function scanRFIDout() {
    var button = document.getElementById("readout-button");
    if (button.innerHTML === "OUT") {
        button.innerHTML = "...";
        sendPostRequest(false, false);
        console.log("Exiting")
        await sleep(3000);
        button.innerHTML = "OUT";
    } else {
        button.innerHTML = "OUT";
    }
}

// isEntering is true if the user has pressed the IN button
function sendPostRequest(isEntering, isApp) {
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ isEntering: isEntering, isApp : isApp })
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Post request failed.');
            }
        })
        .then(data => {
            if (data.Err_db) {
                displayError(3);
            }
            // If the card is empty redirect to the keypad
            const isEmpty = data.empty;
            if (isEmpty) {
                window.location.href = "/keypad";
            } else {
                // Update the isSuccess variable based on the server response
                displayMessage(data);
            }

        })
        .catch(error => {
            // Handle any errors that occurred during the request
            if (error instanceof TypeError && error.message === "NetworkError when attempting to fetch resource.") {
                var messageDiv = document.getElementById("message");
                displayError(2);
            } else {
                console.log(error);

                var messageDiv = document.getElementById("message");
                displayError(1);
            }
        });
}