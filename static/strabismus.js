function fetchLatestReport() {
    fetch('/strabismus/get_latest_report')  // Added blueprint prefix
        .then(response => response.json())
        .then(data => {
            document.getElementById('report').innerText = data.report;
        });
}

setInterval(fetchLatestReport, 1000);
function showCaptureAlert(message) {
        var captureAlert = document.getElementById('capture-alert');
        captureAlert.showCaptureAlert = message;
        captureAlert.style.display = 'block';

        // Automatically close the program after 5 seconds
        setTimeout(function() {
            window.location.href = "{{ url_for('strabismus.shutdown') }}";  // Modified line
        }, 5000);  // Adjust the timeout duration as needed
}
function initiateShutdown() {
    fetch('/strabismus/shutdown')
        .then(response => response.text())
        .then(data => {
            console.log(data);
            window.location.href = "/dashboard";
        });
}

// Add an event listener to the exit button
document.getElementById('dashboard-button').addEventListener('click', initiateShutdown);

// function strabismusTest() {
//     fetch('/strabismus/video_feeds')
//         .then(response => response.text())
//         .then(data => {
//             console.log(data);
//             window.location.href = "/strabismus";
//         });
// }

// document.getElementById('strabismusTest').addEventListener('click', strabismusTest);

