#!/usr/bin/python3
# alc24 - 20 - project1 
# DO NOT remove or edit the lines above. Thank you.

import sys
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.card import CardEnc, EncType

##### GLOBAL VARIABLES #####
wcnf = WCNF()
airport_to_city = {}            # key: airport, value: city
cities_to_visit = []            # list of tuples (airport, k)
flights = []                    # list of Flights (attributes: date, origin, destination, departure, arrival, cost)
flights_with_origin = {}        # key: airport, value: flights[]
flights_with_destination = {}   # key: airport, value: flights[]
##### end: GLOBAL VARIABLES #####


##### CLASSES #####
class Date:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, day, month):
        self.day = int(day)
        self.month = int(month)

    def __str__(self):
        return f"{self.day:02}/{self.month:02}"

    def toOrdinal(self):
        return sum(Date.days_in_month[:self.month - 1]) + self.day

    def nightsBetween(self, dt):
        return dt.toOrdinal() - self.toOrdinal()

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
lines = sys.stdin.read().strip().split("\n")
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
m = int(lines[n+1])
flight_lines = [line.split() for line in lines[n+2: n+2 + m]]

for i in range(m):
    flight = Flight(*flight_lines[i], i+1)
    flights.append(flight)
    flights_with_origin[flight.origin].append(flight)
    flights_with_destination[flight.destination].append(flight)

    # Soft clauses for all flights to minimize cost
    wcnf.append([-flight.var], weight=flight.cost)
##### end: HANDLE FLIGHTS #####


##### FOR EACH CITY, ARRIVAL AND DEPARTURE ARE k NIGHTS APART #####
for airport, k in cities_to_visit + [(base, K)]:
    if airport != base:
        arrivals = flights_with_destination[airport]
        departures = flights_with_origin[airport]
    else:
        arrivals = flights_with_origin[airport]
        departures = flights_with_destination[airport]

    arrival_vars = [f.var for f in arrivals]
    enc = CardEnc.equals(lits=arrival_vars, bound=1, encoding=EncType.pairwise)
    wcnf.extend(enc.clauses)

    departure_vars = [f.var for f in departures]
    enc = CardEnc.equals(lits=departure_vars, bound=1, encoding=EncType.pairwise)
    wcnf.extend(enc.clauses)

    for f_arrival in arrivals:
        compatible_departures = [f_departure.var for f_departure in departures
                                 if f_arrival.date.nightsBetween(f_departure.date) == k]
        wcnf.append([-f_arrival.var] + compatible_departures)
    
    for f_departure in departures:
        compatible_arrivals = [f_arrival.var for f_arrival in arrivals
                               if f_arrival.date.nightsBetween(f_departure.date) == k]
        wcnf.append([-f_departure.var] + compatible_arrivals)
##### end: FOR EACH CITY, ARRIVAL AND DEPARTURE ARE k NIGHTS APART #####


##### SOLVING #####
solver = RC2(wcnf)
solution = solver.compute()

if solution:
    selected_vars = set(var for var in solution if var > 0)
    selected_flights = [f for f in flights if f.var in selected_vars]
    total_cost = sum(f.cost for f in selected_flights)

    print(total_cost)
    for f in selected_flights:
        print(f)
##### end: SOLVING #####
