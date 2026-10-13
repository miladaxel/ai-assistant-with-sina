(() => {
  const form = document.querySelector('[data-student-selection]');
  if (!form) return;
  const rows = [...form.querySelectorAll('[data-student-option]')];
  if (!rows.length) return;
  const search = form.querySelector('[data-student-search]');
  const selected = form.querySelector('[data-selected-count]');
  const visible = form.querySelector('[data-visible-count]');
  const noResults = form.querySelector('[data-no-results]');
  const normalize = value => value.normalize('NFKC').replace(/ي/g, 'ی').replace(/ك/g, 'ک').replace(/[\u200c\u200d]/g, ' ').trim().toLocaleLowerCase('fa');
  const number = value => value.toLocaleString('fa-IR');
  const update = () => {
    selected.value = number(rows.filter(row => row.querySelector('input').checked).length);
    visible.textContent = `نمایش ${number(rows.filter(row => !row.hidden).length)} از ${number(rows.length)} نفر`;
  };
  const filter = () => {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    rows.forEach(row => { row.hidden = !terms.every(term => normalize(row.querySelector('[data-student-name]').textContent).includes(term)); });
    noResults.hidden = rows.some(row => !row.hidden);
    update();
  };
  form.querySelectorAll('[data-selection-enhancement]').forEach(el => { el.hidden = false; });
  search.addEventListener('input', filter);
  search.addEventListener('keydown', event => {
    if (event.key === 'Enter') event.preventDefault();
  });
  form.addEventListener('change', update);
  form.querySelectorAll('[data-select-visible]').forEach(button => {
    button.addEventListener('click', () => {
      rows.filter(row => !row.hidden).forEach(row => { row.querySelector('input').checked = button.dataset.selectVisible === 'true'; });
      update();
    });
  });
  update();
})();
