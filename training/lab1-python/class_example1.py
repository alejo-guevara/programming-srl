#!/usr/bin/env python3

class Building:
    def __init__(self, floors, address):
        self.floors = floors
        self.address = address
    def identify(self):
        print(f"I'm a building consisting of {self.floors} floors located at {self.address}")
