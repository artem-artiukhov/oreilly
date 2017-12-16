#!/usr/bin/env python3

"""
The Oyster Card Problem

You are required to model the following fare card system which is a limited version of
London’s Oyster card system. At the end of the test, you should be able to demonstrate a
user loading a card with £30, and taking the following trips, and then viewing the balance.

- Tube Holborn to Earl’s Court
- 328 bus from Earl’s Court to Chelsea
- Tube Earl’s court to Hammersmith


Operation

When the user passes through the inward barrier at the station, their oyster card is charged
the maximum fare.

When they pass out of the barrier at the exit station, the fare is calculated and the maximum
fare transaction removed and replaced with the real transaction (in this way, if the user
doesn’t swipe out, they are charged the maximum fare).All bus journeys are charged at the same price.

The system should favour the customer where more than one fare is possible for a given
journey. E.g. Holburn to Earl’s Court is charged at £2.50.


Stations and zones:

Station Zone(s)
Holborn 1
Earl’s Court 1, 2
Wimbledon 3
Hammersmith 2


Fares:
Journey Fare
Anywhere in Zone 1 £2.50
Any one zone outside zone 1 £2.00
Any two zones including zone 1 £3.00
Any two zones excluding zone 1 £2.25
Any three zones £3.20
Any bus journey £1.80

The maximum possible fare is therefore £3.20.


Assessment Criteria

Points you will be assessed on:
● Following the Operational requirements
● A working solution which meets the requirements.
● Testing methods and coverage
● Design, Approach and Elegance of Solution.
"""

# defining fares and reusable variables
MAX_FARE = 3.20
BUS_FARE = 1.80
IN_ZONE1_FARE = 2.50
OUTTER_ONE_ZONE_FARE = 2.00
OUTTER_TWO_ZONES_EXCL_1 = 2.25
OUTTER_TWO_ZONES_INCL_1 = 3.00

ZONE1 = 1
ZONE2 = 2
ZONE3 = 3

ZONE_DICT = {
    'Holborn': ZONE1,
    "Earl's Court Zone 1": ZONE1,
    "Earl's Court Zone 2": ZONE2,
    "Hammersmith": ZONE2,
    "Wimbledon": ZONE3,
}

STATIONS_DICT = {
    1: "Holborn",
    2: "Earl's Court",
    3: "Wimbledon",
    4: "Hammersmith"
}

EC_DICT = {
    1: "Earl's Court Zone 1",
    2: "Earl's Court Zone 2"
}

# function to define charge for different zones of Tube
def fare_2_charge(start_point=None, end_point=None):
    if ZONE_DICT[start_point] == ZONE_DICT[end_point]:
        if ZONE_DICT[start_point] in (2, 3):
            return OUTTER_ONE_ZONE_FARE
        else:
            return IN_ZONE1_FARE

    if ZONE_DICT[start_point] != ZONE_DICT[end_point]:
        if ZONE_DICT[start_point] == 1 or ZONE_DICT[end_point] == 1:
            return OUTTER_TWO_ZONES_INCL_1
        else:
            return OUTTER_TWO_ZONES_EXCL_1


# computations if user decides to ride by bus
def journey_by_bus(balance, fare=BUS_FARE):
    print('Cost of this leg you journey by bus is equal to {:.2f} GBP.'.format(BUS_FARE))
    balance -= fare
    return balance

# here we are charging our oyster card:
def charging_balance():
    while True:
        try:
            balance = float(input("Charge your card: "))
            break
        except TypeError:
            print("Enter correct value.")
            continue
    return balance


