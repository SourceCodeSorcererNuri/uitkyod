// static/app.js (Updated)
document.addEventListener('DOMContentLoaded', () => {
    const downloadForm = document.getElementById('downloadForm');
    const submitButton = downloadForm.querySelector('button[type="submit"]');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    let simulationInterval;

    // Function to simulate progress while waiting for the server
    function startSimulation() {
        let progress = 0;
        const speed = 1; // Speed of simulation

        // Show the progress bar container
        progressContainer.style.display = 'flex';

        // Start the interval
        simulationInterval = setInterval(() => {
            if (progress < 95) { // Stop just before 100 to wait for the actual file
                progress += Math.random() * speed;
                progress = Math.min(progress, 95);

                progressBar.style.width = `${progress.toFixed(0)}%`;
                progressText.textContent = `Yuklanmoqda... (${progress.toFixed(0)}%)`;
            } else if (progress >= 95) {
                // Show a final waiting message near completion
                progressBar.style.width = '95%';
                progressText.textContent = `Faylni yakunlash... Kuting.`;
            }
        }, 500); // Update every half second
    }

    function stopSimulation() {
        clearInterval(simulationInterval);
    }

    function resetProgress() {
        stopSimulation();
        progressContainer.style.display = 'none';
        progressBar.style.width = '0%';
        progressText.textContent = 'Tayyorlanmoqda... (0%)';
    }


    downloadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // 1. Start Loading/Simulation State
        submitButton.disabled = true;
        submitButton.textContent = 'Tayyorlanmoqda...';
        startSimulation();

        const formData = new FormData(downloadForm);

        try {
            const response = await fetch('/download', {
                method: 'POST',
                body: formData,
            });

            // 2. Stop Simulation when server response is received
            stopSimulation();

            if (response.ok) {
                // Finalize UI for success
                progressBar.style.width = '100%';
                progressText.textContent = `Yuklash muvaffaqiyatli!`;

                const blob = await response.blob();
                const contentDisposition = response.headers.get('Content-Disposition');

                let filename = 'download.file';
                if (contentDisposition) {
                    const matches = contentDisposition.match(/filename="(.+?)"/);
                    if (matches && matches.length > 1) {
                        filename = matches[1];
                    }
                }

                // Create a temporary link element to trigger the download
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

            } else {
                // Handle server-side errors
                const errorText = await response.text();
                // Finalize UI for error
                progressBar.style.width = '0%';
                progressText.textContent = `Xatolik!`;
                alert(`Yuklab olishda xatolik yuz berdi: ${errorText}`);
            }

        } catch (error) {
            // Handle network errors
            stopSimulation();
            progressBar.style.width = '0%';
            progressText.textContent = `Tarmoq xatosi!`;
            console.error('Fetch error:', error);
            alert('Tarmoq xatosi yoki kutilmagan xato yuz berdi.');
        } finally {
            // 3. Reset Button and Progress after a short delay
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.textContent = 'Yuklab olish';
                resetProgress();
            }, 3000); // Keep success/error message for 3 seconds
        }
    });
});
