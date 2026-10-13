"""Tests for bot.py with fake Discord objects. No network access."""

import asyncio
import types
from unittest import mock

import discord
import pytest

import bot


class FakeChannel:
    def __init__(self, fail_upload=False):
        self.sent = []
        self.fail_upload = fail_upload

    async def send(self, content=None, file=None):
        if file is not None and self.fail_upload:
            raise discord.Forbidden(mock.Mock(status=403, reason="Forbidden"), "Missing Permissions")
        self.sent.append(content)


def make_message(content, channel, author_id=1, is_bot=False):
    return types.SimpleNamespace(
        content=content, channel=channel, author=types.SimpleNamespace(id=author_id, bot=is_bot)
    )


def make_interaction(user_id=1):
    interaction = mock.Mock()
    interaction.user = types.SimpleNamespace(id=user_id)
    interaction.response.defer = mock.AsyncMock()
    interaction.response.send_message = mock.AsyncMock()
    interaction.followup.send = mock.AsyncMock()
    return interaction


@pytest.fixture(autouse=True)
def fresh_state(monkeypatch):
    bot._last_request.clear()
    monkeypatch.setattr(bot, "_chart_slots", asyncio.Semaphore(bot.MAX_CONCURRENT_CHARTS))


@pytest.fixture
def chart_requests(monkeypatch):
    """Replace chart generation with a fake that records its arguments."""
    requests = []

    async def fake_get_chart_png(days, tickers):
        requests.append((days, tickers))
        return b"\x89PNG fake", {}

    monkeypatch.setattr(bot, "get_chart_png", fake_get_chart_png)
    return requests


# --- !stonks messages ---------------------------------------------------------------------------

@pytest.mark.parametrize("content", ["", "   ", "hello", "!stonksfoo"])
def test_other_messages_are_ignored(chart_requests, content):
    channel = FakeChannel()
    asyncio.run(bot.on_message(make_message(content, channel)))
    assert channel.sent == []
    assert chart_requests == []


def test_bots_are_ignored(chart_requests):
    channel = FakeChannel()
    asyncio.run(bot.on_message(make_message("!stonks", channel, is_bot=True)))
    assert channel.sent == []


def test_stonks_command_sends_chart(chart_requests):
    channel = FakeChannel()
    asyncio.run(bot.on_message(make_message("!stonks 30 btc eth", channel)))
    assert chart_requests == [(30, ["BTC", "ETH"])]
    assert channel.sent == ["Generating your stonks chart...", "Here's your stonks chart!"]


def test_invalid_input_is_rejected_without_echoing_it(chart_requests):
    channel = FakeChannel()
    asyncio.run(bot.on_message(make_message("!stonks @everyone", channel)))
    assert chart_requests == []
    assert channel.sent == ["Error: Days must be a whole number between 1 and 3650."]


def test_replies_never_ping_anyone():
    mentions = bot.client.allowed_mentions
    assert not (mentions.everyone or mentions.users or mentions.roles)


def test_skipped_tickers_are_reported(monkeypatch):
    async def fake_get_chart_png(days, tickers):
        return b"png", {"FOO": "not found on CoinGecko"}

    monkeypatch.setattr(bot, "get_chart_png", fake_get_chart_png)
    channel = FakeChannel()
    asyncio.run(bot.on_message(make_message("!stonks 30 BTC FOO", channel)))
    assert channel.sent[-1] == "Here's your stonks chart!\nSkipped FOO (not found on CoinGecko)"


def test_users_have_a_cooldown(chart_requests):
    channel = FakeChannel()
    asyncio.run(bot.on_message(make_message("!stonks", channel)))
    asyncio.run(bot.on_message(make_message("!stonks", channel)))
    asyncio.run(bot.on_message(make_message("!stonks", channel, author_id=2)))
    assert len(chart_requests) == 2
    assert channel.sent[2].startswith("Slow down! Try again in")


def test_failed_upload_is_reported(chart_requests):
    channel = FakeChannel(fail_upload=True)
    asyncio.run(bot.on_message(make_message("!stonks", channel)))
    assert "Attach Files permission" in channel.sent[-1]


def test_unexpected_errors_are_not_echoed(monkeypatch):
    async def broken_get_chart_png(days, tickers):
        raise RuntimeError("internal details")

    monkeypatch.setattr(bot, "get_chart_png", broken_get_chart_png)
    channel = FakeChannel()
    asyncio.run(bot.on_message(make_message("!stonks", channel)))
    assert channel.sent[-1] == "Unexpected error while generating the chart."


# --- /stonks slash command ----------------------------------------------------------------------

def test_slash_command_sends_chart(chart_requests):
    interaction = make_interaction()
    asyncio.run(bot.stonks_command.callback(interaction, days=14, tickers="sol x:nvda"))
    interaction.response.defer.assert_awaited_once_with(thinking=True)
    assert chart_requests == [(14, ["SOL", "X:NVDA"])]
    assert interaction.followup.send.await_args.args == ("Here's your stonks chart!",)
    assert interaction.followup.send.await_args.kwargs["file"].filename == "stonks_chart.png"


def test_slash_command_defaults(chart_requests):
    asyncio.run(bot.stonks_command.callback(make_interaction()))
    assert chart_requests == [(365, ["BTC", "ETH", "XMR", "AVAX"])]


def test_slash_command_rejects_invalid_tickers(chart_requests):
    interaction = make_interaction()
    asyncio.run(bot.stonks_command.callback(interaction, days=14, tickers="@everyone"))
    assert chart_requests == []
    interaction.response.send_message.assert_awaited_once()
    assert interaction.response.send_message.await_args.kwargs == {"ephemeral": True}


def test_slash_command_is_registered():
    assert [command.name for command in bot.client.tree.get_commands()] == ["stonks"]


# --- startup ------------------------------------------------------------------------------------

@pytest.fixture
def no_dotenv(monkeypatch):
    monkeypatch.setattr(bot, "load_dotenv", lambda: None)


def test_main_without_token_exits_with_error(monkeypatch, no_dotenv):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    with pytest.raises(SystemExit) as excinfo:
        bot.main()
    assert excinfo.value.code == 1


def test_main_does_not_add_a_second_log_handler(monkeypatch, no_dotenv):
    monkeypatch.setenv("DISCORD_TOKEN", "token")
    run = mock.Mock()
    monkeypatch.setattr(bot.client, "run", run)
    bot.main()
    run.assert_called_once_with("token", log_handler=None)


@pytest.mark.parametrize("error", [discord.LoginFailure(), discord.PrivilegedIntentsRequired(None)])
def test_main_exits_with_error_on_fatal_discord_errors(monkeypatch, no_dotenv, error):
    monkeypatch.setenv("DISCORD_TOKEN", "token")
    monkeypatch.setattr(bot.client, "run", mock.Mock(side_effect=error))
    with pytest.raises(SystemExit) as excinfo:
        bot.main()
    assert excinfo.value.code == 1
