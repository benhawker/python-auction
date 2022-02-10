import pytest
from auction import Auction
from bid import Bid
from orchestrator import Orchestrator


@pytest.fixture
def item_name_1():
    return "tv"


@pytest.fixture
def item_name_2():
    return "toaster"


@pytest.fixture
def close_time_1():
    return "20"


@pytest.fixture
def close_time_2():
    return "21"


def auction(sell_row):
    return Auction(
        timestamp=int(sell_row[0]),
        user_id=int(sell_row[1]),
        item=str(sell_row[3]),
        reserve_price=float(sell_row[4]),
        close_time=int(sell_row[5]),
    )


def __sell_row(item="toaster_1", close_time="20"):
    return ["10", "1", "SELL", item, "10.00", close_time]


def describe_register_auction():
    def describe_one_listing():
        def returns_true(item_name_1):
            o = Orchestrator()
            sell_row = __sell_row(item=item_name_1)
            return_value = o.register_auction(sell_row)

            assert return_value[0] == ""
            assert return_value[1].__dict__ == auction(sell_row).__dict__

        def it_adds_to_the_auction_registry(item_name_1):
            o = Orchestrator()
            sell_row = __sell_row(item=item_name_1)
            o.register_auction(sell_row)

            assert item_name_1 in o._auction_registry
            assert (
                o._auction_registry[item_name_1].__dict__ == auction(sell_row).__dict__
            )

        def it_adds_to_the_expiry_registry(close_time_1):
            o = Orchestrator()
            sell_row = __sell_row(close_time=close_time_1)
            o.register_auction(sell_row)

            assert (int(close_time_1), [sell_row[3]]) in o._expiry_registry.items()

    def describe_multiple_listings_ending_at_same_time():
        def it_adds_both_to_the_auction_registry(
            item_name_1, item_name_2, close_time_1
        ):
            o = Orchestrator()
            sell_row_1 = __sell_row(item=item_name_1, close_time=close_time_1)
            sell_row_2 = __sell_row(item=item_name_2, close_time=close_time_1)
            o.register_auction(sell_row_1)
            o.register_auction(sell_row_2)

            assert item_name_1 in o._auction_registry
            assert (
                o._auction_registry[item_name_1].__dict__
                == auction(sell_row_1).__dict__
            )

            assert item_name_2 in o._auction_registry
            assert (
                o._auction_registry[item_name_2].__dict__
                == auction(sell_row_2).__dict__
            )

        def it_adds_both_to_the_expiry_registry(item_name_1, item_name_2, close_time_1):
            o = Orchestrator()
            sell_row_1 = __sell_row(item=item_name_1, close_time=close_time_1)
            sell_row_2 = __sell_row(item=item_name_2, close_time=close_time_1)
            o.register_auction(sell_row_1)
            o.register_auction(sell_row_2)

            assert (
                int(close_time_1),
                [item_name_1, item_name_2],
            ) in o._expiry_registry.items()

    def describe_multiple_listings_ending_at_different_times():
        def it_adds_both_to_the_auction_registry(
            item_name_1, item_name_2, close_time_1, close_time_2
        ):
            o = Orchestrator()
            sell_row_1 = __sell_row(item=item_name_1, close_time=close_time_1)
            sell_row_2 = __sell_row(item=item_name_2, close_time=close_time_2)
            o.register_auction(sell_row_1)
            o.register_auction(sell_row_2)

            assert item_name_1 in o._auction_registry
            assert (
                o._auction_registry[item_name_1].__dict__
                == auction(sell_row_1).__dict__
            )

            assert item_name_2 in o._auction_registry
            assert (
                o._auction_registry[item_name_2].__dict__
                == auction(sell_row_2).__dict__
            )

        def it_adds_both_to_the_expiry_registry(
            item_name_1, item_name_2, close_time_1, close_time_2
        ):
            o = Orchestrator()
            sell_row_1 = __sell_row(item=item_name_1, close_time=close_time_1)
            sell_row_2 = __sell_row(item=item_name_2, close_time=close_time_2)
            o.register_auction(sell_row_1)
            o.register_auction(sell_row_2)
            assert (
                int(close_time_1),
                [item_name_1],
            ) in o._expiry_registry.items()

            assert (
                int(close_time_2),
                [item_name_2],
            ) in o._expiry_registry.items()


def bid(bid_row):
    return Bid(
        timestamp=int(bid_row[0]),
        user_id=int(bid_row[1]),
        item=str(bid_row[3]),
        amount=float(bid_row[4]),
    )


def __bid_row(item="toaster_1"):
    return ["10", "1", "BID", item, "10.00"]


def describe_register_bid():
    def describe_valid_auction():
        def returns_true(item_name_1):
            o = Orchestrator()
            sell_row = __sell_row(item=item_name_1)
            o.register_auction(sell_row)

            bid_row = __bid_row(item=item_name_1)
            return_value = o.register_bid(bid_row)

            assert return_value[0] == ""
            assert return_value[1].__dict__ == bid(bid_row).__dict__

    def describe_not_found_auction_item():
        def returns_false():
            o = Orchestrator()
            bid_row = __bid_row()
            return_value = o.register_bid(bid_row)

            assert return_value[0] == "Auction does not exist (at all)"
            assert return_value[1] == None


def describe_handle_ending_listings():
    def describe_when_no_listings():
        def returns_an_empty_list():
            o = Orchestrator()
            return_value = o.handle_ending_listings(11)
            assert return_value == []

    def describe_when_no_listings_ending_on_the_timestamp():
        def returns_an_empty_list():
            o = Orchestrator()
            sell_row = __sell_row(item=item_name_1)
            o.register_auction(sell_row)

            return_value = o.handle_ending_listings(11)
            assert return_value == []

    def describe_when_a_single_listing_ending_on_the_timestamp():
        def returns_output_for_the_single_ending_listing():
            o = Orchestrator()
            sell_row = __sell_row(item="tv", close_time=20)
            o.register_auction(sell_row)

            return_value = o.handle_ending_listings(20)
            assert return_value == [
                {
                    "close_time": 20,
                    "highest_bid": "$0.00",
                    "item": "tv",
                    "lowest_bid": "$0.00",
                    "price_paid": "$0.00",
                    "status": "UNSOLD",
                    "total_valid_bid_count": 0,
                    "winning_bid_user_id": None,
                }
            ]

    def describe_when_multiple_listings_ending_on_the_timestamp():
        def returns_output_for_all_ending_listings():
            o = Orchestrator()
            sell_row_1 = __sell_row(item="tv", close_time=20)
            sell_row_2 = __sell_row(item="shoes", close_time=20)
            o.register_auction(sell_row_1)
            o.register_auction(sell_row_2)
            return_value = o.handle_ending_listings(20)

            assert return_value == [
                {
                    "close_time": 20,
                    "highest_bid": "$0.00",
                    "item": "tv",
                    "lowest_bid": "$0.00",
                    "price_paid": "$0.00",
                    "status": "UNSOLD",
                    "total_valid_bid_count": 0,
                    "winning_bid_user_id": None,
                },
                {
                    "close_time": 20,
                    "highest_bid": "$0.00",
                    "item": "shoes",
                    "lowest_bid": "$0.00",
                    "price_paid": "$0.00",
                    "status": "UNSOLD",
                    "total_valid_bid_count": 0,
                    "winning_bid_user_id": None,
                },
            ]
