#!/usr/bin/env python

import json
import logging
import tornado.ioloop
import tornado.web

import berlin
import ai

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
      response = g.generate_turn()
      logging.debug("response: " + str(response))
      self.write(str(response))
      self.flush()
      return
    self.set_status(200)
    return

class SearchAndDestroy(tornado.web.RequestHandler):
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
      response = ai.search_and_destroy(g)
      logging.debug("response: " + str(response))
      self.write(str(response))
      self.flush()
      return
    self.set_status(200)
    return

class FatCat(tornado.web.RequestHandler):
  def get(self):
    self.write("berlin API, send POST please")
  def post(self):
    body = self.request.body
    catlog = logging.getLogger('fatcat')
    catlog.info("received POST")
    catlog.debug(str(body))
    request = {
        'action': self.get_argument('action'),
        'infos': json.loads(self.get_argument('infos')),
        'map': json.loads(self.get_argument('map')),
        'state': json.loads(self.get_argument('state'))
        }
    catlog.info("decoded request")
    catlog.debug(str(request))
    g = berlin.parse_request(request)
    if g is None:
      self.set_status(500, 'could not parse request')
      return
    if g.action in ['ping', 'turn']:
      # do something useful here
      response = ai.another_bot(g)
      catlog.info("sending response")
      catlog.debug(str(response))
      self.write(str(response))
      self.flush()
      return
    self.set_status(200)
    return


class Jsonify(tornado.web.RequestHandler):
  def get(self):
    self.write("berlin API, send POST please")
  def post(self):
    body = self.request.body
    request = {
        'action': self.get_argument('action'),
        'infos': json.loads(self.get_argument('infos')),
        'map': json.loads(self.get_argument('map')),
        'state': json.loads(self.get_argument('state'))
        }
    print json.dumps(request)
    return

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
#logging.basicConfig(format=FORMAT, level=logging.INFO, filename='berlin.log')
catlog = logging.getLogger('fatcat')
catfh = logging.FileHandler('fatcat-req.log')
catfh.setLevel(logging.DEBUG)
catfh.setFormatter(logging.Formatter(FORMAT))
catlog.addHandler(catfh)

application = tornado.web.Application([
  (r"/tojson", Jsonify),
  (r"/searchdestroy", SearchAndDestroy),
  (r"/fatcat", FatCat),
  (r"/randombot", MainHandler), ])


if __name__ == "__main__":
  print "loaded berlin module %s" % berlin.version
  application.listen(5000)
  tornado.ioloop.IOLoop.instance().start()

# vim: set ts=2 sw=2 sts=2 et:
