import re


class IP:
    """
    This class represents an IP address as four binary octets.
    """

    def __init__(self, ipv4_address: str):
        self._ip_pattern = r"^(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?!$)|$)){4}$"
        self._ip = self._get_binary_octets(ipv4_address)
        self._str_ip = ipv4_address

    def __str__(self):
        return self._str_ip

    def _get_binary_octets(self, ipv4_address: str) -> list:
        """
        Checks the format of the provided IP address and converts it to binary octets.
        Args:
            ipv4_address: IPv4 address in string format.

        Returns:
            The list of binary octets.
        Raises:
            ValueError: If the format does not match.
        """

        if re.match(self._ip_pattern, ipv4_address):
            return [bin(int(octet)) for octet in ipv4_address.split(".")]
        else:
            raise ValueError

    def get_binary_ip(self) -> list:
        """
        A getter method that returns IPv4 address as a list of binary octets.

        Returns:
            The list of binary octets.
        """

        return self._ip
