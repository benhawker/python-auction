import pytest

from parser import Parser


def describe_parse():
    def describe_with_the_default_input():
        def returns_the_correct_output(capfd):
            p = Parser()
            p.parse()

            out, err = capfd.readouterr()
            assert (
                out
                == "20|toaster_1|8|SOLD|$12.50|3|$20.00|$7.50|\n20|tv_1|None|UNSOLD|$0.00|2|$200.00|$150.00|\n"
            )

    def describe_with_the_default_input():
        def returns_the_correct_output():
            with pytest.raises(
                ValueError, match="could not convert string to float: 'aaaa'"
            ):
                p = Parser(file_path="tests/inputs/invalid_input.txt")
                p.parse()
