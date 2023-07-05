class IP:
    """
    This class represents an IP address as four binary octets with custom octet length.
    """

    def __init__(self, ipv4_address: str, number_of_bits: int = 8, is_mask: bool = False):
        """
        The initial method.
        Args:
            ipv4_address: The network address as a string.
            number_of_bits: The length of octet in bits.
            is_mask: Flag for network mask determination.
        Attributes:
            self._number_of_bits: The length of octet in bits.
            self._is_mask: Flag for network mask determination.
            self._str_ip: The IPv4 string representation.
            self._valid_mask_values: The valid octets values for the netmask.
            self._ip: The IPv4 binary representation.
        """

        self._number_of_bits = number_of_bits
        self._is_mask = is_mask
        self._str_ip = ipv4_address
        self._valid_mask_values = self._generate_valid_mask_values()
        self._ip = self._get_binary_octets(ipv4_address)

    def __str__(self):
        return self._str_ip

    def _generate_valid_mask_values(self) -> list:
        """
        A getter method that returns IPv4 address as a list of binary octets.

        Returns:
            The list of binary octets.
        """

        return [2 ** self._number_of_bits - 2 ** i for i in range(self._number_of_bits + 1)]

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
        _flag = True
        ipv4_splitted = ipv4_address.split(".")
        for octet in ipv4_splitted:
            if not self._is_mask:
                if int(octet) not in range(0, 2**self._number_of_bits):
                    _flag = False
            else:
                if int(octet) not in self._valid_mask_values:
                    _flag = False
        if _flag:
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
