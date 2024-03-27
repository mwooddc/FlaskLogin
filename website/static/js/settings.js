document.addEventListener('DOMContentLoaded', () => {
    const themeSwitch = document.querySelector('#theme-toggle');
    if (themeSwitch) {
      const storedTheme = localStorage.getItem('theme') || 'light';
      document.body.className = storedTheme + '-mode';
      themeSwitch.checked = storedTheme === 'dark';
  
      themeSwitch.addEventListener('sl-change', () => {
        const isDarkMode = themeSwitch.checked;
        document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
      });
    }

      // Log the saved background color to the console
    console.log(localStorage.getItem('backgroundColor'));
  
    const savedColor = localStorage.getItem('backgroundColor');
    if (savedColor) {
      document.body.style.backgroundColor = savedColor; // Apply the saved background color
    }
  
    themeSwitch.addEventListener('sl-change', () => {
      const isDarkMode = themeSwitch.checked;
      document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
      localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    });
  
    document.querySelector('sl-color-picker').addEventListener('sl-change', event => {
      const color = event.target.value;
      localStorage.setItem('backgroundColor', color); // Save the color to localStorage
      document.body.style.backgroundColor = color; // Apply color immediately
    });
  });
  