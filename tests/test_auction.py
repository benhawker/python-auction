import pytest
from auction import Auction
from bid import Bid


def describe_add_bid():
    def describe_when_the_bid_is_valid():
        def it_returns_no_error():
            auction = Auction(
                timestamp=10,
                user_id="1",
                item="shoes",
                reserve_price=10.00,
                close_time=20,
            )

            bid_row = ["10", "1", "BID", "shoes", "12.00"]
            expected_bid = Bid(
                timestamp=int(bid_row[0]),
                user_id=int(bid_row[1]),
                item=str(bid_row[3]),
                amount=float(bid_row[4]),
            )
            return_value = auction.add_bid(bid_row)
            assert len(return_value) == 2
            assert return_value[0] == ""
            assert return_value[1].__dict__ == expected_bid.__dict__

        def it_adds_the_bid():
            auction = Auction(
                timestamp=10,
                user_id="1",
                item="shoes",
                reserve_price=10.00,
                close_time=20,
            )

            bid_row = ["10", "1", "BID", "shoes", "12.00"]

            auction.add_bid(bid_row)
            assert len(auction.bids) == 1

    def describe_when_the_bid_is_not_greater_than_an_existing_bid():
        def it_returns_the_correct_error():
            auction = Auction(
                timestamp=10,
                user_id="1",
                item="shoes",
                reserve_price=10.00,
                close_time=20,
            )

            bid_row = ["10", "1", "BID", "shoes", "12.00"]
            bid_row_2 = ["11", "2", "BID", "shoes", "11.00"]

            expected_bid = Bid(
                timestamp=int(bid_row_2[0]),
                user_id=int(bid_row_2[1]),
                item=str(bid_row_2[3]),
                amount=float(bid_row_2[4]),
            )

            auction.add_bid(bid_row)
            return_value = auction.add_bid(bid_row_2)
            assert len(return_value) == 2
            assert (
                return_value[0]
                == "Bid of 11.0 needs to be larger than existing max bid of 12.0"
            )
            assert return_value[1].__dict__ == expected_bid.__dict__

        def it_does_not_add_the_bid():
            auction = Auction(
                timestamp=10,
                user_id="1",
                item="shoes",
                reserve_price=10.00,
                close_time=20,
            )

            bid_row = ["10", "1", "BID", "shoes", "12.00"]
            bid_row_2 = ["11", "2", "BID", "shoes", "11.00"]
            auction.add_bid(bid_row)
            auction.add_bid(bid_row_2)
            assert len(auction.bids) == 1

    def describe_when_bid_is_received_after_the_auction_has_closed():
        def it_returns_the_correct_error():
            auction = Auction(
                timestamp=10,
                user_id="1",
                item="shoes",
                reserve_price=10.00,
                close_time=20,
            )

            bid_row = ["10", "1", "BID", "shoes", "12.00"]
            bid_row_2 = ["21", "2", "BID", "shoes", "16.00"]

            expected_bid = Bid(
                timestamp=int(bid_row_2[0]),
                user_id=int(bid_row_2[1]),
                item=str(bid_row_2[3]),
                amount=float(bid_row_2[4]),
            )

            auction.add_bid(bid_row)
            return_value = auction.add_bid(bid_row_2)
            assert len(return_value) == 2
            assert return_value[0] == "This auction closed at: 20. The time now is: 21"
            assert return_value[1].__dict__ == expected_bid.__dict__

        def it_does_not_add_the_bid():
            auction = Auction(
                timestamp=10,
                user_id="1",
                item="shoes",
                reserve_price=10.00,
                close_time=20,
            )

            bid_row = ["10", "1", "BID", "shoes", "12.00"]
            bid_row_2 = ["21", "2", "BID", "shoes", "16.00"]

            auction.add_bid(bid_row)
            auction.add_bid(bid_row_2)
            assert len(auction.bids) == 1


