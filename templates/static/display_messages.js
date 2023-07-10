async function displayError(err_id) {
    var messageDiv = document.getElementById("message");

    switch (err_id) {
        case 1:
            messageDiv.innerHTML = "Request failed<br>Check internet connection";
            break;
        case 2:
            messageDiv.innerHTML = "NetworkError when <br>attempting to fetch resource";
            break;
        case 3:
            messageDiv.innerHTML = "Error in<br>database connection";
            break;
        case 4:
            messageDiv.innerHTML = "You must enter<br>before exiting";
            break;
        case 5:
            messageDiv.innerHTML = "You must exit<br>before entering";
            break;
        case 6:
            messageDiv.innerHTML = "No areas assigned<br>to this badge";
            break;
        case 7:
            messageDiv.innerHTML = "You can't open<br>this door";
            break;
        default:
            messageDiv.innerHTML = "Generic error";
            break;
    }
    messageDiv.style.display = "block";
    messageDiv.style.color = "#bb0000";

    //Reset message after 3s
    await sleep(3000);
    messageDiv.innerHTML = "";
    messageDiv.style.color = "#000000";
}

async function displayMessage(data) {
    var messageDiv = document.getElementById("message");
    console.log("Displaying message")
    console.log(data.result)

    if (data.dbsuccess) {

        if (data.result == "goinfirst") {
            displayError(4);
        } else if (data.result == "gooutfirst") {
            displayError(5);
        } else if (data.result == "violation_noarea") {
            displayError(6);
        } else if (data.result == "violation") {
            displayError(7);
        } else if (data.result == "success_in") {
            messageDiv.innerHTML = "Welcome back<br>" + data.name + " " + data.surname;
            messageDiv.innerHTML += "<br>Clock in time:<br>" + data.ts_in;
        } else if (data.result == "success_out") {
            messageDiv.innerHTML = "Goodbye<br>" + data.name + " " + data.surname;
            messageDiv.innerHTML += "<br>Clock out time:<br>" + data.ts_out;
        } else { //Means that the result is an otp code
            messageDiv.style.color = "#253885";
            messageDiv.innerHTML = "Use the code<br>" + data.result + "<br>to register time log"
            await sleep(120000);
        }

    } else {
        messageDiv.innerHTML = "Badge not found<br>in the database";
    }

    messageDiv.style.display = "block";
    //Reset message after 5s
    await sleep(5000);
    messageDiv.style.color = "#000000";
    messageDiv.innerHTML = "";
}