# computations if user decides to ride by tube
def tube_journey(balance, start_point, end_point):
    balance -= 3.20
    start_station = STATIONS_DICT[start_point]
    end_station = STATIONS_DICT[end_point]

    if start_point == 2:
        while True:
            # print("Please note, Earl's Court station relates to both Zone 1 and Zone 2, please confirm.")
            print("Charge from Earl's Court station to {2} station will be: Zone 1 - {0:.2f} GBP, Zone 2 - {1:.2f} GBP".format(
                    fare_2_charge(EC_DICT[1], end_station), fare_2_charge(EC_DICT[2], end_station),
                    end_station))
            EC_clar = int(input("Please enter the number of Zone for Earl's Court (1 - Zone 1, 2 - Zone 2): "))
            if EC_clar in (1, 2):
                start_station = EC_DICT[EC_clar]
                break
            else:
                print('Chose correct option for Earl\'s Court station')
                continue

    if end_point == 2:
        while True:
            # print("Please note, Earl's court station relates to both Zone 1 and Zone 2, please confirm.")
            print("Charge from {2} station to Earl's Court station will be: Zone 1 - {0:.2f} GBP, Zone 2 - {1:.2f} GBP".format(
                    fare_2_charge(start_station, EC_DICT[1]), fare_2_charge(start_station, EC_DICT[2]),
                    start_station))
            EC_clar = int(input("Please enter the number of Zone for Earl's Court (1 - Zone 1, 2 - Zone 2): "))
            if EC_clar in (1,2):
                end_station = EC_DICT[EC_clar]
                break
            else:
                print("Please, choose the correct option for Earl's court station")
                continue

    current_charge = fare_2_charge(start_station, end_station)
    print("Your charge at this leg of journey ({0} --> {1}) is: {2:.2f} GBP".format(start_station, end_station,
                                                                                    current_charge))
    # returning MAX_FARE and charging for current leg
    balance += MAX_FARE
    balance -= current_charge
    return balance


# all magic happens here
def main():
    # charging of the Oyster card
    finishing_balance = charging_balance()

    # Here user's journey begins
    print("Charge of the Oyster card in the beginning: {:.2f}".format(finishing_balance))

    while finishing_balance > 0:
        try:
            transport = input("What type of transport would you like to ride (1 - Tube, 2 - by Bus): ")

            if transport not in ('1', '2'):
                print("Please, enter the correct option")
                continue

            # according to task, any bus journey have the same charge, no need to differentiate it
            if transport == '2':
                finishing_balance = journey_by_bus(finishing_balance)
                print("Available amount: {:.2f} GBP".format(finishing_balance))
                while True:
                    ex_status = input("Would you like to continue your journey? ([y]/n): ").lower()
                    if not ex_status or ex_status == 'y':
                        break

                    if ex_status not in ('y', 'n'):
                        print('Please choose correct option.')
                        continue

                    if ex_status == 'n':
                        raise KeyboardInterrupt

                continue

            # here our user starts his journey by tube
            while True:
                start_point = int(input("Please enter the tube station you are going from (1 - Holborn, 2 - Earl's Court, 3 - Wimbledon, 4 - Hammersmith): "))
                if start_point not in range(1,5):
                    print("Please choose correct option.")
                    continue
                else:
                    break

            while True:
                end_point = int(input("Please enter the tube station you are going to (1 - Holborn, 2 - Earl's Court, 3 - Wimbledon, 4 - Hammersmith): "))
                if end_point not in range(1,5):
                    print("Please choose correct option.")
                    continue
                elif end_point == start_point:
                    print("Please chose another place, that differs of where you are now: {}.".format(STATIONS_DICT[start_point]))
                    continue
                else:
                    break

            finishing_balance = tube_journey(finishing_balance, start_point, end_point)

            # small reminder
            if finishing_balance < 5.00:
                print("You will have zero charge soon! ({:.2f} GBP)".format(finishing_balance))

            # Here we ask customer to continue his journey if TUBE option is chosen
            while True:
                ex_status = input("Would you like to continue your journey? ([y]/n): ").lower()
                if not ex_status or ex_status == 'y':
                    break

                if ex_status not in ('y', 'n'):
                    print('Please choose correct option.')
                    continue

                if ex_status == 'n':
                    raise KeyboardInterrupt
        except:
            print("Thank you for journey!")
            break

    if finishing_balance <= 0.00:
        finishing_balance = 0.00
        print("Thank you for journey!")

    # The end
    print("The Oyster card charge left: {:.2f} GBP".format(finishing_balance))


