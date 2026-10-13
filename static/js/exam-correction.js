(() => {
  const form = document.querySelector('[data-correction-form]');
  if (!form) return;
  const rows = [...form.querySelectorAll('[data-correction-row]')].map(row => ({
    checkbox: row.querySelector('[data-correction-fallback] input'),
    fallback: row.querySelector('[data-correction-fallback]'),
    options: row.querySelector('.correction-options'),
  }));
  if (!rows.length) return;
  const update = () => {
    const correct = rows.filter(row => row.checkbox.checked).length;
    document.querySelector('[data-correct-count]').value = correct.toLocaleString('fa-IR');
    document.querySelector('[data-incorrect-count]').value = (rows.length - correct).toLocaleString('fa-IR');
  };
  rows.forEach(row => {
    row.options.querySelectorAll('input[type="radio"]').forEach(radio => {
      radio.checked = (radio.value === 'correct') === row.checkbox.checked;
      radio.addEventListener('change', () => {
        row.checkbox.checked = radio.value === 'correct';
        update();
      });
    });
    row.options.hidden = false;
    row.fallback.hidden = true;
  });
  document.querySelectorAll('[data-correction-enhancement]').forEach(el => { el.hidden = false; });
  update();
})();