def describe_end():
    def describe_when_there_are_no_bids():
        def returns_the_correct_output():
            auction = Auction(
                timestamp=10,
                user_id="1",
                item="shoes",
                reserve_price=10.00,
                close_time=20,
            )
            return_value = auction.end()
            assert return_value == {
                "close_time": 20,
                "item": "shoes",
                "winning_bid_user_id": None,
                "status": "UNSOLD",
                "price_paid": "$0.00",
                "total_valid_bid_count": 0,
                "highest_bid": "$0.00",
                "lowest_bid": "$0.00",
            }

    def describe_when_there_is_a_single_bid():
        def describe_when_the_reserve_is_met():
            def it_returns_the_correct_output():
                auction = Auction(
                    timestamp=10,
                    user_id="1",
                    item="shoes",
                    reserve_price=10.00,
                    close_time=20,
                )
                auction.add_bid(["10", "1", "BID", "shoes", "12.00"])
                return_value = auction.end()
                assert return_value == {
                    "close_time": 20,
                    "item": "shoes",
                    "winning_bid_user_id": 1,
                    "status": "SOLD",
                    "price_paid": "$10.00",
                    "total_valid_bid_count": 1,
                    "highest_bid": "$12.00",
                    "lowest_bid": "$12.00",
                }

        def describe_when_the_reserve_is_not_met():
            def it_returns_the_correct_output():
                auction = Auction(
                    timestamp=10,
                    user_id="1",
                    item="shoes",
                    reserve_price=10.00,
                    close_time=20,
                )
                auction.add_bid(["10", "1", "BID", "shoes", "9.00"])
                return_value = auction.end()
                assert return_value == {
                    "close_time": 20,
                    "item": "shoes",
                    "winning_bid_user_id": None,
                    "status": "UNSOLD",
                    "price_paid": "$0.00",
                    "total_valid_bid_count": 1,
                    "highest_bid": "$9.00",
                    "lowest_bid": "$9.00",
                }

    def describe_when_there_are_multiple_bids():
        def describe_when_the_reserve_is_met():
            def it_returns_the_correct_output():
                auction = Auction(
                    timestamp=10,
                    user_id="1",
                    item="shoes",
                    reserve_price=10.00,
                    close_time=20,
                )
                auction.add_bid(["10", "1", "BID", "shoes", "11.00"])
                auction.add_bid(["11", "2", "BID", "shoes", "12.00"])
                return_value = auction.end()
                assert return_value == {
                    "close_time": 20,
                    "item": "shoes",
                    "winning_bid_user_id": 2,
                    "status": "SOLD",
                    "price_paid": "$11.00",
                    "total_valid_bid_count": 2,
                    "highest_bid": "$12.00",
                    "lowest_bid": "$11.00",
                }

        def describe_when_the_reserve_is_not_met():
            def it_returns_the_correct_output():
                auction = Auction(
                    timestamp=10,
                    user_id="1",
                    item="shoes",
                    reserve_price=10.00,
                    close_time=20,
                )
                auction.add_bid(["10", "1", "BID", "shoes", "8.00"])
                auction.add_bid(["11", "1", "BID", "shoes", "9.00"])
                return_value = auction.end()

                assert return_value == {
                    "close_time": 20,
                    "item": "shoes",
                    "winning_bid_user_id": None,
                    "status": "UNSOLD",
                    "price_paid": "$0.00",
                    "total_valid_bid_count": 2,
                    "highest_bid": "$9.00",
                    "lowest_bid": "$8.00",
                }

        def describe_when_the_reserve_is_met_but_only_one_bid_exceeds_it():
            def it_returns_the_correct_output():
                auction = Auction(
                    timestamp=10,
                    user_id="1",
                    item="shoes",
                    reserve_price=10.00,
                    close_time=20,
                )
                auction.add_bid(["11", "1", "BID", "shoes", "8.00"])
                auction.add_bid(["12", "2", "BID", "shoes", "11.00"])
                return_value = auction.end()

                assert return_value == {
                    "close_time": 20,
                    "item": "shoes",
                    "winning_bid_user_id": 2,
                    "status": "SOLD",
                    "price_paid": "$11.00",
                    "total_valid_bid_count": 2,
                    "highest_bid": "$11.00",
                    "lowest_bid": "$8.00",
                }
