// Tiny interaction: show selected resume filename and playful submit feedback.
document.addEventListener('DOMContentLoaded', () => {
  const file = document.querySelector('#resume');
  if (file) file.addEventListener('change', () => {
    const label = document.querySelector('.upload-zone p');
    if (label && file.files.length) label.textContent = '📎 ' + file.files[0].name + ' — locked in!';
  });
  const form = document.querySelector('#career-form');
  if (form) form.addEventListener('submit', () => {
    const button = form.querySelector('button');
    if (button) { button.disabled = true; button.textContent = 'SCANNING YOUR CAREER UNIVERSE… ✨'; }
  });
});
