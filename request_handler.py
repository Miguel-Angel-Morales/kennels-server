import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from views import (
    get_all_animals,
    get_single_animal,
    get_all_locations,
    get_single_location,
    get_all_employees,
    get_single_employee,
    get_all_customers,
    get_single_customer,
    create_animal,
    create_location,
    create_employee,
    create_customer,
    delete_animal,
    delete_location,
    delete_employee,
    delete_customer,
    update_animal,
    update_customer,
    update_employee,
    update_location,
    get_customer_by_email,
    get_animal_by_location,
    get_animal_by_status,
    get_employee_by_location_id,
    get_all_animals_with_locations_and_customer,
    get_all_employees_with_locations
)


class HandleRequests(BaseHTTPRequestHandler):

    def parse_url(self, path):
        parsed_url = urlparse(path)
        path_params = parsed_url.path.split('/')
        resource = path_params[1]

        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            return (resource, query)

        pk = None
        try:
            pk = int(path_params[2])
        except (IndexError, ValueError):
            pass

        return (resource, pk)

    def _set_headers(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        self._set_headers(200)
        response = {}

        parsed = self.parse_url(self.path)

        if '?' not in self.path:
            (resource, id) = parsed

            if resource == "animals":
                if id is not None:
                    response = get_single_animal(id)
                else:
                    response = get_all_animals_with_locations_and_customer()

            elif resource == "locations":
                if id is not None:
                    response = get_single_location(id)
                else:
                    response = get_all_locations()

            elif resource == "employees":
                if id is not None:
                    response = get_single_employee(id)
                else:
                    response = get_all_employees_with_locations()

            elif resource == "customers":
                if id is not None:
                    response = get_single_customer(id)
                else:
                    response = get_all_customers()

        else:
            (resource, query) = parsed

            if query.get('email') and resource == 'customers':
                response = get_customer_by_email(query['email'][0])

            if query.get('location_id') and resource == 'animals':
                response = get_animal_by_location(query['location_id'][0])

            if query.get('status') and resource == 'animals':
                response = get_animal_by_status(query['status'][0])

            if query.get('location_id') and resource == 'employees':
                response = get_employee_by_location_id(query['location_id'][0])

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        self._set_headers(201)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        (resource, id) = self.parse_url(self.path)

        new_resource = None

        if resource == "animals":
            if "name" in post_body and "breed" in post_body:
                new_resource = create_animal(post_body)
            else:
                self._set_headers(400)
                new_resource = {
                    "message":
                    f'{"name is required" if "name" not in post_body else ""} {"breed is required" if "breed" not in post_body else ""}'
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

        self.wfile.write(json.dumps(new_resource).encode())

    def do_PUT(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        (resource, id) = self.parse_url(self.path)

        success = False

        if resource == "animals":
            success = update_animal(id, post_body)
        elif resource == "employees":
            update_employee(id, post_body)
        elif resource == "customers":
            update_customer(id, post_body)
        elif resource == "locations":
            update_location(id, post_body)

        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

        self.wfile.write("".encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    def do_DELETE(self):
        (resource, id) = self.parse_url(self.path)

        if resource == "customers":
            self._set_headers(405)
            response = {
                "error": "Deleting customers is not allowed."
            }
        else:
            self._set_headers(204)

            if resource == "animals":
                delete_animal(id)
            elif resource == "locations":
                delete_location(id)
            elif resource == "employees":
                delete_employee(id)

            response = ""

        self.wfile.write(json.dumps(response).encode())


def main():
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()