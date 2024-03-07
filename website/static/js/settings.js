// // Function to toggle the theme
// function toggleTheme() {
//     const currentTheme = localStorage.getItem('theme') === 'dark' ? 'dark' : 'light';
//     const newTheme = currentTheme === 'light' ? 'dark' : 'light';
//     document.body.className = newTheme + '-mode';
//     localStorage.setItem('theme', newTheme);
//   }
  
//   // Event listener for the toggle button on the settings page
//   document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
  
//   // Apply the theme when the page loads
//   document.addEventListener('DOMContentLoaded', () => {
//     const storedTheme = localStorage.getItem('theme') || 'light'; // Default to light mode
//     document.body.className = storedTheme + '-mode';
//   });
  



document.addEventListener('DOMContentLoaded', () => {
    const themeSwitch = document.querySelector('#theme-toggle');
    const storedTheme = localStorage.getItem('theme') || 'light';
    document.body.className = storedTheme + '-mode';
    themeSwitch.checked = storedTheme === 'dark';
  
    themeSwitch.addEventListener('sl-change', () => {
      const isDarkMode = themeSwitch.checked;
      document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
      localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    });
  });
  