if __name__ == '__main__':
    main()


import unittest

class FareTestCase(unittest.TestCase):

    def test_zone_1_fare(self):
        tube_fare_zone1 = fare_2_charge("Holborn", "Earl's Court Zone 1")
        self.assertEqual(tube_fare_zone1, 2.50, "Wrong fare in Zone 1")

    def test_zone_incl_1_fare(self):
        tube_fare_incl_zone1 = fare_2_charge("Holborn", "Wimbledon")
        self.assertEqual(tube_fare_incl_zone1, 3.00, "Wrong fare between zones including zone 1")

    def test_zone_excl_1_fare(self):
        tube_fare_excl_zone1 = fare_2_charge("Wimbledon", "Hammersmith")
        self.assertEqual(tube_fare_excl_zone1, 2.25, "Wrong fare between zones excluding zone 1")

    def test_outter_fare(self):
        tube_fare_outter_zones = fare_2_charge("Hammersmith", "Earl's Court Zone 2")
        self.assertEqual(tube_fare_outter_zones, 2.00, "Wrong fare between zones excluding zone 1")


class RouteTestCase(unittest.TestCase):
    # 1 - Holborn, 2 - Earl's Court, 3 - Wimbledon, 4 - Hammersmith
    def setUp(self):
        self.balance = 30

    def test_journey_from_task(self):
        balance = tube_journey(self.balance, 1, 2)
        self.assertEqual(balance, self.balance - IN_ZONE1_FARE, "Probably you chose another Zone for Earl's Court")
        self.balance -= IN_ZONE1_FARE

        balance = journey_by_bus(balance=self.balance)
        self.assertEqual(balance, self.balance - BUS_FARE, "Amount are not equal, please check")
        self.balance -= BUS_FARE

        balance = tube_journey(self.balance, 2, 4)
        self.assertEqual(balance, self.balance - OUTTER_ONE_ZONE_FARE, "Probably you chose another Zone for Earl's Court")
        self.balance -= OUTTER_ONE_ZONE_FARE

        self.assertEqual(self.balance, 30 - IN_ZONE1_FARE - BUS_FARE - OUTTER_ONE_ZONE_FARE,
                         "Somewhere mistake appeared")

        print("Balance left: {:.2f}".format(self.balance))

    def test_journey_custom(self):
        balance = tube_journey(self.balance, 1, 3)
        self.assertEqual(balance, self.balance - OUTTER_TWO_ZONES_INCL_1, "Amount are not equal, please check")
        self.balance -= OUTTER_TWO_ZONES_INCL_1

        balance = journey_by_bus(balance=self.balance)
        self.assertEqual(balance, self.balance - BUS_FARE, "Amount are not equal, please check")
        self.balance -= BUS_FARE

        balance = journey_by_bus(balance=self.balance)
        self.assertEqual(balance, self.balance - BUS_FARE, "Amount are not equal, please check")
        self.balance -= BUS_FARE

        balance = tube_journey(self.balance, 4, 1)
        self.assertEqual(balance, self.balance - OUTTER_TWO_ZONES_INCL_1, "Amount are not equal, please check")
        self.balance -= OUTTER_TWO_ZONES_INCL_1

        balance = tube_journey(self.balance, 1, 2)
        self.assertEqual(balance, self.balance - IN_ZONE1_FARE, "Probably you chose another Zone for Earl's Court")
        self.balance -= IN_ZONE1_FARE

        self.assertEqual(self.balance, 30 - OUTTER_TWO_ZONES_INCL_1 - BUS_FARE - BUS_FARE - OUTTER_TWO_ZONES_INCL_1 - IN_ZONE1_FARE,
                         "Somewhere mistake appeared")

        print("Balance left: {:.2f}".format(self.balance))


if __name__ == '__main__':
    unittest.main(verbosity=2)
