from ip import IP
from ip_checker import IPChecker


if __name__ == "__main__":
    number_of_bits = input("Please enter the length of one octet in bits: ")
    network = input("Please enter the IPv4 network address: ")
    mask = input("Please enter the network mask: ")
    input_file = input("Please provide the list if IPs: ")
    try:
        number_of_bits = int(number_of_bits)
        binary_network = IP(network, number_of_bits=number_of_bits)
        binary_mask = IP(mask, number_of_bits=number_of_bits, is_mask=True)
        result = IPChecker(binary_network, binary_mask, input_file)
        result.check()
    except ValueError:
        print(f"Your network address ({network}), network mask ({mask}) or octet length are not valid")
    except FileNotFoundError:
        print(f"There is no such file or incorrect file type: {input_file}")
    except EnvironmentError:
        print("Missing .env file. Can't find it in project root directory.")
