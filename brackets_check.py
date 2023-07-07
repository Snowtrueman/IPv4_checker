def check_string(string: str) -> bool:
    opened_ct = 0
    closed_ct = 0
    for symbol in string:
        if symbol in ["(", ")"]:
            if (symbol == ")" and opened_ct == 0) or (symbol == ")" and opened_ct < closed_ct + 1):
                return False
            if symbol == ")" and opened_ct != 0:
                closed_ct += 1
            if symbol == "(":
                opened_ct += 1
    if opened_ct != closed_ct:
        return False
    return True


if __name__ == "__main__":
    test_string = "(())))))(()()()()("
    result = check_string(test_string)
    if result:
        print("Valid")
    else:
        print("Not valid")