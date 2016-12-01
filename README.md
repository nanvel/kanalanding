# Japanese Kana app landing page

## JS

JS compile:
```bash
babel static/app.js -o static/app.min.js -s --presets=es2015,stage-0,babili --no-babelrc
```

## Server

Run server:
```bash
gunicorn -b 0.0.0.0:8080 -k aiohttp.worker.GunicornWebWorker -w 2 -t 60 app:app --env=APP_EMAIL=... --env RECAPTCHA_SITE_KEY=... --env RECAPTCHA_SECRET_KEY=... --reload
```

Fake mail server:
```bash
python -m smtpd -n -c DebuggingServer localhost:1025
```
