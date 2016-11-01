#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb

from api import TicTacToeApi
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email & incomplete game.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            games = Game.query(Game.game_over == False,
                               ndb.OR(Game.user_name_x == user.key,
                                      Game.user_name_o == user.key))
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


# class UpdateAverageMovesRemaining(webapp2.RequestHandler):
#     def post(self):
#         """Update game listing announcement in memcache."""
#         TicTacToeApi._cache_average_attempts()
#         self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)
#    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
