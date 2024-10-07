#!/usr/bin/python3
# alc24 - 20 - project1 
# DO NOT remove or edit the lines above. Thank you.

import sys
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.card import CardEnc, EncType
# TODO: improve separation comments


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

    def isBefore(self, dt):
        return self.month < dt.month or (self.month == dt.month and self.day < dt.day)

    def nightsBetween(self, dt):
        if not self.isBefore(dt):
            return -1
        elif self.month == dt.month:
            return dt.day - self.day
        elif self.month + 1 == dt.month:
            return Date.days_in_month[self.month - 1] - self.day + dt.day
        else:
            return -1


class Flight:
    def __init__(self, date, origin, destination, departure, arrival, cost, var):
        self.date = Date(date[0:2], date[3:5])
        self.origin = origin
        self.destination = destination
        self.departure = departure
        # self.arrival = arrival
        self.cost = int(cost)
        self.var = int(var)

    def __str__(self):
        return f"{self.date} {airport_to_city[self.origin]} {airport_to_city[self.destination]} {self.departure} {self.cost}"
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

flight_lines = [line.split() for line in lines[n+2: n+2 + n_flights]]

for i in range(n_flights):
    flight = Flight(*flight_lines[i], i+1)
    flights.append(flight)
    flights_with_origin[flight.origin].append(flight)
    flights_with_destination[flight.destination].append(flight)

    # Soft clauses for all flights to minimize cost
    wcnf.append([-flight.var], weight=flight.cost)
##### end: HANDLE FLIGHTS #####


##### TOTAL n FLIGHTS ##### # FIXME: needed?
# enc = CardEnc.equals(lits=[i for i in range(1, n_flights+1)], bound=n, top_id=num_vars, encoding=EncType.seqcounter)
# num_vars = enc.nv # FIXME: is this correct?
# for clause in enc.clauses:
#     wcnf.append(clause)
##### end: TOTAL n FLIGHTS #####


##### FOR EACH CITY, ARRIVAL AND DEPARTURE k NIGHTS APART #####
for airport, k in cities_to_visit + [(base, K)]:
    if airport != base:
        arrivals = flights_with_destination[airport]
        departures = flights_with_origin[airport]
    else:
        arrivals = flights_with_origin[airport]
        departures = flights_with_destination[airport]

    arrival_vars = [f.var for f in arrivals]
    departure_vars = [f.var for f in departures]

    enc = CardEnc.equals(lits=arrival_vars, bound=1, top_id=num_vars, encoding=EncType.cardnetwrk)
    num_vars = enc.nv
    # print(f"125: {num_vars}", file=sys.stderr)
    for clause in enc.clauses:
        wcnf.append(clause)

    enc = CardEnc.equals(lits=departure_vars, bound=1, top_id=num_vars, encoding=EncType.cardnetwrk)
    num_vars = enc.nv
    # print(f"131: {num_vars}", file=sys.stderr)
    for clause in enc.clauses:
        wcnf.append(clause)

    for f_arrival in arrivals:
        for f_departure in departures:
            if f_arrival.date.nightsBetween(f_departure.date) != k:
                wcnf.append([-f_arrival.var, -f_departure.var])
##### end: FOR EACH CITY, ARRIVAL AND DEPARTURE k NIGHTS APART #####


##### SOLVING #####
solver = RC2(wcnf)
solution = solver.compute()

if solution:
    selected_flights = [i for i in range(len(flights)) if solution[i] > 0]
    print(sum(flights[i].cost for i in selected_flights))
    for i in selected_flights:
        print(flights[i])
##### end: SOLVING #####
