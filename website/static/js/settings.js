document.addEventListener('DOMContentLoaded', () => {
  // Apply theme mode and background color on page load
  applyThemeMode();
  applyBackgroundColor();

  // Add event listener for theme toggle if it exists
  const themeSwitch = document.querySelector('#theme-toggle');
  if (themeSwitch) {
      themeSwitch.addEventListener('sl-change', () => {
          const isDarkMode = themeSwitch.checked;
          document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
          localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
      });
  }

  // Add event listener for background color selection
  const colorPicker = document.querySelector('sl-color-picker');
  if (colorPicker) {
      colorPicker.addEventListener('sl-change', event => {
          const color = event.target.value;
          localStorage.setItem('backgroundColor', color);
          document.body.style.backgroundColor = color;
      });
  }

  // Add event listener for notification badge if it exists
  const notificationBadge = document.getElementById("notification-badge");
  if (notificationBadge) {
      const notificationCount = 5; // Replace this with your actual notification count
      notificationBadge.innerText = notificationCount;
  }
});

function applyThemeMode() {
  const storedTheme = localStorage.getItem('theme') || 'light';
  document.body.className = storedTheme + '-mode';
  const themeSwitch = document.querySelector('#theme-toggle');
  if (themeSwitch) {
      themeSwitch.checked = storedTheme === 'dark';
  }
}

function applyBackgroundColor() {
  const savedColor = localStorage.getItem('backgroundColor');
  if (savedColor) {
      document.body.style.backgroundColor = savedColor;
  }
}
