document.addEventListener('DOMContentLoaded', (event) => {
    const webcamElement = document.getElementById('webcam');
    const wordDisplayElement = document.getElementById('word-display');
    const distanceDisplayElement = document.getElementById('distance-display');
    const wordInputElement = document.getElementById('word-input');
    const verifyButtonElement = document.getElementById('verify-button');
    let currentWord = "";

    async function setupWebcam() {
        const stream = await navigator.mediaDevices.getUserMedia({ 'video': true });
        webcamElement.srcObject = stream;

        setInterval(async () => {
            const frame = captureFrame(webcamElement);
            const distance = await sendFrameToServer(frame);
            distanceDisplayElement.innerText = `Distance: ${distance} inches`;
        }, 1000);
    }

    async function sendFrameToServer(frame) {
        const response = await fetch('/process_image', {
            method: 'POST',
            body: frame
        });
        const result = await response.json();
        return result.distance;
    }

    function captureFrame(video) {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg');
    }

    async function getNextWord() {
        const response = await fetch('/get_next_word');
        const result = await response.json();
        currentWord = result.word;
        wordDisplayElement.innerText = currentWord;
    }

    async function verifyWord() {
        const response = await fetch('/verify_word', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ response: wordInputElement.value })
        });
        const result = await response.json();
        alert(result.verified ? "Correct" : "Incorrect");
        await getNextWord();
    }

    verifyButtonElement.addEventListener('click', verifyWord);
    getNextWord();
    setupWebcam();
});
