import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from views import get_all_animals
from views import get_single_animal
from views import get_all_locations
from views import get_single_location
from views import get_all_employees
from views import get_single_employee
from views import get_all_customers
from views import get_single_customer
from views import create_animal
from views import create_location
from views import create_employee
from views import create_customer
from views import delete_animal
from views import delete_location
from views import delete_employee
from views import delete_customer
from views import update_animal
from views import update_customer
from views import update_employee
from views import update_location

# Here's a class. It inherits from another class.
# For now, think of a class as a container for functions that
# work together for a common purpose. In this case, that
# common purpose is to respond to HTTP requests from a client.


class HandleRequests(BaseHTTPRequestHandler):
    def parse_url(self, path):
        # Just like splitting a string in JavaScript. If the
        # path is "/animals/1", the resulting list will
        # have "" at index 0, "animals" at index 1, and "1"
        # at index 2.
        path_params = path.split("/")
        resource = path_params[1]
        id = None

        # Try to get the item at index 2
        try:
            # Convert the string "1" to the integer 1
            # This is the new parseInt()
            id = int(path_params[2])
        except IndexError:
            pass  # No route parameter exists: /animals
        except ValueError:
            pass  # Request had trailing slash: /animals/

        return (resource, id)  # This is a tuple
    # This is a Docstring it should be at the beginning of all classes and functions
    # It gives a description of the class or function
    """Controls the functionality of any GET, PUT, POST, DELETE requests to the server
    """

    # Here's a class function

    # Here's a method on the class that overrides the parent's method.
    # It handles any GET request.
    def do_GET(self):
        """Handles GET requests to the server
        """
        response = {}  # Default response

        # Parse the URL and capture the tuple that is returned
        (resource, id) = self.parse_url(self.path)

        if resource == "animals":
            if id is not None:
                response = get_single_animal(id)
                if response is None:
                    self._set_headers(404)
                    response = {
                        "error": "Animal was captured by David Blane, is now Unicorn galloping on rainbows throughout the universe"}
            else:
                response = get_all_animals()

        if resource == "locations":
            if id is not None:
                response = get_single_location(id)
                if response is None:
                    self._set_headers(404)
                    response = {
                        "error": "Location is currently under seige, return with reinforcements."}

            else:
                response = get_all_locations()

        if resource == "employees":
            if id is not None:
                response = get_single_employee(id)
                if response is None:
                    self._set_headers(404)
                    response = {
                        "error": "Employee has been out to lunch for 82 years..."}

            else:
                response = get_all_employees()

        if resource == "customers":
            if id is not None:
                response = get_single_customer(id)
                if response is None:
                    self._set_headers(404)
                    response = {
                        "error": "customer is unaware of the majesty of animal retail therapy, whats wrong with being a crazy cat lady?"}

            else:
                response = get_all_customers()
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any POST request.
    def do_POST(self):
        self._set_headers(201)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Convert JSON string to a Python dictionary
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        # Initialize new resource variables
        new_resource = None

        if resource == "animals":
            if "name" in post_body and "species" in post_body:
                new_resource = create_animal(post_body)
            else:
                self._set_headers(400)
                new_resource = {
                    "message":
                    f'{"name is required" if "name" not in post_body else ""} {"species is required" if "species" not in post_body else ""}'
                }

        if resource == "locations":
            if "name" in post_body and "address" in post_body:
                new_resource = create_location(post_body)
            else:
                self._set_headers(400)
                new_resource = {
                    "message": f'{"name is required" if "name" not in post_body else ""} {"address is required" if "address" not in post_body else ""}'
                }

        if resource == "employees":
            if "name" in post_body and "position" in post_body:
                new_resource = create_employee(post_body)
            else:
                self._set_headers(400)
                new_resource = {
                    "message": f'{"name is required" if "name" not in post_body else ""} {"address is required" if "address" not in post_body else ""}'
                }

        if resource == "customers":
            if "name" in post_body:
                new_resource = create_customer(post_body)
            else:
                self._set_headers(400)
                new_resource = {
                    "message": f'name is required'
                }

        # Encode the new resource and send in response
        self.wfile.write(json.dumps(new_resource).encode())

    # A method that handles any PUT request.
    # def do_PUT(self):
    """Handles PUT requests to the server"""
    # self.do_PUT()

    def do_PUT(self):
        self._set_headers(204)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        # Delete a single animal from the list
        if resource == "animals":
            update_animal(id, post_body)

        if resource == "employees":
            update_employee(id, post_body)

        if resource == "customers":
            update_customer(id, post_body)

        if resource == "locations":
            update_location(id, post_body)

        # Encode the new animal and send in response
        self.wfile.write(json.dumps(
            {"message": "Resource updated successfully"}).encode())

    def _set_headers(self, status):
        # Notice this Docstring also includes information about the arguments passed to the function
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Another method! This supports requests with the OPTIONS verb.
    def do_OPTIONS(self):
        """Sets the options headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    def do_DELETE(self):
        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        if resource == "customers":
            # Customers cannot be deleted, send a 405 Method Not Allowed response
            self._set_headers(405)
            response = {
                "error": "Deleting customers is not allowed."
            }
        else:
            # For other resources, proceed with the delete operation
            self._set_headers(204)

            if resource == "animals":
                delete_animal(id)
            elif resource == "locations":
                delete_location(id)
            elif resource == "employees":
                delete_employee(id)

            response = ""

        # Encode the response and send it
        self.wfile.write(json.dumps(response).encode())


# This function is not inside the class. It is the starting
# point of this application.


def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()
