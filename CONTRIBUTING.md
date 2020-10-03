# Contributing

## Creating a virtual environment

Prepare you environment by creating a virtualenv:

    python3 -m venv venv

Then you can add the environment binaries to you path running:

    source venv/bin/activate

Now you can run `python` and `pip`, and your system will execute the
version on your new virtual environment.

When you need to leave your venv, just run `deactivate`.  If you don't
want to use `source venv/bin/activate` you can run `venv/bin/python` and
`venv/bin/pip` directly.

## Installing dependencies and running

Install dependencies with:

    pip install -r requirements.txt

To test the bot, you need to create a bot using
[BotFather](t.me/BotFather) and copy the token. You can then run the bot
like that:

    export CITADOR_TOKEN="your bot token"
    python bot.py

If you don't want to export the token in every new shell session, save
it on a file named `.env` on project root. Its contents should look like
that:

    CITADOR_TOKEN="your bot token"
