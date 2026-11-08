/* Health Center — enhancement: speech, chips, validation, loading */
(function () {
  'use strict';

  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  var form = document.getElementById('predict-form');
  var input = document.getElementById('symptoms');
  var errorEl = document.getElementById('symptoms-error');
  var submitBtn = document.getElementById('submit-btn');
  var clearBtn = document.getElementById('clear-btn');
  var speechBtn = document.getElementById('startSpeechRecognition');
  var transcription = document.getElementById('transcription');
  var speechStatus = document.getElementById('speech-status');

  function setError(msg) {
    if (errorEl) errorEl.textContent = msg || '';
    if (input) {
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
      if (msg) input.focus();
    }
  }

  function normalizeChips() {
    if (!input) return;
    var chips = document.querySelectorAll('[data-symptom-chip]');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var symptom = chip.getAttribute('data-symptom-chip');
        if (!symptom) return;
        var current = input.value.trim();
        var parts = current ? current.split(',').map(function (s) { return s.trim(); }).filter(Boolean) : [];
        if (parts.map(function (s) { return s.toLowerCase(); }).indexOf(symptom.toLowerCase()) === -1) {
          parts.push(symptom);
        }
        input.value = parts.join(', ');
        input.focus();
        setError('');
      });
    });
  }

  function validate() {
    if (!input || !form) return true;
    var raw = input.value.trim();
    if (!raw) {
      setError('Please enter at least one symptom (e.g. itching, cough, high_fever).');
      return false;
    }
    var parts = raw.split(',').map(function (s) { return s.trim(); }).filter(Boolean);
    if (parts.length === 0) {
      setError('Please enter at least one symptom.');
      return false;
    }
    if (parts.length > 30) {
      setError('Please enter at most 30 symptoms.');
      return false;
    }
    if (raw.length > 2000) {
      setError('Input is too long. Please keep it under 2,000 characters.');
      return false;
    }
    setError('');
    return true;
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      if (!validate()) {
        e.preventDefault();
        return;
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-inline" role="status" aria-hidden="true"></span>Analyzing…';
      }
    });
  }

  if (clearBtn && input) {
    clearBtn.addEventListener('click', function () {
      input.value = '';
      setError('');
      if (transcription) transcription.textContent = '';
      input.focus();
    });
  }

  if (input) {
    input.addEventListener('input', function () {
      if (errorEl && errorEl.textContent) setError('');
    });
  }

  normalizeChips();

  /* Speech recognition — graceful fallback */
  function SpeechProxy() {}
  SpeechProxy.Supported = function () {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  };
  SpeechProxy.create = function () {
    var Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    return new Ctor();
  };

  if (speechBtn) {
    if (!SpeechProxy.Supported()) {
      speechBtn.disabled = true;
      speechBtn.title = 'Speech recognition is not supported in this browser. Use manual input or Chrome.';
      if (speechStatus) speechStatus.textContent = 'Speech input is not supported in this browser — please type your symptoms.';
    } else {
      speechBtn.addEventListener('click', function () {
        var recognition = SpeechProxy.create();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        function resetBtn() {
          speechBtn.innerHTML = '<i class="fas fa-microphone" aria-hidden="true"></i> Speak Your Symptoms';
          speechBtn.classList.remove('listening');
          speechBtn.removeAttribute('aria-pressed');
        }

        speechBtn.innerHTML = '<i class="fas fa-microphone-lines" aria-hidden="true"></i> Listening…';
        speechBtn.classList.add('listening');
        speechBtn.setAttribute('aria-pressed', 'true');
        if (speechStatus) speechStatus.textContent = 'Listening… speak your symptoms.';

        recognition.onresult = function (event) {
          var result = event.results[0][0].transcript;
          if (transcription) transcription.textContent = result;
          if (input) input.value = result;
          if (speechStatus) speechStatus.textContent = 'Heard: ' + result;
          setError('');
        };
        recognition.onend = function () {
          resetBtn();
          if (speechStatus && speechStatus.textContent.indexOf('Listening') === 0) {
            speechStatus.textContent = '';
          }
        };
        recognition.onerror = function (event) {
          resetBtn();
          var msg = 'Speech error: ' + (event && event.error ? event.error : 'unknown');
          if (speechStatus) speechStatus.textContent = msg;
          if (transcription) transcription.textContent = '';
        };
        try {
          recognition.start();
        } catch (err) {
          resetBtn();
          if (speechStatus) speechStatus.textContent = 'Could not start speech recognition.';
        }
      });
    }
  }
})();
