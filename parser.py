import logging
from utils import has_error
from orchestrator import Orchestrator

logging.basicConfig(level=logging.DEBUG)


class Parser:
    """
    Opens & parses the input file.
    """

    DEFAULT_INPUT_FILE_PATH = "inputs/basic.txt"

    def __init__(self, file_path=DEFAULT_INPUT_FILE_PATH):
        self._file_path = file_path
        self._orchestrator = Orchestrator()

    def parse(self):
        with open(self._file_path, "r") as f:
            data = f.read()

        for idx, row in enumerate(data.split()):
            self.__handle_row(row.split("|"), idx + 1)

        # print("----- Registry at end ------")
        # for key, value in self._orchestrator._auction_registry.items():
        #     print(value.__dict__)
        # print(self._orchestrator._expiry_registry)

    def __handle_row(self, row_data, row_number):
        if len(row_data) == 1:
            pass  # no-op (heartbeat)
        elif row_data[2] == "SELL":
            error, auction = self._orchestrator.register_auction(row_data)
            self.__log_status(error, auction)
        elif row_data[2] == "BID":
            error, bid = self._orchestrator.register_bid(row_data)
            self.__log_status(error, bid)
        else:
            log.info(f"Unidentified line at row {row_number+1}")

        timestamp = int(row_data[0])
        output = self._orchestrator.handle_ending_listings(timestamp)
        output = [o for o in output if o is not None]

        if len(output) > 0:
            for o in output:
                generator_obj = ((f"{value}|") for key, value in o.items())
                print("".join(generator_obj))

    def __log_status(self, error, obj):
        logging.info(
            f"{type(obj).__name__} {'failed' if has_error(error) else 'registered'} - {error} - {obj.__dict__ if obj is not None else ''}"
        )


# p = Parser()
# p.parse()
