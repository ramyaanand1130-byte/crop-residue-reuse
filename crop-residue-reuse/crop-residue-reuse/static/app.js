/* Crop Residue Reuse Guide - front end.
 * Voice: browser Web Speech API (SpeechRecognition for answers, speechSynthesis for questions).
 * Everything the voice assistant hears is written into the same form that can be filled by hand.
 */
(function () {
  'use strict';

  var P = window.Parser;
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var synth = ('speechSynthesis' in window) ? window.speechSynthesis : null;

  // ---------------------------------------------------------------------
  // Text (Tamil / English)
  // ---------------------------------------------------------------------
  var STR = {
    ta: {
      skip_link: 'உள்ளடக்கத்திற்குச் செல்',
      app_title: 'பயிர்க் கழிவு மறுபயன்பாட்டு வழிகாட்டி',
      app_tag: 'கழிவை எரிக்காமல், பயனுள்ள வழியில் பயன்படுத்துங்கள்',
      tab_new: 'புதிய பரிந்துரை',
      tab_history: 'முந்தைய பதிவுகள்',
      voice_title: 'குரல் உதவியாளர்',
      voice_start: 'குரல் உதவியாளரைத் தொடங்கு',
      voice_resume: 'தொடர்ந்து பேசு',
      voice_stop: 'நிறுத்து',
      voice_idle: 'மைக்கை அழுத்தி, கேள்விகளுக்குப் பதில் சொல்லுங்கள். கீழே உள்ள படிவத்திலும் தேர்ந்தெடுக்கலாம்.',
      voice_listening: 'கேட்கிறேன்… பேசுங்கள்',
      voice_speaking: 'கேள்வியைச் சொல்கிறேன்…',
      voice_heard: 'கேட்டது:',
      voice_retry: 'மன்னிக்கவும், புரியவில்லை. மீண்டும் சொல்லுங்கள்.',
      voice_manual: 'குரல் மூலம் புரியவில்லை. கீழே உள்ள படிவத்தில் தேர்ந்தெடுத்து, பிறகு "தொடர்ந்து பேசு" அழுத்தவும்.',
      voice_unsupported: 'இந்த உலாவியில் குரல் உள்ளீடு இல்லை. Chrome அல்லது Edge பயன்படுத்தவும், அல்லது கீழே உள்ள படிவத்தை நிரப்பவும்.',
      voice_blocked: 'மைக்ரோஃபோன் அனுமதி இல்லை. உலாவியில் அனுமதி அளிக்கவும், அல்லது படிவத்தை நிரப்பவும்.',
      voice_network: 'குரல் அறிதலுக்கு இணைய இணைப்பு தேவை. இணைப்பைச் சரிபார்க்கவும்.',
      voice_no_tamil: 'இந்தச் சாதனத்தில் தமிழ் குரல் இல்லை; கேள்விகள் எழுத்தில் மட்டும் காட்டப்படும்.',
      voice_declined: 'சரி. விவரங்களைச் சரிபார்த்து, பச்சை பொத்தானை அழுத்தவும்.',
      q_crop: 'எந்தப் பயிரின் கழிவு உங்களிடம் உள்ளது? எடுத்துக்காட்டு: நெல், கரும்பு, நிலக்கடலை.',
      q_residue: 'எந்தக் கழிவு: {list}?',
      q_quantity: 'எவ்வளவு கழிவு உள்ளது? அளவைக் கூறுங்கள். எடுத்துக்காட்டு: 500 கிலோ அல்லது 2 டன்.',
      q_moisture: 'கழிவு எவ்வளவு ஈரமாக உள்ளது: உலர்ந்தது, சிறிது ஈரம், அல்லது ஈரமானது?',
      q_quality: 'கழிவின் தரம் எப்படி: நல்லது, சராசரி, அல்லது மோசம்?',
      q_location: 'உங்கள் வயல் எந்த ஊர் அல்லது மாவட்டத்தில் உள்ளது? சொல்ல விரும்பவில்லை என்றால் "வேண்டாம்" என்று சொல்லுங்கள்.',
      q_confirm: '{summary}. பரிந்துரைகளைக் காட்டலாமா? ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.',
      f_crop: 'பயிர்',
      f_residue: 'கழிவு வகை',
      f_quantity: 'அளவு',
      f_moisture: 'ஈரப்பதம்',
      f_quality: 'கழிவின் தரம்',
      f_location: 'இடம் (ஊர் அல்லது மாவட்டம்)',
      ph_quantity: 'எ.கா. 500',
      ph_location: 'எ.கா. தஞ்சாவூர்',
      pick_crop_first: 'முதலில் பயிரைத் தேர்ந்தெடுக்கவும்.',
      btn_submit: 'பரிந்துரைகளைப் பெறு',
      btn_clear: 'படிவத்தை அழி',
      submitting: 'பரிந்துரைகளைத் தயாரிக்கிறது…',
      err_required: 'தயவுசெய்து இவற்றை நிரப்பவும்: {fields}',
      err_network: 'சேவையகத்தை அடைய முடியவில்லை. பயன்பாடு இயங்குகிறதா எனப் பார்க்கவும்.',
      res_title: 'உங்களுக்கான பரிந்துரைகள்',
      res_steps: 'எப்படிச் செய்வது',
      res_precautions: 'முன்னெச்சரிக்கைகள்',
      res_more: 'படிகள் மற்றும் முன்னெச்சரிக்கைகள்',
      res_notes: 'உங்கள் நிலைக்கு ஏற்ப',
      res_general: 'நினைவில் கொள்ளுங்கள்',
      res_saved: 'இந்தப் பதிவு முந்தைய பதிவுகளில் சேமிக்கப்பட்டது.',
      level_high: 'மிகப் பொருத்தம்',
      level_medium: 'நல்ல பொருத்தம்',
      level_fair: 'சாத்தியம்',
      btn_read: 'படித்துக் காட்டு',
      btn_stop_read: 'படிப்பதை நிறுத்து',
      btn_print: 'அச்சிடு',
      hist_title: 'முந்தைய பதிவுகள்',
      hist_empty: 'இன்னும் பதிவுகள் இல்லை. முதல் பரிந்துரையைப் பெறுங்கள்.',
      hist_view: 'பார்',
      hist_delete: 'நீக்கு',
      hist_clear: 'அனைத்தையும் நீக்கு',
      hist_back: 'பட்டியலுக்குத் திரும்பு',
      hist_confirm_delete: 'இந்தப் பதிவை நீக்கவா?',
      hist_confirm_clear: 'எல்லாப் பதிவுகளையும் நீக்கவா?',
      hist_voice: 'குரல் மூலம்',
      hist_manual: 'கையால் உள்ளிட்டது',
      foot_note: 'பரிந்துரைகள் வேளாண் விதிகளின் அடிப்படையில் உருவாக்கப்படுகின்றன; பயிற்சி பெற்ற செயற்கை நுண்ணறிவு மாதிரியால் அல்ல.'
    },
    en: {
      skip_link: 'Skip to content',
      app_title: 'Crop Residue Reuse Guide',
      app_tag: 'Put your crop residue to good use instead of burning it',
      tab_new: 'New recommendation',
      tab_history: 'Past records',
      voice_title: 'Voice assistant',
      voice_start: 'Start voice assistant',
      voice_resume: 'Continue by voice',
      voice_stop: 'Stop',
      voice_idle: 'Press the mic and answer each question. You can also pick answers in the form below.',
      voice_listening: 'Listening… please speak',
      voice_speaking: 'Asking the question…',
      voice_heard: 'Heard:',
      voice_retry: 'Sorry, I did not catch that. Please say it again.',
      voice_manual: 'I could not understand by voice. Please choose in the form below, then press "Continue by voice".',
      voice_unsupported: 'Voice input is not supported in this browser. Use Chrome or Edge, or fill in the form below.',
      voice_blocked: 'Microphone access is blocked. Allow it in the browser, or fill in the form below.',
      voice_network: 'Speech recognition needs an internet connection. Please check it.',
      voice_no_tamil: 'This device has no Tamil voice, so questions are shown as text only.',
      voice_declined: 'Okay. Please review the details and press the green button.',
      q_crop: 'Which crop is the residue from? For example: paddy, sugarcane or groundnut.',
      q_residue: 'Which residue: {list}?',
      q_quantity: 'How much residue do you have? For example: 500 kilograms or 2 tonnes.',
      q_moisture: 'How wet is it: dry, slightly damp, or wet?',
      q_quality: 'What is its quality: good, average, or poor?',
      q_location: 'Which village or district is your farm in? Say "skip" if you prefer not to say.',
      q_confirm: '{summary}. Shall I show the recommendations? Say yes or no.',
      f_crop: 'Crop',
      f_residue: 'Residue type',
      f_quantity: 'Quantity',
      f_moisture: 'Moisture',
      f_quality: 'Residue quality',
      f_location: 'Location (village or district)',
      ph_quantity: 'e.g. 500',
      ph_location: 'e.g. Thanjavur',
      pick_crop_first: 'Choose a crop first.',
      btn_submit: 'Get recommendations',
      btn_clear: 'Clear form',
      submitting: 'Preparing recommendations…',
      err_required: 'Please fill in: {fields}',
      err_network: 'Could not reach the server. Check that the app is running.',
      res_title: 'Recommendations for you',
      res_steps: 'How to do it',
      res_precautions: 'Precautions',
      res_more: 'Steps and precautions',
      res_notes: 'For your situation',
      res_general: 'Good to know',
      res_saved: 'This record was saved to your past records.',
      level_high: 'Best fit',
      level_medium: 'Good fit',
      level_fair: 'Possible',
      btn_read: 'Read aloud',
      btn_stop_read: 'Stop reading',
      btn_print: 'Print',
      hist_title: 'Past records',
      hist_empty: 'No records yet. Get your first recommendation.',
      hist_view: 'View',
      hist_delete: 'Delete',
      hist_clear: 'Delete all',
      hist_back: 'Back to list',
      hist_confirm_delete: 'Delete this record?',
      hist_confirm_clear: 'Delete all records?',
      hist_voice: 'By voice',
      hist_manual: 'Typed or selected',
      foot_note: 'Recommendations come from fixed agricultural rules, not from a trained AI model.'
    }
  };

  // ---------------------------------------------------------------------
  // State and small helpers
  // ---------------------------------------------------------------------
  var lang = loadLang();
  var cat = null;                       // option catalog from /api/options
  var form = emptyForm();
  var usedVoice = false;
  var voice = { runId: 0, active: false, rec: null, skipLocation: false };
  var reading = { token: 0, on: false };
  var lastResult = null;                // {id, created_at, result} shown in #resultArea
  var historyItems = [];
  var historyDetail = null;

  function emptyForm() { return { crop: null, residue: null, quantity: '', unit: 'kg', moisture: null, quality: null, location: '' }; }
  function $(id) { return document.getElementById(id); }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function loadLang() {
    try { var v = localStorage.getItem('lang'); if (v === 'ta' || v === 'en') return v; } catch (e) { /* ignore */ }
    return 'ta';
  }
  function saveLang() { try { localStorage.setItem('lang', lang); } catch (e) { /* ignore */ } }

  function t(key, vars) {
    var s = (STR[lang] && STR[lang][key]) || STR.en[key] || key;
    if (vars) Object.keys(vars).forEach(function (k) { s = s.split('{' + k + '}').join(vars[k]); });
    return s;
  }

  // Create DOM safely: all text goes through textContent, never innerHTML.
  function h(tag, props) {
    var e = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (k) {
        var v = props[k];
        if (v === false || v === null || v === undefined) return;
        if (k === 'class') e.className = v;
        else if (k === 'text') e.textContent = v;
        else if (k === 'checked') e.checked = !!v;
        else if (k.indexOf('on') === 0) e.addEventListener(k.slice(2), v);
        else e.setAttribute(k, v === true ? '' : v);
      });
    }
    var kids = Array.prototype.slice.call(arguments, 2);
    (function add(list) {
      list.forEach(function (kid) {
        if (kid === null || kid === undefined || kid === false) return;
        if (Array.isArray(kid)) add(kid);
        else e.appendChild(kid.nodeType ? kid : document.createTextNode(String(kid)));
      });
    }(kids));
    return e;
  }

  function find(list, value) {
    for (var i = 0; i < list.length; i++) if (list[i].value === value) return list[i];
    return null;
  }
  var CAT_KEY = { crop: 'crops', residue: 'residues', moisture: 'moisture', quality: 'quality', unit: 'units' };
  function labelOf(kind, value) {
    var item = cat && find(cat[CAT_KEY[kind]], value);
    return item ? item.label[lang] : (value || '');
  }
  function residuesFor(cropValue) {
    var crop = cat && find(cat.crops, cropValue);
    if (!crop) return [];
    return crop.residues.map(function (v) { return find(cat.residues, v); }).filter(Boolean);
  }
  function quantityNumber() {
    var n = parseFloat(form.quantity);
    return (isFinite(n) && n > 0) ? n : null;
  }
  function fmtNum(n) { return String(parseFloat(Number(n).toFixed(2))); }

  // ---------------------------------------------------------------------
  // Static text and form rendering
  // ---------------------------------------------------------------------
  function applyStaticText() {
    document.documentElement.lang = lang;
    document.title = t('app_title');
    document.querySelectorAll('[data-i18n]').forEach(function (el) { el.textContent = t(el.getAttribute('data-i18n')); });
    $('quantity').placeholder = t('ph_quantity');
    $('location').placeholder = t('ph_location');
    document.querySelectorAll('.lang button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang));
    });
    updateMicLabel();
    if (!voice.active) setStatus(t('voice_idle'));
  }

  function renderGroup(name) {
    var box = $(name + 'Choices');
    var items;
    if (name === 'crop') items = cat.crops;
    else if (name === 'residue') items = form.crop ? residuesFor(form.crop) : [];
    else items = cat[name];
    box.replaceChildren();
    if (name === 'residue' && !form.crop) {
      box.classList.add('choices-note');
      box.appendChild(h('p', { text: t('pick_crop_first') }));
      return;
    }
    box.classList.remove('choices-note');
    items.forEach(function (it) {
      var icon = it.icon || null;
      box.appendChild(
        h('label', { class: 'chip' },
          h('input', {
            type: 'radio', name: name, value: it.value, checked: form[name] === it.value,
            onchange: function () { setField(name, it.value, false); }
          }),
          h('span', { class: 'chip-body' },
            icon ? h('span', { class: 'chip-icon', 'aria-hidden': 'true', text: icon }) : null,
            h('span', { class: 'chip-label', text: it.label[lang] }),
            it.hint ? h('span', { class: 'chip-hint', text: it.hint[lang] }) : null))
      );
    });
  }

  function renderUnits() {
    var sel = $('unit');
    sel.replaceChildren();
    cat.units.forEach(function (u) {
      sel.appendChild(h('option', { value: u.value, selected: form.unit === u.value, text: u.label[lang] }));
    });
    sel.value = form.unit;
  }

  function renderDistricts() {
    var dl = $('districtList');
    dl.replaceChildren();
    cat.districts.forEach(function (d) { dl.appendChild(h('option', { value: d })); });
  }

  function renderForm() {
    ['crop', 'residue', 'moisture', 'quality'].forEach(renderGroup);
    renderUnits();
    $('quantity').value = form.quantity;
    $('location').value = form.location;
    renderTags();
  }

  function renderTags() {
    var ul = $('voiceSummary');
    ul.replaceChildren();
    var items = [];
    if (form.crop) items.push(labelOf('crop', form.crop));
    if (form.residue) items.push(labelOf('residue', form.residue));
    if (quantityNumber()) items.push(fmtNum(quantityNumber()) + ' ' + labelOf('unit', form.unit));
    if (form.moisture) items.push(labelOf('moisture', form.moisture));
    if (form.quality) items.push(labelOf('quality', form.quality));
    if (form.location) items.push(form.location);
    items.forEach(function (text) { ul.appendChild(h('li', { text: text })); });
  }

  // ---------------------------------------------------------------------
  // Field setters (used by both manual input and voice)
  // ---------------------------------------------------------------------
  function setField(name, value, byVoice) {
    form[name] = value;
    if (byVoice) usedVoice = true;
    if (name === 'crop') {
      var list = residuesFor(value);
      var ok = list.some(function (r) { return r.value === form.residue; });
      if (!ok) form.residue = list.length === 1 ? list[0].value : null;
      renderGroup('residue');
    }
    if (byVoice) renderGroup(name);
    renderTags();
  }

  function setQuantity(value, unit, byVoice) {
    form.quantity = fmtNum(value);
    if (unit) form.unit = unit;
    if (byVoice) usedVoice = true;
    $('quantity').value = form.quantity;
    $('unit').value = form.unit;
    renderTags();
  }

  function setLocation(text, byVoice) {
    form.location = text;
    if (byVoice) usedVoice = true;
    $('location').value = text;
    renderTags();
  }

  function clearForm() {
    stopVoice();
    form = emptyForm();
    usedVoice = false;
    voice.skipLocation = false;
    renderForm();
    showFormError('');
    $('voiceHeard').textContent = '';
    $('voiceQuestion').textContent = '';
  }

  // ---------------------------------------------------------------------
  // Speech output
  // ---------------------------------------------------------------------
  function pickVoice(l) {
    if (!synth) return null;
    var voices = synth.getVoices() || [];
    var want = l === 'ta' ? 'ta' : 'en';
    var exact = l === 'ta' ? 'ta-in' : 'en-in';
    var best = null;
    for (var i = 0; i < voices.length; i++) {
      var vl = (voices[i].lang || '').toLowerCase().replace('_', '-');
      if (vl === exact) return voices[i];
      if (!best && vl.indexOf(want) === 0) best = voices[i];
    }
    return best;
  }

  function tamilVoiceMissing() {
    if (!synth || lang !== 'ta') return false;
    var voices = synth.getVoices() || [];
    return voices.length > 0 && !pickVoice('ta');
  }

  function speakOne(text) {
    return new Promise(function (resolve) {
      if (!synth || !text) { resolve(); return; }
      var u = new SpeechSynthesisUtterance(text);
      u.lang = lang === 'ta' ? 'ta-IN' : 'en-IN';
      var v = pickVoice(lang);
      if (v) u.voice = v;
      u.rate = 0.9;
      var finished = false;
      var guard = null;
      function done() { if (finished) return; finished = true; clearTimeout(guard); resolve(); }
      u.onend = done;
      u.onerror = done;
      guard = setTimeout(done, Math.max(5000, text.length * 160));
      try { synth.speak(u); } catch (e) { done(); }
    });
  }

  // Long text is split into sentences: some browsers cut off long utterances.
  function speak(text, alive) {
    var parts = String(text).match(/[^.!?।]+[.!?।]*/g) || [text];
    var chain = Promise.resolve();
    parts.forEach(function (p) {
      chain = chain.then(function () { return (alive && !alive()) ? null : speakOne(p.trim()); });
    });
    return chain;
  }

  function cancelSpeech() { if (synth) { try { synth.cancel(); } catch (e) { /* ignore */ } } }

  // ---------------------------------------------------------------------
  // Voice assistant
  // ---------------------------------------------------------------------
  function setStatus(text) { $('voiceStatus').textContent = text || ''; }
  function setNotice(text) {
    var el = $('voiceNotice');
    el.textContent = text || '';
    el.hidden = !text;
  }
  function setQuestion(text) { $('voiceQuestion').textContent = text || ''; }
  function setStage(state) {
    var s = $('micStage');
    s.classList.toggle('is-active', state !== 'idle');
    s.classList.toggle('is-listening', state === 'listening');
    s.classList.toggle('is-speaking', state === 'speaking');
  }
  function anyAnswered() { return !!(form.crop || form.residue || quantityNumber() || form.moisture || form.quality); }
  function updateMicLabel() {
    var key = voice.active ? 'voice_stop' : (anyAnswered() ? 'voice_resume' : 'voice_start');
    $('micLabel').textContent = t(key);
    $('micBtn').setAttribute('aria-label', t(key));
  }

  function alive(runId) { return voice.active && voice.runId === runId; }

  function stopVoice(message) {
    voice.runId++;
    voice.active = false;
    if (voice.rec) { try { voice.rec.abort(); } catch (e) { /* ignore */ } voice.rec = null; }
    cancelSpeech();
    reading.on = false; reading.token++;
    setReadButtons();
    setStage('idle');
    setStatus(t('voice_idle'));
    updateMicLabel();
    if (message) setNotice(message);
  }

  function listenOnce() {
    return new Promise(function (resolve) {
      var rec = new SR();
      voice.rec = rec;
      var finished = false;
      var timer = null;
      function finish(result) {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        if (voice.rec === rec) voice.rec = null;
        resolve(result);
      }
      rec.lang = lang === 'ta' ? 'ta-IN' : 'en-IN';
      rec.interimResults = false;
      rec.continuous = false;
      rec.maxAlternatives = 3;
      rec.onresult = function (e) {
        var out = [];
        for (var i = 0; i < e.results.length; i++) {
          for (var j = 0; j < e.results[i].length; j++) out.push(e.results[i][j].transcript);
        }
        finish({ transcripts: out, error: null });
      };
      rec.onerror = function (e) { finish({ transcripts: [], error: e.error }); };
      rec.onend = function () { finish({ transcripts: [], error: null }); };
      timer = setTimeout(function () { try { rec.stop(); } catch (e) { /* ignore */ } }, 10000);
      try { rec.start(); } catch (err) { finish({ transcripts: [], error: 'start-failed' }); }
    });
  }

  function firstMatch(texts, fn) {
    for (var i = 0; i < texts.length; i++) {
      var v = fn(texts[i]);
      if (v !== null && v !== undefined) return v;
    }
    return null;
  }

  function summaryText() {
    var parts = [labelOf('crop', form.crop), labelOf('residue', form.residue),
      fmtNum(quantityNumber()) + ' ' + labelOf('unit', form.unit),
      labelOf('moisture', form.moisture), labelOf('quality', form.quality)];
    if (form.location) parts.push(form.location);
    return parts.join(', ');
  }

  var STEPS = {
    crop: {
      question: function () { return t('q_crop'); },
      parse: function (texts) { return firstMatch(texts, function (x) { return P.matchOption(x, cat.crops); }); },
      apply: function (v) { setField('crop', v, true); },
      describe: function (v) { return labelOf('crop', v); }
    },
    residue: {
      question: function () {
        return t('q_residue', { list: residuesFor(form.crop).map(function (r) { return r.label[lang]; }).join(lang === 'ta' ? ', ' : ', ') });
      },
      parse: function (texts) {
        var opts = residuesFor(form.crop);
        return firstMatch(texts, function (x) { return P.matchOption(x, opts); });
      },
      apply: function (v) { setField('residue', v, true); },
      describe: function (v) { return labelOf('residue', v); }
    },
    quantity: {
      question: function () { return t('q_quantity'); },
      parse: function (texts) { return firstMatch(texts, function (x) { return P.parseQuantity(x); }); },
      apply: function (q) { setQuantity(q.value, q.unit, true); },
      describe: function (q) { return fmtNum(q.value) + ' ' + labelOf('unit', q.unit || form.unit); }
    },
    moisture: {
      question: function () { return t('q_moisture'); },
      parse: function (texts) { return firstMatch(texts, function (x) { return P.matchOption(x, cat.moisture); }); },
      apply: function (v) { setField('moisture', v, true); },
      describe: function (v) { return labelOf('moisture', v); }
    },
    quality: {
      question: function () { return t('q_quality'); },
      parse: function (texts) {
        return firstMatch(texts, function (x) { return P.matchOption(x, cat.quality, { negatedValues: ['poor'] }); });
      },
      apply: function (v) { setField('quality', v, true); },
      describe: function (v) { return labelOf('quality', v); }
    },
    location: {
      question: function () { return t('q_location'); },
      parse: function (texts) {
        var x = String(texts[0] || '').replace(/[.,!?।]+$/g, '').trim();
        if (!x) return null;
        return P.isSkip(x) ? { skip: true } : { text: x.slice(0, 100) };
      },
      apply: function (v) { if (v.skip) voice.skipLocation = true; else setLocation(v.text, true); },
      describe: function (v) { return v.skip ? '-' : v.text; }
    },
    confirm: {
      question: function () { return t('q_confirm', { summary: summaryText() }); },
      parse: function (texts) { return firstMatch(texts, function (x) { return P.parseYesNo(x); }); },
      apply: function () { /* handled by caller */ },
      describe: function (v) { return v; }
    }
  };

  function nextStep() {
    if (!form.crop) return 'crop';
    if (!form.residue) return 'residue';
    if (!quantityNumber()) return 'quantity';
    if (!form.moisture) return 'moisture';
    if (!form.quality) return 'quality';
    if (!form.location && !voice.skipLocation) return 'location';
    return 'confirm';
  }

  // Ask one question (with up to 3 tries). Returns {status: 'ok'|'fail'|'stop', value}.
  async function askStep(step, runId) {
    var def = STEPS[step];
    var question = def.question();
    setQuestion(question);
    for (var attempt = 0; attempt < 3; attempt++) {
      if (!alive(runId)) return { status: 'stop' };
      setStage('speaking');
      setStatus(t('voice_speaking'));
      await speak(attempt === 0 ? question : t('voice_retry'), function () { return alive(runId); });
      if (!alive(runId)) return { status: 'stop' };
      await sleep(250);
      if (!alive(runId)) return { status: 'stop' };
      setStage('listening');
      setStatus(t('voice_listening'));
      var res = await listenOnce();
      if (!alive(runId)) return { status: 'stop' };
      if (res.error === 'not-allowed' || res.error === 'service-not-allowed') { setNotice(t('voice_blocked')); return { status: 'stop-notice' }; }
      if (res.error === 'network') { setNotice(t('voice_network')); return { status: 'stop-notice' }; }
      if (!res.transcripts.length) continue;
      $('voiceHeard').textContent = t('voice_heard') + ' “' + res.transcripts[0] + '”';
      var parsed = def.parse(res.transcripts);
      if (parsed !== null && parsed !== undefined) {
        def.apply(parsed);
        if (step !== 'confirm') $('voiceHeard').textContent += '  →  ' + def.describe(parsed);
        return { status: 'ok', value: parsed };
      }
    }
    return { status: 'fail' };
  }

  async function runVoice() {
    var runId = ++voice.runId;
    voice.active = true;
    setNotice(tamilVoiceMissing() ? t('voice_no_tamil') : '');
    updateMicLabel();
    $('voiceHeard').textContent = '';
    var wantSubmit = false;
    try {
      while (alive(runId)) {
        var step = nextStep();
        var r = await askStep(step, runId);
        if (r.status === 'stop') return;
        if (r.status === 'stop-notice') { stopVoice(); setNotice($('voiceNotice').textContent); return; }
        if (r.status === 'fail') { stopVoice(t('voice_manual')); return; }
        if (step === 'confirm') {
          if (r.value === 'yes') { wantSubmit = true; break; }
          stopVoice(t('voice_declined'));
          return;
        }
      }
    } finally {
      if (voice.runId === runId && voice.active) {
        voice.active = false;
        setStage('idle');
        setStatus(t('voice_idle'));
        updateMicLabel();
      }
    }
    if (wantSubmit) await submit(true);
  }

  function startVoice() {
    if (!SR) { setNotice(t('voice_unsupported')); return; }
    stopVoice();
    runVoice();
  }

  // ---------------------------------------------------------------------
  // Submit and results
  // ---------------------------------------------------------------------
  function showFormError(msg) {
    var el = $('formError');
    el.textContent = msg || '';
    el.hidden = !msg;
  }

  async function api(path, options) {
    try {
      var resp = await fetch(path, options);
      var data = null;
      try { data = await resp.json(); } catch (e) { /* no body */ }
      return { ok: resp.ok, status: resp.status, data: data };
    } catch (e) {
      return { ok: false, status: 0, data: null };
    }
  }

  function errorText(res) {
    if (res.status === 0) return t('err_network');
    var e = res.data && res.data.error;
    return (e && (e[lang] || e.en)) || t('err_network');
  }

  async function submit(autoRead) {
    var missing = [];
    if (!form.crop) missing.push(t('f_crop'));
    if (!form.residue) missing.push(t('f_residue'));
    if (!quantityNumber()) missing.push(t('f_quantity'));
    if (!form.moisture) missing.push(t('f_moisture'));
    if (!form.quality) missing.push(t('f_quality'));
    if (missing.length) { showFormError(t('err_required', { fields: missing.join(', ') })); return false; }
    showFormError('');

    var btn = $('submitBtn');
    btn.disabled = true;
    btn.textContent = t('submitting');
    var res = await api('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crop: form.crop, residue: form.residue, quantity: quantityNumber(), unit: form.unit,
        moisture: form.moisture, quality: form.quality, location: form.location.trim(),
        language: lang, input_method: usedVoice ? 'voice' : 'manual'
      })
    });
    btn.disabled = false;
    btn.textContent = t('btn_submit');

    if (!res.ok) { showFormError(errorText(res)); return false; }

    lastResult = res.data;
    usedVoice = false;
    var area = $('resultArea');
    area.hidden = false;
    renderResult(area, lastResult, true);
    var title = area.querySelector('h2');
    if (title) { title.setAttribute('tabindex', '-1'); title.focus({ preventScroll: true }); }
    area.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (autoRead) readResult(lastResult);
    return true;
  }

  function levelBadge(level) {
    return h('span', { class: 'badge badge-' + level, text: t('level_' + level) });
  }

  function recCard(rec, isTop) {
    var more = h('details', { class: 'rec-more', open: isTop },
      h('summary', { text: t('res_more') }),
      h('h4', { text: t('res_steps') }),
      h('ol', null, rec.steps[lang].map(function (s) { return h('li', { text: s }); })),
      h('h4', { text: t('res_precautions') }),
      h('ul', null, rec.precautions[lang].map(function (s) { return h('li', { text: s }); })));
    var notes = rec.notes[lang].length
      ? h('ul', { class: 'rec-notes', 'aria-label': t('res_notes') },
          rec.notes[lang].map(function (n) { return h('li', { text: n }); }))
      : null;
    return h('li', { class: 'rec' + (isTop ? ' rec--top' : '') },
      h('div', { class: 'rec-head' },
        h('span', { class: 'rec-icon', 'aria-hidden': 'true', text: rec.icon }),
        h('h3', { text: rec.title[lang] }),
        levelBadge(rec.level)),
      h('p', { class: 'rec-desc', text: rec.description[lang] }),
      notes,
      more);
  }

  function renderResult(container, data, justSaved) {
    var r = data.result;
    container.replaceChildren(
      h('h2', { text: t('res_title') }),
      h('p', { class: 'res-summary', text: r.summary[lang] }),
      h('div', { class: 'res-actions' },
        h('button', { type: 'button', class: 'btn btn-quiet btn-small js-read', onclick: function () { toggleRead(data); }, text: t('btn_read') }),
        h('button', { type: 'button', class: 'btn btn-quiet btn-small', onclick: function () { window.print(); }, text: t('btn_print') })),
      h('ol', { class: 'recs' }, r.recommendations.map(function (rec, i) { return recCard(rec, i === 0); })),
      h('div', { class: 'res-general' },
        h('h3', { text: t('res_general') }),
        h('ul', null, r.general_precautions[lang].map(function (s) { return h('li', { text: s }); }))),
      h('p', { class: 'res-tip', text: r.location_tip[lang] }),
      justSaved ? h('p', { class: 'res-saved', text: t('res_saved') }) : null);
    setReadButtons();
  }

  // ---------------------------------------------------------------------
  // Read results aloud
  // ---------------------------------------------------------------------
  function resultChunks(data) {
    var r = data.result, chunks = [r.summary[lang]];
    r.recommendations.forEach(function (rec, i) {
      chunks.push((i + 1) + '. ' + rec.title[lang] + '. ' + rec.description[lang]);
      rec.notes[lang].forEach(function (n) { chunks.push(n); });
      chunks.push(t('res_precautions') + ': ' + rec.precautions[lang].join(' '));
    });
    chunks.push(r.general_precautions[lang][0]);
    return chunks;
  }

  function setReadButtons() {
    document.querySelectorAll('.js-read').forEach(function (b) {
      b.textContent = reading.on ? t('btn_stop_read') : t('btn_read');
    });
  }

  async function readResult(data) {
    cancelSpeech();
    var token = ++reading.token;
    reading.on = true;
    setReadButtons();
    var chunks = resultChunks(data);
    for (var i = 0; i < chunks.length; i++) {
      if (reading.token !== token) return;
      await speak(chunks[i], function () { return reading.token === token; });
    }
    if (reading.token === token) { reading.on = false; setReadButtons(); }
  }

  function toggleRead(data) {
    if (reading.on) { reading.token++; reading.on = false; cancelSpeech(); setReadButtons(); }
    else readResult(data);
  }

  // ---------------------------------------------------------------------
  // History
  // ---------------------------------------------------------------------
  function fmtDate(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    try { return d.toLocaleString(lang === 'ta' ? 'ta-IN' : 'en-IN', { dateStyle: 'medium', timeStyle: 'short' }); }
    catch (e) { return d.toLocaleString(); }
  }

  function setHistoryError(msg) {
    var el = $('historyError');
    el.textContent = msg || '';
    el.hidden = !msg;
  }

  async function loadHistory() {
    setHistoryError('');
    var res = await api('/api/history');
    if (!res.ok) { setHistoryError(errorText(res)); return; }
    historyItems = res.data.items;
    renderHistory();
  }

  function historyRow(it) {
    return h('li', { class: 'hist-item' },
      h('h3', { text: labelOf('residue', it.residue) }),
      h('div', { class: 'hist-meta' },
        h('span', { text: fmtDate(it.created_at) }),
        h('span', { text: fmtNum(it.quantity) + ' ' + labelOf('unit', it.unit) }),
        it.location ? h('span', { text: it.location }) : null,
        h('span', { text: it.input_method === 'voice' ? t('hist_voice') : t('hist_manual') })),
      h('ul', { class: 'hist-top' }, it.top.map(function (r) { return h('li', { text: r.icon + ' ' + r.title[lang] }); })),
      h('div', { class: 'hist-actions' },
        h('button', { type: 'button', class: 'btn btn-quiet btn-small', onclick: function () { openHistory(it.id); }, text: t('hist_view') }),
        h('button', { type: 'button', class: 'btn btn-quiet btn-small', onclick: function () { deleteHistory(it.id); }, text: t('hist_delete') })));
  }

  function renderHistory() {
    var list = $('historyList');
    list.replaceChildren();
    historyItems.forEach(function (it) { list.appendChild(historyRow(it)); });
    $('historyEmpty').hidden = historyItems.length > 0;
    $('historyClear').hidden = historyItems.length === 0;
  }

  function showHistoryDetail(data) {
    historyDetail = data;
    var box = $('historyDetail');
    renderResult(box, data, false);
    box.insertBefore(
      h('button', { type: 'button', class: 'btn btn-quiet btn-small', onclick: closeHistoryDetail, text: t('hist_back') }),
      box.firstChild);
    box.hidden = false;
    $('historyList').hidden = true;
    $('historyClear').hidden = true;
    $('historyEmpty').hidden = true;
    box.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function closeHistoryDetail() {
    historyDetail = null;
    $('historyDetail').hidden = true;
    $('historyList').hidden = false;
    reading.token++; reading.on = false; cancelSpeech();
    renderHistory();
  }

  async function openHistory(id) {
    setHistoryError('');
    var res = await api('/api/history/' + id);
    if (!res.ok) { setHistoryError(errorText(res)); return; }
    showHistoryDetail(res.data);
  }

  async function deleteHistory(id) {
    if (!window.confirm(t('hist_confirm_delete'))) return;
    var res = await api('/api/history/' + id, { method: 'DELETE' });
    if (!res.ok) { setHistoryError(errorText(res)); return; }
    historyItems = historyItems.filter(function (x) { return x.id !== id; });
    renderHistory();
  }

  async function clearHistory() {
    if (!window.confirm(t('hist_confirm_clear'))) return;
    var res = await api('/api/history', { method: 'DELETE' });
    if (!res.ok) { setHistoryError(errorText(res)); return; }
    historyItems = [];
    renderHistory();
  }

  // ---------------------------------------------------------------------
  // Tabs, language, start-up
  // ---------------------------------------------------------------------
  function showTab(name) {
    var isNew = name === 'new';
    $('tabNew').hidden = !isNew;
    $('tabHistory').hidden = isNew;
    $('tabBtnNew').setAttribute('aria-selected', String(isNew));
    $('tabBtnHistory').setAttribute('aria-selected', String(!isNew));
    if (!isNew) { stopVoice(); loadHistory(); }
  }

  function setLang(next) {
    if (next === lang) return;
    stopVoice();
    lang = next;
    saveLang();
    applyStaticText();
    if (cat) renderForm();
    $('submitBtn').textContent = t('btn_submit');
    if (lastResult) renderResult($('resultArea'), lastResult, false);
    if (historyDetail) showHistoryDetail(historyDetail);
    else if (!$('tabHistory').hidden) renderHistory();
  }

  function buildRing() {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 200 200');
    svg.setAttribute('class', 'ring');
    svg.setAttribute('aria-hidden', 'true');
    function dot(cls, i, n, radius, size) {
      var a = (i / n) * 2 * Math.PI;
      var c = document.createElementNS(NS, 'circle');
      c.setAttribute('class', cls);
      c.setAttribute('cx', (100 + radius * Math.cos(a)).toFixed(2));
      c.setAttribute('cy', (100 + radius * Math.sin(a)).toFixed(2));
      c.setAttribute('r', String(size));
      c.style.setProperty('--i', String(i));
      svg.appendChild(c);
    }
    var i;
    for (i = 0; i < 24; i++) dot('outer', i, 24, 90, i % 2 ? 3 : 4.5);
    for (i = 0; i < 12; i++) dot('inner', i, 12, 74, 2.5);
    $('micStage').insertBefore(svg, $('micBtn'));
  }

  function bindEvents() {
    document.querySelectorAll('.lang button').forEach(function (b) {
      b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
    });
    $('tabBtnNew').addEventListener('click', function () { showTab('new'); });
    $('tabBtnHistory').addEventListener('click', function () { showTab('history'); });
    $('micBtn').addEventListener('click', function () { if (voice.active) stopVoice(); else startVoice(); });
    $('quantity').addEventListener('input', function (e) { form.quantity = e.target.value; renderTags(); updateMicLabel(); });
    $('unit').addEventListener('change', function (e) { form.unit = e.target.value; renderTags(); });
    $('location').addEventListener('input', function (e) { form.location = e.target.value; renderTags(); });
    $('residueForm').addEventListener('submit', function (e) { e.preventDefault(); submit(false); });
    $('clearBtn').addEventListener('click', clearForm);
    $('historyClear').addEventListener('click', clearHistory);
    window.addEventListener('beforeprint', function () {
      document.querySelectorAll('details.rec-more').forEach(function (d) { d.open = true; });
    });
    if (synth && synth.addEventListener) {
      synth.addEventListener('voiceschanged', function () {
        if (tamilVoiceMissing() && !voice.active) setNotice(t('voice_no_tamil'));
      });
    }
  }

  async function init() {
    buildRing();
    bindEvents();
    applyStaticText();
    var res = await api('/api/options');
    if (!res.ok) { setNotice(t('err_network')); return; }
    cat = res.data;
    renderDistricts();
    renderForm();
    if (!SR) setNotice(t('voice_unsupported'));
  }

  init();
}());
