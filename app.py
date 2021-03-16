# import tornado
# import os

# class MainHandler(tornado.web.RequestHandler):
#   def get(self):
#     self.render("index.html")

# def main():
#   app = tornado.web.Application(
#     [r"/", MainHandler],
#     static_path=os.path.join(os.path.dirname(__file__), "static"),
#   )
#   app.listen(9099)
#   tornado.ioloop.IOLoop.current().start()

# if __name__ == '__main__':
#   main()
