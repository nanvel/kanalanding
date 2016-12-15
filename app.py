"""
gunicorn -b 0.0.0.0:8080 -k aiohttp.worker.GunicornWebWorker -w 2 -t 60 app:app --env=APP_EMAIL=... --env RECAPTCHA_SITE_KEY=... --env RECAPTCHA_SECRET_KEY=... --reload
"""

import aiosmtplib
import asyncio
import ujson
import os
import re

from aiohttp import web, ClientSession, errors


RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
SMTP_PORT = os.getenv('SMTP_PORT', 1025)
APP_EMAIL = os.getenv('APP_EMAIL')


EMAIL_REGEXP = re.compile(r"[^@]+@[^@]+\.[^@]+")


class RecaptchaError(errors.HttpProcessingError):

    code = 400
    message = "Recaptcha error"


async def index(request):
    with open("static/index.html", 'r') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def feedback(request):

    if not APP_EMAIL:
        raise errors.HttpProcessingError(code=500, message="Invalid configuration.")

    data = await request.post()

    recaptchaResponse = data['recaptchaResponse']

    async with ClientSession() as session:
        async with session.post("https://www.google.com/recaptcha/api/siteverify", data={
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptchaResponse
        }) as response:
            if response.status != 200:
                raise RecaptchaError()

            response = await response.read()
            response = ujson.loads(response)

            if not response['success']:
                raise RecaptchaError()

    if data['email'] and EMAIL_REGEXP.match(data['email']):
        sender = data['email']
    else:
        sender = "noname@kana.nanvel.com"

    message = "Subject: Kana app feedback from {name}\n\nname: {name}\nemail: {email}\nmessage: {message}".format(
        name=data['name'],
        email=data['email'],
        message=data['message']
    )

    await request.app['smtp'].sendmail(sender, [APP_EMAIL], message)
    return web.Response(text="Ok", content_type='text/plain')


app = web.Application()

loop = asyncio.get_event_loop()
smtp = aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT, loop=loop)
loop.run_until_complete(smtp.connect())
app['smtp'] = smtp

# python -m smtpd -n -c DebuggingServer localhost:1025

# for dev only
app.router.add_get('/', index, name='index')
app.router.add_static('/', './static', name='static')

app.router.add_post('/api/feedback', feedback, name='feedback')
