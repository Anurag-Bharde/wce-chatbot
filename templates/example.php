<?php
// Connect to MySQL (replace with your actual database credentials)
$servername = "localhost";
$username = "root";
$password = "Anuraggb";
$dbname = "wce_chatbot";

$conn = new mysqli($localhost, $root, $Anuraggb, $wce_chatbot);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get form data
$username = $_POST['username'];
$response = $_POST['response'];
$correctness = $_POST['correctness'];
$clarity = $_POST['clarity'];
$experience = $_POST['experience'];
$comment = $_POST['comment'];

// Insert data into the database
$sql = "INSERT INTO feedback (username, response, correctness, clarity, experience, comment) 
        VALUES ('$username', $response, $correctness, $clarity, $experience, '$comment')";

if ($conn->query($sql) === TRUE) {
    echo "Feedback submitted successfully!";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
