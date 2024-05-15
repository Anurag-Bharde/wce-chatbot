// Import required modules
const express = require('express');
const mysql = require('mysql');

// Create Express app
const app = express();
const port = 3306;


const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'Anuraggb',
  database: 'wce_chatbot'
});

// Connect to MySQL database
connection.connect((err) => {
  if (err) {
    console.error('Error connecting to MySQL database: ' + err.stack);
    return;
  }
  console.log('Connected to MySQL database as id ' + connection.threadId);
});

// Middleware to parse JSON and form data
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// POST endpoint to handle feedback submission
app.post('/submit_feedback', (req, res) => {
  const { response, correctness, clarity, comment } = req.body;

  // Insert feedback into the database
  const sql = "INSERT INTO feedbacked (response, correctness, clarity, comment) VALUES (?, ?, ?, ?)";
  connection.query(sql, [response, correctness, clarity, comment], (err, result) => {
    if (err) {
      console.error("Error inserting feedback: " + err.message);
      res.status(500).send("Internal server error");
      return;
    }
    console.log("Feedback submitted successfully");
    res.status(200).send("Feedback submitted successfully");
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
