
  let langFrom = "{{ default_lang_from }}";
  let langTo = "{{ default_lang_to }}";
  let currentListName = "";

  async function updateLangsIfNeeded() {
    const newListName = document.getElementById('list_name').value;
    if (newListName !== currentListName) {
      currentListName = newListName;

      const response = await fetch(
        `/get_langs?text_id={{ text.id }}&list_name=${encodeURIComponent(currentListName)}`
      );
      const data = await response.json();

      langFrom = data.lang_from;
      langTo = data.lang_to;
    }
  }

  document.getElementById('glosbe-link').addEventListener('click', async function (event) {
    const link = event.currentTarget;
    const phrase = document.getElementById('phrase-field').value.trim();

    if (link.classList.contains('disabled') || !phrase) {
      event.preventDefault();
      return;
    }

    event.preventDefault();

    await updateLangsIfNeeded();

    const glosbeUrl = `https://glosbe.com/${langFrom}/${langTo}/${encodeURIComponent(phrase)}`;
    link.setAttribute('href', glosbeUrl);
    window.open(glosbeUrl, '_blank');
  });

function setGlosbeUrl() {
  const link = document.getElementById('glosbe-link');
  const phrase = document.getElementById('phrase-field').value.trim();

  if (!phrase || link.classList.contains('disabled')) {
    return;
  }

  updateLangsIfNeeded();

  const glosbeUrl = `https://glosbe.com/${langFrom}/${langTo}/${encodeURIComponent(phrase)}`;
  link.setAttribute('href', glosbeUrl);
};

 document.getElementById('phrase-field').addEventListener('input', (event) => {
      onOffPhraseLink("glosbe-link", 100);
  });
  window.addEventListener('load', (event) => {
      onOffPhraseLink("glosbe-link", 100);
  });
  window.addEventListener('load', updateLangsIfNeeded);
