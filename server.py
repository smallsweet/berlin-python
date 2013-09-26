#!/usr/bin/env python

import json
import logging
import tornado.ioloop
import tornado.web

import berlin

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("berlin API, send POST please")
  def post(self):
    body = self.request.body
    logging.debug("received POST: " + body)
    request = {
        'action': self.get_argument('action'),
        'infos': json.loads(self.get_argument('infos')),
        'map': json.loads(self.get_argument('map')),
        'state': json.loads(self.get_argument('state'))
        }
    logging.debug("decoded request: " + str(request))
    g = berlin.parse_request(request)
    if g is None:
      self.set_status(500, 'could not parse request')
      return
    if g.action in ['ping', 'turn']:
      # do something useful here
      response = berlin.move_at_random(g)
      logging.info("response: " + str(response))
      self.write(str(response))
      self.flush()
      return
    self.set_status(200)
    return

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

application = tornado.web.Application([ (r"/randombot", MainHandler), ])


if __name__ == "__main__":
  application.listen(5000)
  tornado.ioloop.IOLoop.instance().start()

# vim: set ts=2 sw=2 sts=2 et:
