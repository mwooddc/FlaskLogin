document.addEventListener("DOMContentLoaded", function() {

    // Event listener for form submission
    document.getElementById("eventForm").addEventListener("submit", function(e) {
        e.preventDefault(); // Prevent the default form submission

        var formData = new FormData(this);

        // AJAX request to the server
        fetch("{{ url_for('coach.create_event_and_matches') }}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}',
                'Accept': 'application/json',
            },
        })
        .then(response => response.json()) // Convert response to JSON
        .then(data => {
            if (data.status === 'success') {
                console.log("Form submitted successfully");
            } else {
                // Handle failure - display validation errors
                console.log("Validation errors", data.errors);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});