# Smart Crop Residue Reuse Recommendation System with Tamil Voice Assistant

A Flask + SQLite web app that helps farmers decide how to reuse crop residue
(compost, mulching, animal feed, biochar, briquettes and more) instead of burning it.
The farmer can speak in Tamil or English, or fill the form by hand.

## How to run

1. Install Python 3.9 or newer.
2. Open a terminal in this folder and run:

```
pip install -r requirements.txt
python app.py
```

3. Open **http://127.0.0.1:5000** in **Google Chrome or Microsoft Edge**.

Use `localhost` or `127.0.0.1` (not your network IP) so the browser allows the microphone.

### Opening it on a phone

`127.0.0.1` on a phone means the phone itself, so it will say "This site can't be reached".

- **Same Wi-Fi:** run `python app.py --share` on the computer, then open `http://<computer-IP>:5000` on the phone.
  The form and recommendations work. Chrome blocks the microphone on plain `http://` addresses; to allow it, open
  `chrome://flags`, search "Insecure origins treated as secure", add `http://<computer-IP>:5000`, enable it and relaunch.
- **Full voice on the phone:** host the app on a free HTTPS service such as PythonAnywhere or Render, or run it inside Termux on the phone and open `http://localhost:5000` in Chrome.
- Use Chrome on Android. Opera and some other browsers do not support speech recognition.

## Features

| Feature | How it works |
|---|---|
| Voice questions (Tamil / English) | Browser `speechSynthesis` reads each question aloud |
| Voice answers | Browser `SpeechRecognition` (Web Speech API) turns speech into text |
| Manual fallback | Every question is also a form field; voice and typing fill the same form |
| Inputs collected | Crop, residue type, quantity (kg / quintal / tonne), moisture, quality, location |
| Recommendations | Rule-based scoring (no trained AI model), with steps and precautions |
| Read results aloud | "Read aloud" button on the results page |
| Storage | Every submission is saved in SQLite (`data/records.db`) |
| History | View, reopen or delete earlier recommendations |

## Project structure

```
app.py              Flask server, REST API, SQLite
recommender.py      Rule engine + all Tamil/English content
templates/index.html
static/style.css
static/app.js       Form, voice assistant, results, history
static/parser.js    Turns spoken text into form choices and numbers
data/               SQLite database is created here on first run
```

## API

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/options` | Crops, residues, units, districts |
| POST | `/api/recommend` | Validate, recommend and save |
| GET | `/api/history` | Last 100 records |
| GET / DELETE | `/api/history/<id>` | One record |
| DELETE | `/api/history` | Delete all |

## How the rules work

For each reuse option the score is:

`base suitability for the residue + moisture adjustment + quality adjustment + quantity adjustment`

Options scoring 5 or more are shown (best four). Poor-quality residue never gets
animal-feed or mushroom advice. Edit the tables in `recommender.py`
(`_BASE_ROWS`, `MODIFIERS`, `NOTES`) to change the behaviour.

## Notes

- Voice recognition in Chrome and Edge sends audio to the browser vendor's speech service, so it needs internet.
- Tamil speech output needs a Tamil voice on the device (Android and Windows usually have one). If none exists, questions are shown as text.
- If voice fails three times on a question, the assistant stops and asks the farmer to use the form.
- The app is for learning and decision support. Farmers should confirm large-scale plans with a local Krishi Vigyan Kendra (KVK).
