#!/usr/bin/python3
# alc24 - 20 - project1 
# DO NOT remove or edit the lines above. Thank you.

import sys
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.card import CardEnc, EncType
# TODO: remove prints with file=sys.stderr

wcnf = WCNF()
num_vars = 0

airport_to_city = {}    # key: airport, value: city
cities_to_visit = []    # list of tuples (city, k)
flights = []            # list of Flights (attributes: date, origin, destination, departure, arrival, cost)



##### CLASSES #####
class Flight:
    def __init__(self, date, origin, destination, departure, arrival, cost):
        self.date = date
        self.origin = origin
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.cost = int(cost)

    def __str__(self):
        return self.date + ' ' + airport_to_city[self.origin] + ' ' + airport_to_city[self.destination] + ' ' + self.departure + ' ' + self.arrival + ' ' + str(self.cost)

    def __repr__(self): # TODO: remove?
        return self.__str__()
##### end CLASSES #####



##### READ INPUT #####
input_stream = sys.stdin.read()
lines = input_stream.strip().split("\n")

n = int(lines[0])

city, airport = lines[1].split()
base = airport
airport_to_city[airport] = city

for i in range(2, n+1):
    city, airport, k = lines[i].split()
    airport_to_city[airport] = city
    cities_to_visit.append((airport, k))

n_flights = int(lines[n+1])

date = lines[n+2].split()[0]
flight_lines = [line.split() for line in lines[n+2: n+2 + n_flights]]
last_flight_line = n+2 + n_flights - 1

atmost1_lits = []
base_origin_lits = []
base_destination_lits = []

for i in range(n_flights):
    flight = Flight(*flight_lines[i])
    flights.append(flight)

    ##### SOFT CLAUSES #####
    num_vars += 1
    flight_var = num_vars
    wcnf.append([-flight_var], weight=flight.cost)
    print(f"soft clause: {[-flight_var]}, weight: {flight.cost}", file=sys.stderr)
    ##### end SOFT CLAUSES #####

    ##### AT MOST 1 FLIGHT PER DAY #####
    atmost1_lits.append(flight_var)
    if i == n_flights-1 or flight.date != flight_lines[i+1][0]:
        enc = CardEnc.atmost(lits=atmost1_lits, bound=1, top_id=num_vars, encoding=EncType.pairwise) # TODO: encoding
        # TODO: num_vars
        print(f"number of vars: {enc.nv}", file=sys.stderr)
        for clause in enc.clauses:
            wcnf.append(clause)
            print(f"hard clause: {clause}", file=sys.stderr)
        atmost1_lits = []
    ##### end AT MOST 1 FLIGHT PER DAY #####

    ##### 1 FLIGHT FROM AND TO BASE #####
    if flight.origin == base:
        base_origin_lits.append(flight_var)
    elif flight.destination == base:
        base_destination_lits.append(flight_var)
    ##### to be continued 1 FLIGHT FROM AND TO BASE #####

##### end READ INPUT #####


##### continue 1 FLIGHT FROM AND TO BASE #####
for list in [base_origin_lits, base_destination_lits]:
    enc = CardEnc.equals(lits=list, bound=1, top_id=num_vars, encoding=EncType.pairwise) # TODO: encoding
    # TODO: num_vars
    print(f"number of vars: {enc.nv}", file=sys.stderr)
    for clause in enc.clauses:
        wcnf.append(clause)
        print(f"hard clause: {clause}", file=sys.stderr)
##### end 1 FLIGHT FROM AND TO BASE #####



##### SOLVING #####
solver = RC2(wcnf)
solution = solver.compute()
print(f"Solution: {solution}; Cost: {solver.cost}", file=sys.stderr)

selected_flights = [i for i in range(len(flights)) if solution[i] > 0]
print(sum(flights[i].cost for i in selected_flights))
for i in selected_flights:
    print(flights[i])

# print("airport_to_city:", airport_to_city)
# print("base:", base)
# print("cities_to_visit:", cities_to_visit)
# print("flights:", flights)
##### end SOLVING #####
