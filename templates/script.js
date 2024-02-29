document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();
  
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;
    const confirm_password = document.querySelector('input[name="confirm_password"]').value;
  
    if (password !== confirm_password) {
      alert('Passwords do not match');
      return;
    }
  
    const data = { username, password };
  
    fetch('http://localhost:5000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      alert('User registered successfully');
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred while registering');
    });
  });
  