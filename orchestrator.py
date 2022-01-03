from auction import Auction
from utils import has_error


class Orchestrator:
    """
    Orchestrates the Auction process
    """

    def __init__(self):
        self._auction_registry = {}
        self._expiry_registry = {}

    def register_auction(self, row_data):
        auction = Auction(
            timestamp=int(row_data[0]),
            user_id=int(row_data[1]),
            item=str(row_data[3]),
            reserve_price=float(row_data[4]),
            close_time=int(row_data[5]),
        )

        error = self.__add_auction_to_auction_registry(auction)
        if has_error(error):
            return error, auction

        self.__add_auction_to_expiry_registry(auction)
        return error, auction

    def register_bid(self, row_data):
        item_identifier = str(row_data[3])

        if item_identifier not in self._auction_registry:
            return (
                "Auction does not exist (at all)",
                None,
            )

        auction = self._auction_registry[item_identifier]
        return auction.add_bid(row_data)

    def handle_ending_listings(self, timestamp):
        output = []
        if timestamp in self._expiry_registry:
            for item in self._expiry_registry[timestamp]:

                auction = self._auction_registry[item]
                output.append(auction.end())

        return output

    def __add_auction_to_auction_registry(self, auction):
        if auction.item in self._auction_registry:
            return "An auction for this item already exists"

        self._auction_registry[auction.item] = auction
        return ""

    def __add_auction_to_expiry_registry(self, auction):
        if auction.close_time in self._expiry_registry:
            self._expiry_registry[auction.close_time].append(auction.item)
        else:
            self._expiry_registry[auction.close_time] = [auction.item]
