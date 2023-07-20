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
from views import get_customer_by_email
from views import get_animal_by_location
from views import get_animal_by_status
from views import get_employee_by_location_id
from urllib.parse import urlparse, parse_qs


class HandleRequests(BaseHTTPRequestHandler):

    def parse_url(self, path):
        parsed_url = urlparse(path)
        path_params = parsed_url.path.split('/')  # ['', 'animals', 1]
        resource = path_params[1]

        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            return (resource, query)

        pk = None
        try:
            pk = int(path_params[2])
        except (IndexError, ValueError):
            pass

        # <-- Corrected indentation for the return statement
        return (resource, pk)

    def do_GET(self):
        self._set_headers(200)
        response = {}

        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url(self.path)

        # If the path does not include a query parameter, continue with the original if block
        if '?' not in self.path:
            (resource, id) = parsed

            if resource == "animals":
                if id is not None:
                    response = get_single_animal(id)

                else:
                    response = get_all_animals()

            elif resource == "locations":
                if id is not None:
                    response = get_single_location(id)

                else:
                    response = get_all_locations()

            elif resource == "employees":
                if id is not None:
                    response = get_single_employee(id)

                else:
                    response = get_all_employees()

            elif resource == "customers":
                if id is not None:
                    response = get_single_customer(id)

                else:
                    response = get_all_customers()

        else:  # There is a ? in the path, run the query param functions
            (resource, query) = parsed

            # see if the query dictionary has an email key
            if query.get('email') and resource == 'customers':
                response = get_customer_by_email(query['email'][0])

            if query.get('location_id') and resource == 'animals':
                response = get_animal_by_location(query['location_id'][0])

            if query.get('status') and resource == 'animals':
                response = get_animal_by_status(query['status'][0])

            if query.get('location_id') and resource == 'employees':
                response = get_employee_by_location_id(query['location_id'][0])

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
