function setCambridgeUrl() {
  const link = document.getElementById('cambridge-link');
  const phrase = document.getElementById('phrase-field').value.trim();

  if (!phrase || link.classList.contains('disabled')) {
    return;
  }

  updateLangsIfNeeded();

  const CambridgeUrl = `https://dictionary.cambridge.org/dictionary/english/${encodeURIComponent(phrase)}`;
  link.setAttribute('href', CambridgeUrl);
};

  document.getElementById('phrase-field').addEventListener('input', (event) => {
      onOffPhraseLink("cambridge-link");
  });
  window.addEventListener('load', (event) => {
      onOffPhraseLink("cambridge-link");
  });