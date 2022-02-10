from bid import Bid


class Auction:
    """
    Class that models an auction
    """

    UNSOLD_STATUS = "UNSOLD"
    SOLD_STATUS = "SOLD"
    IN_PROGRESS_STATUS = "IN PROGRESS"
    KEYS_TO_OUTPUT = [
        "close_time",
        "item",
        "winning_bid_user_id",
        "status",
        "price_paid",
        "total_valid_bid_count",
    ]

    def __init__(self, *, timestamp, user_id, item, reserve_price, close_time):
        self.timestamp = timestamp
        self.user_id = user_id
        self.item = item
        self.reserve_price = reserve_price
        self.close_time = close_time
        self.bids = []
        self.open = True
        self.status = self.IN_PROGRESS_STATUS

        self.lowest_bid = 0
        self.highest_bid = 0
        self.winning_bid_user_id = None
        self.total_valid_bid_count = 0
        self.price_paid = 0

    def add_bid(self, row_data):
        bid = Bid(
            timestamp=int(row_data[0]),
            user_id=int(row_data[1]),
            item=str(row_data[3]),
            amount=float(row_data[4]),
        )

        current_max_bid_amount = 0

        for existing_bid in self.bids:
            if current_max_bid_amount < existing_bid.amount:
                current_max_bid_amount = existing_bid.amount

        if bid.amount <= current_max_bid_amount:
            return (
                f"Bid of {bid.amount} needs to be larger than existing max bid of {current_max_bid_amount}",
                bid,
            )

        if bid.timestamp > self.close_time:
            return (
                f"This auction closed at: {self.close_time}. The time now is: {bid.timestamp}",
                bid,
            )

        self.bids.append(bid)
        return "", bid

    def end(self):
        self._sort_bids()

        highest_bid = self._get_highest_bid()
        status = self._calculate_status(highest_bid)
        self.status = status
        self.price_paid = self._calculate_price_paid(status)
        self.total_valid_bid_count = len(self.bids)
        self.highest_bid = highest_bid
        self.lowest_bid = self._get_lowest_bid()
        self.winning_bid_user_id = self._get_winning_bid_user_id(status, highest_bid)

        return self._output()

    def _calculate_price_paid(self, status):
        if status == self.SOLD_STATUS:
            if len(self.bids) == 1:
                # NB: This assumes there is ALWAYS a reservePrice
                # An item with no reserve presents issues given we do not consider a 'starting_price' (it is implicitly 0)
                # A sensible addition would be the concept of a `minimumValidBidAmount` or a
                # 'defaultStartingPrice' (e.g. 1) to ensure that a price is always paid in this scenario.
                return self.reserve_price

            # The requirements state:
            #  - At the end of the auction the winner will pay the price of the second highest bidder.
            #  - If there is only a single 'valid' bid they will pay the reserve price of the auction.
            #  - If two bids are received for the same amount then the earliest bid wins the item.

            # In reality the situation is more complex:
            # - At the end of the auction the winner will pay the price of the second highest bidder only if BOTH of these bids exceeded the reserve price.

            # When >= 2 bids
            # - 1 exceeding reserve, 1 below reserve => highest bidder will pay reserve price
            # - Both exceeding or equal to reserve => highester bidder will pay second highest bid
            # - Both below reserve => return 0.00 - UNSOLD item. (NB: this block is not executed in this case)

            second_highest_bid_amount = self.bids[-2].amount
            if second_highest_bid_amount >= self.reserve_price:
                return second_highest_bid_amount

            # If the second highest bid is below the reserve price then the highest bidder pays the reserve.
            # We have already confirmed that highestBid >= listing.reservePrice in `calculateStatus`
            return self.bids[-1].amount

        return 0.00

    def _output(self):
        out = {key: self.__dict__[key] for key in self.KEYS_TO_OUTPUT}
        out["highest_bid"] = "${:.2f}".format(self.highest_bid.amount)
        out["lowest_bid"] = "${:.2f}".format(self.lowest_bid.amount)
        out["price_paid"] = "${:.2f}".format(self.price_paid)
        return out

    def _calculate_status(self, highest_bid):
        if highest_bid.amount >= self.reserve_price:
            return self.SOLD_STATUS

        return self.UNSOLD_STATUS

    def _get_lowest_bid(self):
        return self.bids[0] if len(self.bids) > 0 else Bid.null_bid()

    def _get_highest_bid(self):
        return self.bids[-1] if len(self.bids) > 0 else Bid.null_bid()

    def _get_winning_bid_user_id(self, status, highest_bid):
        if status == self.SOLD_STATUS:
            return highest_bid.user_id
        else:
            return None

    def _sort_bids(self):
        # Sorts the bids slice by bids in ascending order (i.e. highest bids last)
        # Secondary sort by timestamp in descending order (i.e. earliest bid last)
        #
        # This allows us to access the last element for the earliest AND highest bid.
        # The second last element for the second highest bid whether this is:
        # 1. A bid of the same amount but made at a later date
        # 2. A bid of a lower amount but made at any time.
        self.bids.sort(key=lambda b: (b.amount, -b.timestamp))
