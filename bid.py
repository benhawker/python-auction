class Bid:
    """
    Class that models a bid
    """

    def __init__(self, *, timestamp, user_id, item, amount):
        self.timestamp = timestamp
        self.user_id = user_id
        self.item = item
        self.amount = amount

    def null_bid():
        return Bid(
            timestamp=0,
            user_id=0,
            item="0",
            amount=0,
        )
