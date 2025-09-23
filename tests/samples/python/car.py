class Car:
    a = 5
    b = "hello"

    def __init__(self, brand, color, year):
        self.brand = brand
        self.color = color
        self.year = year

    def start_engine(self):
        print(f"The {self.color} {self.brand} engine has started.")

    def stop_engine(self):
        print(f"The {self.brand} engine has stopped.")


class Vehicle:
    def __init__(self, make, model):
        self.make = make
        self.model = model
