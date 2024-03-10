document.addEventListener("DOMContentLoaded", function() {

    // Event listener for form submission
    document.getElementById("eventForm").addEventListener("submit", function(e) {
        e.preventDefault(); // Prevent the default form submission

        var formData = new FormData(this); // 'this' refers to the form

        // AJAX request to the server
        fetch("{{ url_for('coach.create_event_and_matches') }}", {
            method: 'POST',
            body: formData, // Send the form data
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}', // Ensure you're passing the CSRF token
                'Accept': 'application/json', // Explicitly accept JSON
            },
        })
        .then(response => response.json()) // Convert response to JSON
        .then(data => {
            // Handle the response data
            if (data.status === 'success') {
                // Handle success - perhaps redirect or clear the form
                console.log("Form submitted successfully");
            } else {
                // Handle failure - display validation errors
                console.log("Validation errors", data.errors);
                // Dynamically display errors next to each field
                // You'd need to adjust this to target your dynamic fields
            }
        })
        .catch(error => console.error('Error:', error));
    });
});