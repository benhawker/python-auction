import pytest
from auction import Auction
from bid import Bid


def describe_end():
    def when_there_are_no_bids():
        def returns_true(item_name_1):
            auction = Auction("10", "1", "SELL", "toaster_1", "10.00", "20")
            assert auction.end() == None

    def when_there_are_bids():
        def it_adds_both_to_the_auction_registry():
            auction = Auction("10", "1", "SELL", "toaster_1", "10.00", "20")
            bid = Bid("21", "1", "toaster_1", "100")
            auction.bids = [bid]
            assert return_value == "bob"
