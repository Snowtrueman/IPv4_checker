from ip import IP
from ip_checker import IPChecker


if __name__ == "__main__":
    network = input("Please enter the IPv4 network address: ")
    mask = input("Please enter the network mask: ")
    input_file = input("Please provide the list if IPs: ")
    try:
        binary_network = IP(network)
        binary_mask = IP(mask)
        result = IPChecker(binary_network, binary_mask, input_file)
        result.check()
    except ValueError:
        print(f"Your network address ({network}) or network mask ({mask}) are not valid")
    except FileNotFoundError:
        print(f"There is no such file or incorrect file type: {input_file}")
    except EnvironmentError:
        print("Missing .env file. Can't find it in project root directory.")
