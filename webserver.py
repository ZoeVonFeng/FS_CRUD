import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, MenuItem, Restaurant
import re
from urllib.parse import unquote, parse_qs
import requests

# Create session and connect to DB
engine = create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost:5433/restaurantmenu?client_encoding=utf8', use_batch_mode=True)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/add"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output = "<h1>Add a new restaurant: </h1>"
                output += "</br>"
                output += "<form method='POST' action ='%s'>" % (
                    "/restaurants/add")
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type = 'submit' value = 'Add'/>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output.encode())

            if self.path.endswith("/delete"):
                restaurantID = self.path.split("/")[2]
                # restaurantID = re.split(".*/.*/edit", self.path)
                restaurantEditEntry = session.query(
                    Restaurant).filter_by(id=restaurantID).one()
                if restaurantEditEntry:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output = "<h1>Are you sure you want to delete %s ?</h1>" % restaurantEditEntry.name
                    output += "</br>"
                    output += "<form method='POST' action ='%s'>" % (
                        "/restaurants/"+restaurantID+"/delete")
                    output += "<input type = 'submit' value = 'Delete'/>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output.encode())

            if self.path.endswith("/edit"):
                restaurantID = self.path.split("/")[2]
                # restaurantID = re.split(".*/.*/edit", self.path)
                restaurantEditEntry = session.query(
                    Restaurant).filter_by(id=restaurantID).one()
                print(restaurantEditEntry)
                if restaurantEditEntry:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output = "<h1>Change %s to: </h1>" % restaurantEditEntry.name
                    output += "</br>"
                    # output += "<form method='POST' enctype='multipart/form-data' action ='%s'>" % ("/restaurants/"+restaurantID+"/edit")
                    output += "<form method='POST' action ='%s'>" % (
                        "/restaurants/"+restaurantID+"/edit")
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '%s'>" % restaurantEditEntry.name
                    output += "<input type = 'submit' value = 'Rename'/>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output.encode())

            if self.path.endswith("/restaurants"):
                restaurantList = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<a href=%s>Add a new restaurant</a>" % (
                    "/restaurants/add")
                output += "</br>"
                output += "</br>"
                output += "</br>"

                for r in restaurantList:
                    subpath = "/" + str(r.id) + "/"

                    output += r.name
                    output += "</br>"
                    output += "<a href=%s>Edit</a>" % (
                        "/restaurants"+subpath+"edit")
                    output += "</br>"
                    output += "<a href=%s>Delete</a>" % (
                        "/restaurants"+subpath+"delete")
                    output += "</br>"
                    output += "</br>"

                output += "</body></html>"
                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/add"):
                length = int(self.headers.get('Content-length', 0))
                body = self.rfile.read(length).decode()
                params = parse_qs(body)
                messagecontent = params.get("newRestaurantName")
                newRestaurant = Restaurant(name=messagecontent[0])
                session.add(newRestaurant)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/delete"):
                restaurantID = self.path.split("/")[2]
                restaurantDeleteEntry = session.query(
                    Restaurant).filter_by(id=restaurantID).one()
                if restaurantDeleteEntry:
                    session.delete(restaurantDeleteEntry)
                    print("Delete 1")
                    session.commit()
                    print("Delete 2")
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                length = int(self.headers.get('Content-length', 0))
                body = self.rfile.read(length).decode()
                params = parse_qs(body)
                messagecontent = params.get("newRestaurantName")
                restaurantID = self.path.split("/")[2]
                restaurantEditEntry = session.query(
                    Restaurant).filter_by(id=restaurantID).one()
                if restaurantEditEntry:
                    restaurantEditEntry.name = messagecontent[0]
                    session.add(restaurantEditEntry)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            session.rollback()


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


if __name__ == '__main__':
    main()
