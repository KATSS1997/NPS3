let selectedRating = null;
let requestAnswered = null;

// Extract the OS number from the URL and set it in the input field
function getOsNumberFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const osNumber = urlParams.get('id');
    if (osNumber) {
        document.getElementById('os-number').value = osNumber;
        confirmOsNumber(osNumber); // Automatically confirm the OS number
    }
}

// Function to confirm OS number
function confirmOsNumber(osNumber) {
    fetch('/confirm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            osNumber: osNumber
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response from server:', data);
        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('os-number').disabled = true;
        document.getElementById('confirm-os').style.display = 'none';
        document.getElementById('additional-container').style.display = 'block';
        document.getElementById('scale-container').style.display = 'block';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    getOsNumberFromUrl();
});

document.querySelectorAll('.scale div').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.scale div').forEach(div => div.classList.remove('selected'));
        item.classList.add('selected');
        selectedRating = item.getAttribute('data-value');
        console.log('Selected Rating:', selectedRating);
        document.getElementById('comment-container').style.display = 'block';
        document.getElementById('solicitacao-container').style.display = 'block';
        document.getElementById('submit').style.display = 'block';
    });
});

document.getElementById('yes').addEventListener('click', () => {
    document.getElementById('yes').classList.add('selected');
    document.getElementById('no').classList.remove('selected');
    requestAnswered = 'S';
    console.log('Request Answered:', requestAnswered);
});

document.getElementById('no').addEventListener('click', () => {
    document.getElementById('no').classList.add('selected');
    document.getElementById('yes').classList.remove('selected');
    requestAnswered = 'N';
    console.log('Request Answered:', requestAnswered);
});

// Remove the click event listener for the confirm-os button
// document.getElementById('confirm-os').addEventListener('click', () => {
//     const osNumber = document.getElementById('os-number').value;

//     if (osNumber === '') {
//         alert('Por favor, digite o número da OS.');
//         return;
//     }

//     console.log('OS Number:', osNumber);

//     confirmOsNumber(osNumber);
// });

document.getElementById('submit').addEventListener('click', () => {
    const comment = document.getElementById('comment').value;
    const osNumber = document.getElementById('os-number').value;

    if (selectedRating === null || requestAnswered === null || osNumber === '') {
        alert('Por favor, complete todas as perguntas.');
        return;
    }

    const data = {
        rating: selectedRating,
        requestAnswered: requestAnswered,
        comment: comment,
        osNumber: osNumber
    };

    console.log('Submitting data:', data);

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response from server:', data);
        document.getElementById('os-container').style.display = 'none';
        document.getElementById('additional-container').style.display = 'none';
        document.getElementById('thank-you-message').style.display = 'block';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
