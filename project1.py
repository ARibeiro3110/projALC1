#!/usr/bin/python3
# alc24 - 20 - project1 
# DO NOT remove or edit the lines above. Thank you.

import sys
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.card import CardEnc, EncType
# TODO: remove prints with file=sys.stderr
# TODO: improve separation comments

import os # TODO: remove
sys.stderr = open(os.devnull, 'w') # TODO: remove


wcnf = WCNF()

airport_to_city = {}            # key: airport, value: city
cities_to_visit = []            # list of tuples (airport, k)
flights = []                    # list of Flights (attributes: date, origin, destination, departure, arrival, cost)
flights_with_origin = {}        # key: airport, value: flights[]
flights_with_destination = {}   # key: airport, value: flights[]


##### CLASSES #####
class Date:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, day, month):
        self.day = int(day)
        self.month = int(month)

    def __str__(self):
        return f"{self.day:02}/{self.month:02}"
    
    def isBefore(self, dt): # TODO remove?
        return self.month < dt.month or (self.month == dt.month and self.day < dt.day)
    
    def nightsBetween(self, dt):
        if not self.isBefore(dt):
            return -1
        elif self.month == dt.month:
            return dt.day - self.day
        elif self.month + 1 == dt.month:
            return Date.days_in_month[self.month - 1] - self.day + dt.day
        else:
            raise ValueError("The method only supports consecutive months or the same month.")


class Flight:
    def __init__(self, date, origin, destination, departure, arrival, cost, var):
        self.date = Date(date[0:2], date[3:5])
        self.origin = origin
        self.destination = destination
        self.departure = departure # FIXME: needed?
        self.arrival = arrival # FIXME: needed?
        self.cost = int(cost)
        self.var = int(var)

    def __str__(self):
        return str(self.date) + ' ' + airport_to_city[self.origin] + ' ' + airport_to_city[self.destination] + ' ' + self.departure + ' ' + str(self.cost)

    def __repr__(self): # TODO: remove?
        return self.__str__()
##### end: CLASSES #####


##### READ FROM STDIN #####
input_stream = sys.stdin.read()
lines = input_stream.strip().split("\n")
n = int(lines[0])
##### end: READ FROM STDIN #####


##### HANDLE CITIES #####
city, airport = lines[1].split()
airport_to_city[airport] = city
flights_with_origin[airport] = []
flights_with_destination[airport] = []
base = airport

K = 0
for i in range(2, n+1):
    city, airport, k = lines[i].split()
    airport_to_city[airport] = city
    flights_with_origin[airport] = []
    flights_with_destination[airport] = []
    cities_to_visit.append((airport, int(k)))
    K += int(k)
##### end: HANDLE CITIES #####


##### HANDLE FLIGHTS #####
n_flights = int(lines[n+1])
num_vars = n_flights

date = lines[n+2].split()[0]
flight_lines = [line.split() for line in lines[n+2: n+2 + n_flights]]
last_flight_line = n+2 + n_flights - 1

atmost1_lits = []
base_origin_lits = []
base_destination_lits = []

for i in range(n_flights):
    flight = Flight(*flight_lines[i], i+1)
    flights.append(flight)
    flights_with_origin[flight.origin].append(flight)
    flights_with_destination[flight.destination].append(flight)

    ##### SOFT CLAUSES FOR ALL FLIGHTS TO MINIMIZE COST #####
    wcnf.append([-flight.var], weight=flight.cost)
    print(f"soft clause: {[-flight.var]}, weight: {flight.cost}", file=sys.stderr)
    ##### end: SOFT CLAUSES FOR ALL FLIGHTS TO MINIMIZE COST #####

    ##### AT MOST 1 FLIGHT PER DAY ##### # TODO: needed?
    # atmost1_lits.append(flight.var)
    # if i == n_flights-1 or flight.date != flight_lines[i+1][0]:
    #     enc = CardEnc.atmost(lits=atmost1_lits, bound=1, top_id=num_vars, encoding=EncType.pairwise) # TODO: encoding
    #     num_vars = enc.nv # FIXME: is this correct?
    #     print(f"number of vars: {enc.nv}", file=sys.stderr)
    #     for clause in enc.clauses:
    #         wcnf.append(clause)
    #         print(f"hard clause: {clause}", file=sys.stderr)
    #     atmost1_lits = []
    ##### end: AT MOST 1 FLIGHT PER DAY #####

    ##### 1 FLIGHT FROM AND TO BASE ##### FIXME: obsolete
    # if flight.origin == base:
    #     base_origin_lits.append(flight.var)
    # elif flight.destination == base:
    #     base_destination_lits.append(flight.var)
    ##### to be continued: 1 FLIGHT FROM AND TO BASE #####
##### end: HANDLE FLIGHTS #####


##### TOTAL n FLIGHTS ##### # FIXME: needed?
enc = CardEnc.equals(lits=[i for i in range(1, n_flights+1)], bound=n, top_id=num_vars, encoding=EncType.seqcounter)
num_vars = enc.nv # FIXME: is this correct?
for clause in enc.clauses:
    print(f"hard clause: {clause}", file=sys.stderr)
    wcnf.append(clause)
##### end: TOTAL n FLIGHTS #####


##### continue: 1 FLIGHT FROM AND TO BASE ##### FIXME: obsolete
# for list in [base_origin_lits, base_destination_lits]:
#     enc = CardEnc.equals(lits=list, bound=1, top_id=num_vars, encoding=EncType.pairwise) # TODO: encoding
#     num_vars = enc.nv # FIXME: is this correct?
#     print(f"number of vars: {enc.nv}", file=sys.stderr)
#     for clause in enc.clauses:
#         wcnf.append(clause)
#         print(f"hard clause: {clause}", file=sys.stderr)
##### end: 1 FLIGHT FROM AND TO BASE #####


##### FOR EACH CITY, ARRIVAL AND DEPARTURE k NIGHTS APART #####
for airport, k in cities_to_visit + [(base, K)]:
    flights_pairs_lits = []
    if airport != base:
        flights1 = flights_with_destination[airport]
        flights2 = flights_with_origin[airport]
    else:
        flights1 = flights_with_origin[airport]
        flights2 = flights_with_destination[airport]

    for f1 in flights1:
        for f2 in flights2:
            if f1.date.nightsBetween(f2.date) == k:
                num_vars += 1
                flights_pairs_lits.append(num_vars)
                wcnf.append([-num_vars, f1.var])
                wcnf.append([-num_vars, f2.var])
                wcnf.append([num_vars, -f1.var, -f2.var])
                print(f"hard clause: {[-num_vars, f1.var]}", file=sys.stderr)
                print(f"hard clause: {[-num_vars, f2.var]}", file=sys.stderr)
                print(f"hard clause: {[num_vars, -f1.var, -f2.var]}", file=sys.stderr)
    enc = CardEnc.equals(lits=flights_pairs_lits, bound=1, top_id=num_vars, encoding=EncType.pairwise) # TODO: could be atLeast1?
    num_vars = enc.nv # FIXME: is this correct?
    for clause in enc.clauses:
        wcnf.append(clause)
        print(f"hard clause: {clause}", file=sys.stderr)
##### end: FOR EACH CITY, ARRIVAL AND DEPARTURE k NIGHTS APART #####



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
##### end: SOLVING #####
