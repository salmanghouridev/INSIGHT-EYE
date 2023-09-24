function fetchLatestReport() {
    fetch('/get_latest_report')
        .then(response => response.json())
        .then(data => {
            document.getElementById('report').innerText = data.report;
        });
}

setInterval(fetchLatestReport, 1000);

function showCaptureAlert(message) {
        var captureAlert = document.getElementById('capture-alert');
        captureAlert.innerHTML = message;
        captureAlert.style.display = 'block';

        // Automatically close the program after 5 seconds
        setTimeout(function() {
            window.location.href = "{{ url_for('shutdown') }}";
        }, 1000);  // Adjust the timeout duration as needed
    }
