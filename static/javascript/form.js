function validateForm() {
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    var valPassword = document.getElementById("valPassword").value;
    var image = document.getElementById("image").value;
    var errorMessage = document.getElementById("errorMessage");

    errorMessage.innerHTML = ""; // Clear any previous error message

    if (email.trim() === "") {
        errorMessage.innerHTML = "Please enter your email.";
        return false; // Prevent form submission
    }

    if (password.trim() === "") {
        errorMessage.innerHTML = "Please enter your password.";
        return false;
    }

    if (password.length < 6) {
        document.getElementById("password").style.color = "#f00"
        errorMessage.innerHTML = "Password should be at least 6 characters long.";
        return false;
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

    if (password !== valPassword) {
        errorMessage.innerHTML = "Passwords do not match.";
        return false;
    }
    // Additional validation rules can be added here if needed

    return true; // Allow form submission
}