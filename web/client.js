(() => {
  const form = document.querySelector('#analyze-form');
  const review = document.querySelector('#review-text');
  const apiUrl = document.querySelector('#api-url');
  const count = document.querySelector('#char-count');
  const button = document.querySelector('#analyze-button');
  const formError = document.querySelector('#form-error');
  const resultCard = document.querySelector('.result-card');
  const resultStatus = document.querySelector('#result-status');
  const resultContent = document.querySelector('#result-content');
  const apiStatus = document.querySelector('#api-status');

  const labels = {
    POSITIVE: { title: 'Avis positif', message: 'Le texte exprime plutôt une expérience positive.' },
    NEGATIVE: { title: 'Avis négatif', message: 'Le texte exprime plutôt une expérience négative.' },
    INDETERMINE: { title: 'À faire vérifier', message: 'Le modèle manque de confiance pour trancher.' },
  };

  function baseUrl() {
    return apiUrl.value.trim().replace(/\/+$/, '');
  }

  function setStatus(state, message) {
    resultCard.dataset.state = state;
    resultStatus.textContent = message;
  }

  function showError(message) {
    formError.textContent = message;
    formError.hidden = false;
    resultContent.removeAttribute('data-label');
    resultContent.replaceChildren();
    const title = document.createElement('h2');
    title.textContent = 'Analyse impossible';
    const detail = document.createElement('p');
    detail.textContent = message;
    resultContent.append(title, detail);
    setStatus('error', 'Une erreur est survenue');
  }

  function responseMessage(body, fallback) {
    return body?.detail || body?.erreur?.message || body?.message || fallback;
  }

  function renderResult(data) {
    const label = labels[data.label];
    if (!label || !Number.isFinite(Number(data.score))) {
      showError('La réponse reçue ne correspond pas au contrat attendu par cette page.');
      return;
    }

    const score = Math.max(0, Math.min(1, Number(data.score)));
    resultContent.dataset.label = data.label;
    resultContent.replaceChildren();

    const badge = document.createElement('span');
    badge.className = 'verdict';
    badge.textContent = data.label;
    const title = document.createElement('h2');
    title.className = 'result-title';
    title.textContent = label.title;
    const description = document.createElement('p');
    description.textContent = label.message;

    const scoreRow = document.createElement('div');
    scoreRow.className = 'score-row';
    scoreRow.setAttribute('aria-label', `Confiance ${Math.round(score * 100)} pour cent`);
    const track = document.createElement('div');
    track.className = 'score-track';
    const fill = document.createElement('div');
    fill.className = 'score-fill';
    fill.style.width = `${Math.round(score * 100)}%`;
    track.append(fill);
    const value = document.createElement('span');
    value.className = 'score-value';
    value.textContent = `${Math.round(score * 100)} %`;
    scoreRow.append(track, value);
    resultContent.append(badge, title, description, scoreRow);

    if (data.label === 'INDETERMINE') {
      const note = document.createElement('p');
      note.className = 'review-note';
      note.textContent = 'Un conseiller doit examiner cet avis avant toute décision.';
      resultContent.append(note);
    }
    formError.hidden = true;
    setStatus('success', 'Analyse terminée');
  }

  async function request(path, options = {}) {
    let response;
    try {
      response = await fetch(`${baseUrl()}${path}`, {
        ...options,
        headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
      });
    } catch {
      throw new Error('API injoignable. Vérifiez son adresse, son démarrage et la configuration CORS.');
    }
    let body = {};
    try { body = await response.json(); } catch { /* Some server errors have no JSON body. */ }
    if (!response.ok) {
      const fallback = response.status === 422
        ? 'Le texte a été refusé : vérifiez qu’il contient entre 1 et 2 000 caractères.'
        : `L’API a répondu avec le statut ${response.status}.`;
      throw new Error(responseMessage(body, fallback));
    }
    return body;
  }

  review.addEventListener('input', () => {
    count.textContent = `${review.value.length} / 2 000`;
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const text = review.value.trim();
    formError.hidden = true;
    if (!text) {
      showError('Saisissez un avis avant de lancer l’analyse.');
      return;
    }
    button.disabled = true;
    button.querySelector('span:first-child').textContent = 'Analyse en cours…';
    setStatus('loading', 'Le modèle analyse votre avis');
    try {
      renderResult(await request('/predict', { method: 'POST', body: JSON.stringify({ text }) }));
    } catch (error) {
      showError(error.message || 'Une erreur inattendue est survenue.');
    } finally {
      button.disabled = false;
      button.querySelector('span:first-child').textContent = 'Analyser l’avis';
    }
  });

  document.querySelector('#check-api').addEventListener('click', async () => {
    apiStatus.dataset.state = '';
    apiStatus.textContent = 'Vérification de la connexion…';
    try {
      const health = await request('/health');
      apiStatus.dataset.state = 'ok';
      apiStatus.textContent = `API disponible${health.model ? ` · ${health.model}` : ''}.`;
    } catch (error) {
      apiStatus.dataset.state = 'error';
      apiStatus.textContent = error.message || 'API injoignable.';
    }
  });
})();
