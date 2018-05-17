#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# Slack / WeAreDevs 2018 - Let's Build A Slack App Example App
#
# This is the started app, from here we'll add:
# - an existing Flask instance
# - a `app_mention` event handler
# - message menus
# - dynamic menu endpoints

from flask import Flask, request, make_response, Response
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter

import json
import os
import urllib

# This is the Flask instance that our event handler will be bound to
# If you don't have an existing Flask app, the events api adapter
# will instantiate it's own Flask instance for you
app = Flask(__name__)


# Bind the Events API route to your existing Flask app by passing the server
# instance as the last param, or with `server=app`.
# Our app's Slack Event Adapter for receiving actions via the Events API
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/slack/events", app)

# Create a SlackClient for your bot to use for Web API requests
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
slack_client = SlackClient(SLACK_BOT_TOKEN)
# ------------------------------------------------------------------------------


# An example of one of your Flask app's routes
@app.route("/test")
def hello():
  return "Hello there!"



# An example of one of your Flask app's routes
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])
    action_json = json.dumps(form_json, indent=4)
    channel = form_json["channel"]["id"]
    slack_client.api_call("chat.postMessage", channel=channel, text="```{}```".format(action_json))
    return ""



# An example of one of your Flask app's routes
@app.route("/slack/message_options", methods=["POST"])
def message_options():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    menu_options = {
        "options": [
            {
                "text": "Unexpected sentience",
                "value": "AI-2323"
            },
            {
                "text": "Bot biased toward other bots",
                "value": "SUPPORT-42"
            },
            {
                "text": "Bot broke my toaster",
                "value": "IOT-75"
            }
        ]
    }

    response = json.dumps(menu_options)
    return Response(json.dumps(menu_options), mimetype='application/json')



# ==============================================================================
# Event listened for reactions
# When a user reacts to a message, echo it to the channel
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    # Get the emoji name from the event dats
    emoji = event["reaction"]
    # Get the channel ID from the event data
    channel = event["item"]["channel"]
    user = event["user"]
    text = "<@{}> reacted with :{}:".format(user, emoji)
    slack_client.api_call("chat.postMessage", channel=channel, text=text)
# ------------------------------------------------------------------------------


# ==============================================================================
# Event listener for messages
# When subscribed to `message` events, your app will receive any messages
# sent to the channels your app has been invited to
@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    message = event_data["event"]

    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None:
        # If the incoming message contains "hi", then respond with a greeting
        if "hi" in message.get('text'):
            channel = message["channel"]
            message = "Hello <@{}>! :tada:".format(message["user"])
            button_attachment = [
                {
                    "text": "Choose a game to play",
                    "fallback": "You are unable to choose a game",
                    "callback_id": "wopr_game",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "game",
                            "text": "Print this action!",
                            "type": "select",
                            "data_source": "external"
                        }
                    ]
                }
            ]
            slack_client.api_call("chat.postMessage", channel=channel, text=message, attachments=button_attachment)
# ------------------------------------------------------------------------------


# ==============================================================================
# Event listener for messages
# When subscribed to `message` events, your app will receive any messages
# sent to the channels your app has been invited to
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]

    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None:
        # If the incoming message contains "hi", then respond with a greeting
        if "status" in message.get('text'):
            channel = message["channel"]
            message = "Hello <@{}>! :tada: EVERY IS AWESOME - THE SERVER IS NOT DEAD".format(message["user"])
            slack_client.api_call("chat.postMessage", channel=channel, text=message)
# ------------------------------------------------------------------------------


# ==============================================================================
# Start the Flask server on port 3000
if __name__ == "__main__":
    app.run(port=3000)
# ------------------------------------------------------------------------------
