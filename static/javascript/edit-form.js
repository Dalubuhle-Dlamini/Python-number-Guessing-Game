function validateForm() {
    var email = document.getElementById("email").value;
    var image = document.getElementById("image").value;
    var errorMessage = document.getElementById("errorMessage");

    errorMessage.innerHTML = ""; // Clear any previous error message

    if (email.trim() === "") {
        errorMessage.innerHTML = "Please enter your email.";
        return false; // Prevent form submission
    }

    if (image.trim() === "") {
        errorMessage.innerHTML = "Please select a profile picture.";
        return false;
    }

    var allowedExtensions = /(\.jpg|\.jpeg|\.png|\.gif)$/i;
    if (!allowedExtensions.exec(image)) {
        errorMessage.innerHTML = "Invalid file format. Please select an image file (JPG, JPEG, PNG, GIF).";
        return false;
    }

    // Additional validation rules can be added here if needed

    return true; // Allow form submission
}