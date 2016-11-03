#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb

from api import TicTacToeApi
from models import User, Game
from utils import get_by_urlsafe


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email & incomplete game.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            games = Game.query(Game.game_over == False,
                               ndb.OR(Game.user_name_x == user.key,
                                      Game.user_name_o == user.key)).fetch()
            if games:
                subject = 'You have a game in progress'
                body = """Hello {}, you still have a game in progress!
                          Come back & finish up!""".format(user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)

class NotifyOfTurn(webapp2.RequestHandler):
    def post(self):
        """Send a notification email when it's a users's turn"""
        app_id = app_identity.get_application_id()
        # if the user has an email send a reminder
        # keys extracted are urlsafe
        user_key = self.request.get('user_key')
        user = get_by_urlsafe(user_key, User)
        game_key = self.request.get('game_key')
        game = get_by_urlsafe(game_key, Game)
        if game.user_name_x == user.key:
            opponent_key = game.user_name_o
        else:
            opponent_key = game.user_name_x
        if user.email:
            subject = "It's your turn!"
            body = ("Hello {}, it's your turn against {} after {} moves! "
                    "Come back & make a move!").format(user.name,
                                                  opponent_key.get().name,
                                                  game.number_of_moves)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/turn_notification', NotifyOfTurn),
], debug=True)
