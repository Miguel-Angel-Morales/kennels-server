class Customer():
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password


new_customer = Customer(2, "Monica", "something@gmail.com", "password")
