/* Speech-text helpers: match a spoken phrase to a form choice, and read numbers.
 * Works in the browser (window.Parser) and in Node (module.exports) so it can be tested.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Parser = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var TAMIL_DIGITS = { '௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4', '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9' };

  function toAsciiDigits(s) {
    return s.replace(/[௦-௯]/g, function (d) { return TAMIL_DIGITS[d]; });
  }

  // Lower-case, Tamil digits -> ASCII, punctuation -> space.
  function normalize(text, keepDecimal) {
    var s = toAsciiDigits(String(text == null ? '' : text).normalize('NFC').toLowerCase());
    if (keepDecimal) {
      s = s.replace(/(\d),(?=\d{3}(\D|$))/g, '$1');           // 1,000 -> 1000
      s = s.replace(/\./g, function (m, off, str) {            // keep only decimal points
        return (/\d/.test(str[off - 1] || '') && /\d/.test(str[off + 1] || '')) ? '.' : ' ';
      });
      s = s.replace(/[,!?;:"“”‘’()]/g, ' ');
    } else {
      s = s.replace(/[.,!?;:"“”‘’()]/g, ' ');
    }
    return s.replace(/\s+/g, ' ').trim();
  }

  function isAscii(s) { return /^[\x00-\x7f]+$/.test(s); }

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  // ASCII keywords must match whole words (optionally plural); Tamil keywords match as substrings.
  function hasKeyword(text, kw) {
    if (!kw) return false;
    if (isAscii(kw)) {
      return new RegExp('(^|[^a-z])' + escapeRe(kw) + '(s|es)?($|[^a-z])').test(text);
    }
    return text.indexOf(kw) !== -1;
  }

  var NEGATION = /(இல்லை|இல்ல|இல்லாத|இல்லாமல்)|(^|[^a-z])(no|not|without|never)($|[^a-z])/;

  /* options: [{value, keywords:[...]}]. Returns the value whose longest matching
   * keyword is longest; null when nothing matches or two options tie.
   * config.negatedValues: values to ignore when the phrase is negated ("no mold").
   */
  function matchOption(text, options, config) {
    var t = normalize(text);
    if (!t) return null;
    var negated = config && config.negatedValues && NEGATION.test(t);
    var best = null, bestLen = 0, tie = false;
    for (var i = 0; i < options.length; i++) {
      var opt = options[i];
      if (negated && config.negatedValues.indexOf(opt.value) !== -1) continue;
      var len = 0;
      var kws = opt.keywords || [];
      for (var j = 0; j < kws.length; j++) {
        var k = normalize(kws[j]);
        if (k.length > len && hasKeyword(t, k)) len = k.length;
      }
      if (len > bestLen) { best = opt.value; bestLen = len; tie = false; }
      else if (len > 0 && len === bestLen && opt.value !== best) tie = true;
    }
    return (best !== null && !tie) ? best : null;
  }

  // --- numbers -------------------------------------------------------------

  var WORDS = {
    // English
    zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
    eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17,
    eighteen: 18, nineteen: 19, twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60,
    seventy: 70, eighty: 80, ninety: 90, half: 0.5,
    // Tamil
    'ஒன்று': 1, 'ஒரு': 1, 'இரண்டு': 2, 'இரு': 2, 'மூன்று': 3, 'மூணு': 3, 'நான்கு': 4, 'நாலு': 4,
    'ஐந்து': 5, 'அஞ்சு': 5, 'ஆறு': 6, 'ஏழு': 7, 'எட்டு': 8, 'ஒன்பது': 9, 'பத்து': 10,
    'இருபது': 20, 'முப்பது': 30, 'நாற்பது': 40, 'ஐம்பது': 50, 'அறுபது': 60, 'எழுபது': 70,
    'எண்பது': 80, 'தொண்ணூறு': 90,
    'நூறு': 100, 'இருநூறு': 200, 'முன்னூறு': 300, 'முந்நூறு': 300, 'நானூறு': 400,
    'ஐநூறு': 500, 'ஐந்நூறு': 500, 'அறுநூறு': 600, 'எழுநூறு': 700, 'எண்ணூறு': 800,
    'தொள்ளாயிரம்': 900,
    'அரை': 0.5, 'ஒன்றரை': 1.5, 'இரண்டரை': 2.5, 'மூன்றரை': 3.5,
    'இரண்டாயிரம்': 2000, 'மூவாயிரம்': 3000, 'நாலாயிரம்': 4000, 'நான்காயிரம்': 4000,
    'ஐயாயிரம்': 5000, 'ஆறாயிரம்': 6000, 'ஏழாயிரம்': 7000, 'எட்டாயிரம்': 8000,
    'ஒன்பதாயிரம்': 9000, 'பத்தாயிரம்': 10000
  };
  var THOUSAND = { thousand: 1, 'ஆயிரம்': 1, 'ஆயிரத்து': 1 };

  function wordsToNumber(t) {
    var tokens = t.split(' ');
    var total = 0, current = 0, found = false;
    for (var i = 0; i < tokens.length; i++) {
      var tok = tokens[i];
      if (Object.prototype.hasOwnProperty.call(WORDS, tok)) { current += WORDS[tok]; found = true; }
      else if (tok === 'hundred') { current = (current || 1) * 100; found = true; }
      else if (THOUSAND[tok]) { total += (current || 1) * 1000; current = 0; found = true; }
    }
    return found ? total + current : null;
  }

  var UNIT_OPTIONS = [
    { value: 'kg', keywords: ['கிலோ', 'கிகி', 'kg', 'kilo', 'kilogram'] },
    { value: 'quintal', keywords: ['குவிண்டால்', 'குவின்டால்', 'குயின்டால்', 'quintal'] },
    { value: 'tonne', keywords: ['டன்', 'ton', 'tonne'] }
  ];

  /* Returns {value:number, unit:'kg'|'quintal'|'tonne'|null} or null. */
  function parseQuantity(text) {
    var t = normalize(text, true);
    if (!t) return null;
    var value = null;
    var m = t.match(/\d+(?:\.\d+)?/);
    if (m) value = parseFloat(m[0]);
    else value = wordsToNumber(t);
    if (value === null || !isFinite(value) || value <= 0) return null;
    return { value: value, unit: matchOption(t, UNIT_OPTIONS) };
  }

  var YES_NO = [
    { value: 'yes', keywords: ['ஆம்', 'ஆமாம்', 'சரி', 'காட்டு', 'yes', 'yeah', 'ok', 'okay', 'correct', 'sure', 'show'] },
    { value: 'no', keywords: ['இல்லை', 'இல்ல', 'வேண்டாம்', 'வேணாம்', 'no', 'nope', 'not', 'stop'] }
  ];
  function parseYesNo(text) { return matchOption(text, YES_NO); }

  var SKIP = [{ value: 'skip', keywords: ['தெரியாது', 'வேண்டாம்', 'இல்லை', 'skip', 'no', 'none', 'not sure', 'pass'] }];
  function isSkip(text) { return matchOption(text, SKIP) === 'skip'; }

  return {
    normalize: normalize,
    matchOption: matchOption,
    parseQuantity: parseQuantity,
    parseYesNo: parseYesNo,
    isSkip: isSkip
  };
}));
