#!/usr/bin/env python3

class Building:
    def __init__(self, floors, address):
        self.floors = floors
        self.address = address
    def identify(self):
        print(f"\nI'm a {self.type} consisting of {self.floors} floors located at {self.address}")
        if self.type == 'warehouse':
            print(f"I have a total storage capacity of {self.num_units * self.unit_sqm} square meters over {self.num_units} storage units.")
        elif self.type == 'house':
            print(f"I have {self.num_bedrooms} bedrooms and {self.num_bathrooms} bathrooms")


class House(Building):
    def __init__(self, num_bedrooms, num_bathrooms):
        self.num_bedrooms = num_bedrooms
        self.num_bathrooms = num_bathrooms
        self.type = 'house'
        self.floors = input("How many floors does your house have? ")
        self.address = input("What is the address of your house? ")


class WareHouse(Building):
    def __init__(self, num_units, unit_sqm):
        self.num_units = num_units
        self.unit_sqm = unit_sqm
        self.type = 'warehouse'
        self.floors = input("How many floors does your warehouse have? ")
        self.address = input("What is the address of your warehouse? ")
