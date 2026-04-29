"""
Questions:
 

    1. Complete the MiniVenmo.create_user() method to allow our application to create new users.

    2. Complete the User.pay() method to allow users to pay each other. Consider the following: 
    if user A is paying user B, user's A balance should be used if there's enough balance to cover 
    the whole payment, if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. 
    If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this
   

    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the User.retrieve_activity() and MiniVenmo.render_feed() methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the User.add_friend() method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

import re
import unittest
import uuid


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class FriendEvent:

    def __init__(self, actor, target):
        self.id = str(uuid.uuid4())
        self.actor = actor
        self.target = target


class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0

        # chronological list of Payment and FriendEvent objects for this users feed
        self._feed = []
        # list of User objects this user has added as friends
        self._friends = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')


    def retrieve_feed(self):
        # return the users activity feed in chronological order
        return self._feed

    def add_friend(self, new_friend):
        # record the friendship and add a FriendEvent to both users feeds
        # so the event shows up when either user views their activity
        self._friends.append(new_friend)
        event = FriendEvent(self, new_friend)
        self._feed.append(event)
        new_friend._feed.append(event)

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        # use balance if there's enough to cover the full amount, otherwise charge the card
        # after payment succeeds, append to both users feeds
        amount = float(amount)
        if self.balance >= amount:
            payment = self.pay_with_balance(target, amount, note)
        else:
            payment = self.pay_with_card(target, amount, note)
        self._feed.append(payment)
        target._feed.append(payment)
        return payment

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        # validate, deduct from actor balance and credit the target
        # feed recording is left to pay() so this stays focused
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.balance < amount:
            raise PaymentException('Insufficient balance.')

        self.balance -= amount
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        # instantiate a user, set starting balance and register the credit card
        user = User(username)
        user.add_to_balance(balance)
        user.add_credit_card(credit_card_number)
        return user

    def render_feed(self, feed):
        # Bobby paid Carol $5.00 for Coffee
        # Carol paid Bobby $15.00 for Lunch
        # print each event, branch on type to pick the right format
        for event in feed:
            if isinstance(event, Payment):
                print(f"{event.actor.username} paid {event.target.username} ${event.amount:.2f} for {event.note}")
            elif isinstance(event, FriendEvent):
                print(f"{event.actor.username} and {event.target.username} are now friends")

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")
 
            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()


class TestCreateUser(unittest.TestCase):

    def setUp(self):
        self.venmo = MiniVenmo()

    def test_create_user_sets_balance(self):
        user = self.venmo.create_user("Bobby", 7.50, "4111111111111111")
        self.assertEqual(user.balance, 7.50)

    def test_create_user_sets_credit_card(self):
        user = self.venmo.create_user("Bobby", 0.0, "4111111111111111")
        self.assertEqual(user.credit_card_number, "4111111111111111")


class TestPay(unittest.TestCase):

    def setUp(self):
        venmo = MiniVenmo()
        self.bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        self.carol = venmo.create_user("Carol", 10.00, "4242424242424242")

    def test_pay_uses_balance_when_sufficient(self):
        self.bobby.pay(self.carol, 5.00, "Coffee")
        self.assertEqual(self.bobby.balance, 5.00)
        self.assertEqual(self.carol.balance, 15.00)

    def test_pay_uses_card_when_balance_insufficient(self):
        # actor balance should stay unchanged when card is used
        self.bobby.pay(self.carol, 15.00, "Dinner")
        self.assertEqual(self.bobby.balance, 10.00)
        self.assertEqual(self.carol.balance, 25.00)

    def test_pay_uses_balance_when_exact(self):
        self.bobby.pay(self.carol, 10.00, "Exact")
        self.assertEqual(self.bobby.balance, 0.0)

    def test_pay_appends_to_actor_feed(self):
        payment = self.bobby.pay(self.carol, 5.00, "Coffee")
        self.assertIn(payment, self.bobby._feed)

    def test_pay_appends_to_target_feed(self):
        payment = self.bobby.pay(self.carol, 5.00, "Coffee")
        self.assertIn(payment, self.carol._feed)

    def test_pay_returns_payment_with_correct_fields(self):
        payment = self.bobby.pay(self.carol, 5.00, "Coffee")
        self.assertIsInstance(payment, Payment)
        self.assertEqual(payment.amount, 5.00)
        self.assertEqual(payment.actor, self.bobby)
        self.assertEqual(payment.target, self.carol)
        self.assertEqual(payment.note, "Coffee")


class TestPayWithBalance(unittest.TestCase):

    def setUp(self):
        self.bobby = User("Bobby")
        self.bobby.add_to_balance(10.00)
        self.carol = User("Carol")

    def test_pay_with_balance_decreases_actor_balance(self):
        self.bobby.pay_with_balance(self.carol, 4.00, "Snacks")
        self.assertEqual(self.bobby.balance, 6.00)

    def test_pay_with_balance_increases_target_balance(self):
        self.bobby.pay_with_balance(self.carol, 4.00, "Snacks")
        self.assertEqual(self.carol.balance, 4.00)

    def test_pay_with_balance_exact_amount(self):
        self.bobby.pay_with_balance(self.carol, 10.00, "All in")
        self.assertEqual(self.bobby.balance, 0.0)

    def test_pay_with_balance_insufficient_raises(self):
        with self.assertRaises(PaymentException):
            self.bobby.pay_with_balance(self.carol, 99.00, "Too much")

    def test_pay_with_balance_returns_payment_with_correct_fields(self):
        payment = self.bobby.pay_with_balance(self.carol, 3.00, "Coffee")
        self.assertIsInstance(payment, Payment)
        self.assertEqual(payment.actor, self.bobby)
        self.assertEqual(payment.target, self.carol)
        self.assertEqual(payment.amount, 3.00)
        self.assertEqual(payment.note, "Coffee")

    def test_pay_with_balance_does_not_touch_feed(self):
        # feed management is pay()'s responsibility, not pay_with_balance()'s
        self.bobby.pay_with_balance(self.carol, 3.00, "Coffee")
        self.assertEqual(self.bobby._feed, [])
        self.assertEqual(self.carol._feed, [])


class TestRetrieveFeed(unittest.TestCase):

    def setUp(self):
        venmo = MiniVenmo()
        self.bobby = venmo.create_user("Bobby", 20.00, "4111111111111111")
        self.carol = venmo.create_user("Carol", 20.00, "4242424242424242")

    def test_feed_empty_for_new_user(self):
        fresh = User("Dave1")
        self.assertEqual(fresh.retrieve_feed(), [])

    def test_feed_contains_payment_as_actor(self):
        payment = self.bobby.pay(self.carol, 5.00, "Coffee")
        self.assertIn(payment, self.bobby.retrieve_feed())

    def test_feed_contains_payment_as_target(self):
        payment = self.bobby.pay(self.carol, 5.00, "Coffee")
        self.assertIn(payment, self.carol.retrieve_feed())

    def test_feed_is_ordered_chronologically(self):
        p1 = self.bobby.pay(self.carol, 5.00, "First")
        p2 = self.carol.pay(self.bobby, 3.00, "Second")
        feed = self.bobby.retrieve_feed()
        self.assertEqual(feed.index(p1), 0)
        self.assertEqual(feed.index(p2), 1)

    def test_feed_contains_friend_event_after_add_friend(self):
        self.bobby.add_friend(self.carol)
        feed = self.bobby.retrieve_feed()
        self.assertEqual(len(feed), 1)
        self.assertIsInstance(feed[0], FriendEvent)

    def test_feed_contains_mixed_events_in_order(self):
        payment = self.bobby.pay(self.carol, 5.00, "Coffee")
        self.bobby.add_friend(self.carol)
        feed = self.bobby.retrieve_feed()
        self.assertIsInstance(feed[0], Payment)
        self.assertIsInstance(feed[1], FriendEvent)


class TestAddFriend(unittest.TestCase):

    def setUp(self):
        self.bobby = User("Bobby")
        self.carol = User("Carol")

    def test_add_friend_appears_in_friends_list(self):
        self.bobby.add_friend(self.carol)
        self.assertIn(self.carol, self.bobby._friends)

    def test_add_friend_event_in_actor_feed(self):
        self.bobby.add_friend(self.carol)
        event = self.bobby._feed[0]
        self.assertIsInstance(event, FriendEvent)
        self.assertEqual(event.actor, self.bobby)
        self.assertEqual(event.target, self.carol)

    def test_add_friend_event_also_in_target_feed(self):
        self.bobby.add_friend(self.carol)
        # same FriendEvent object should appear in Carol's feed too
        self.assertIn(self.bobby._feed[0], self.carol._feed)


class TestMiniVenmoRun(unittest.TestCase):

    def test_run_completes_without_error(self):
        MiniVenmo.run()


if __name__ == '__main__':
    unittest.main()