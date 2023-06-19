import os
import re
import csv
import time
import logging
import requests
from ip import IP
from dotenv import load_dotenv


class IPChecker:
    """
    This class checks the provided list of IP addresses for the belonging to the specified network based on the
    provided netmask.
    Returns a list of IP addresses satisfying this condition, with the ISP name for each of them.
    """

    def __init__(self, network: IP, mask: IP, path_to_ip_list: str):
        """
          The initial method.
          Args:
              network: The network address as an instance of IP class.
              mask: The network mask as an instance of IP class.
              path_to_ip_list: The string with a list of IPv4 addresses or the path to CSV file.
          Attributes:
              self._ip_list: Is used for temporary storage.
              self._verified_ip_dict: The result dictionary containing the valid IP addresses and ISP names.
              self._ip_pattern: A regex expression to extract IP addresses from the string.
              self._csv_param: Is set to True if the path_to_ip_list argument was recognized as a path to CSV file,
                    else False.
              self._csv_column_name: The exact name of the column with the list of IP addresses.
              self._csv_fieldnames: The values in the first row of CSV file (headers).
              self._csv_directory: The path to the csv file directory.
              self._csv_delimiter: Delimiter used in csv file (loaded from settings file).
              self._api_url: The URL of an API service for determining the ISP name (loaded from settings file).
              self._attempts_header: The HTTP header of an API service that contains the number of requests remaining
                    in the current rate limit window.
              self._timeout_header: The HTTP header of an API service provides the time to wait for next attempt if
                    the requests limit is reached (loaded from settings file).
          """

        self._logger = self._get_logger()
        self._load_env()

        # General attributes
        self._network = network
        self._mask = mask
        self._path_to_ip_list = path_to_ip_list
        self._ip_list = []
        self._verified_ip_dict = {}
        self._ip_pattern = re.compile(
            r"(?:^|\b(?<!\.))(?:1?\d?\d|2[0-4]\d|25[0-5])(?:\.(?:1?\d?\d|2[0-4]\d|25[0-5])){3}(?=$|[^\w.])")

        # CSV settings
        self._csv_param = True if self._check_path(path_to_ip_list) else False
        self._csv_column_name = None
        self._csv_fieldnames = None
        self._csv_directory = None
        self._csv_delimiter = os.environ.get("CSV_DELIMITER")

        # API settings
        self._api_url = os.environ.get("ISP_API_URL")
        self._attempts_header = os.environ.get("ISP_API_ATTEMPTS_HEADER")
        self._timeout_header = os.environ.get("ISP_API_TIMEOUT_HEADER")

    @staticmethod
    def _get_logger() -> logging.Logger:
        """
        Configures and creates logger.

        Returns:
            Logger instance.
        """

        logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(levelname)s | %(name)s --- %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
        return logging.getLogger("ip_checker")

    def _load_env(self) -> None:
        """
        Load all the variables found as environment variables in .env file.

        Returns:
            None
        Raises:
            EnvironmentError: If the .env file is missing.
        """
        dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            self._logger.info("Settings loaded successfully.")
        else:
            raise EnvironmentError

    def _check_path(self, path_to_ip_list) -> bool:
        """
        Checks the path_to_ip_list argument. Determines it as a list of IPv4 addresses or the path to a CSV file.

        Args:
            path_to_ip_list: The string with a list of IPv4 addresses or the path to CSV file.
        Returns:
            False if at least one IPv4 address was found in the path_to_ip_list argument else False.
        """
        return True if re.search(self._ip_pattern, path_to_ip_list) is None else False

    def _get_ip_from_string(self) -> None:
        """
        Extracts IPv4 addresses from the string using regex.

        Returns:
            None
        """

        ip_list = re.findall(self._ip_pattern, self._path_to_ip_list)
        for ip in ip_list:
            try:
                current_ip = IP(ip)
                self._ip_list.append(current_ip)
                self._logger.info(f"IPv4 addresses successfully extracted from list. "
                                  f"Detected {len(self._ip_list)} valid addresses.")
            except ValueError:
                continue

    def _get_ip_from_csv(self) -> None:
        """
        Extracts IPv4 addresses from the provided CSV file.

        Returns:
            None
        Raises:
            FileNotFoundError: If the extension of file is not .csv or if the format of provided data is incorrect.
        """

        _, file_extension = os.path.splitext(self._path_to_ip_list)
        self._csv_directory = os.path.dirname(self._path_to_ip_list)
        if file_extension != ".csv":
            raise FileNotFoundError

        with open(self._path_to_ip_list, encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=self._csv_delimiter)
            self._csv_fieldnames = reader.fieldnames
            if not self._csv_fieldnames:
                raise FileNotFoundError
            ip_column = [column for column in reader.fieldnames if column in ["ip", "IP", "iP", "Ip"]]
            if len(ip_column):
                ip_column, *_ = ip_column
                self._csv_column_name = ip_column
                ip_list = []
                for row in reader:
                    ip_list.append(row[ip_column])
            else:
                raise FileNotFoundError

        if "ip_list" in locals():
            for ip in ip_list:
                try:
                    current_ip = IP(ip)
                    self._ip_list.append(current_ip)
                except ValueError:
                    continue
            self._logger.info(f"IPv4 addresses successfully extracted from CSV file. "
                              f"Detected {len(self._ip_list)} valid addresses.")
        else:
            raise FileNotFoundError

    def _check_for_entry(self, ip: IP) -> bool:
        """
        Checks if the provided IPv4 address is in the specified network.

        Args:
            ip: The IPv4 address as an instance of IP class.
        Returns:
            None
        """

        result_network = []
        for i in range(4):
            result_network.append(str(int(ip.get_binary_ip()[i], 2) & int(self._mask.get_binary_ip()[i], 2)))
        result = ".".join(result_network)
        return str(self._network) == result

    def _get_isp(self, ip: str) -> str:
        """
        Defines the ISP name for provided IPv4 address.

        Args:
            ip: The IPv4 address as a string.
        Returns:
            The ISP name for provided IP address or error message.
        """
        try:
            request = requests.get(f"{self._api_url}{ip}", timeout=62)
            if request.headers.get(self._attempts_header) == "0":
                time_to_sleep = int(request.headers.get(self._timeout_header)) + 2
                self._logger.info(f"Requests limit is reached. "
                                  f"Need to wait for {time_to_sleep} seconds.")
                time.sleep(time_to_sleep)
            if request.status_code == 200:
                response = request.json()
                if response["status"] == "success":
                    return f"{response['isp']}"
                else:
                    return f"No information about ISP for IP: {ip} in remote service database."
            else:
                return "Some problems with connection to IP determining service"
        except requests.ConnectionError:
            return "Some problems with connection to IP determining service"

    def _perform_isp_check(self) -> None:
        """
        Performs the ISP name definition procedure.

        Returns:
            None
        """

        self._logger.info(f"Addresses were checked for belonging to the specified network. "
                          f"Detected {len(self._verified_ip_dict)} such addresses.")
        counter = 1
        for ip in self._verified_ip_dict:
            self._logger.info(f"Receiving information about IPS. "
                              f"{counter} of {len(self._verified_ip_dict)} done.")
            self._verified_ip_dict[ip] = self._get_isp(ip)
            counter += 1

    def _print_results(self) -> None:
        """
        Prints a list of IP addresses with the ISP name for each of them to console.

        Returns:
            None
        """

        counter = 1
        for ip, isp in self._verified_ip_dict.items():
            print(f"{counter}. {ip} -> {isp}")
            counter += 1

    def _export_results_to_csv(self) -> None:
        """
        Creates a new CSV file containing the information of the original file with the addition of a column with
        the ISP name.

        Returns:
            None
        """

        with open(self._path_to_ip_list, encoding="utf-8", newline="", ) as initial_csv, \
             open(os.path.join(self._csv_directory, "result.csv"), "w", encoding="utf-8", newline="", ) as result_csv:
            self._csv_fieldnames.append("provider")
            writer = csv.DictWriter(result_csv, fieldnames=self._csv_fieldnames, delimiter=self._csv_delimiter)
            writer.writeheader()
            for row in csv.DictReader(initial_csv, delimiter=self._csv_delimiter):
                if row[self._csv_column_name] in self._verified_ip_dict:
                    row["provider"] = self._verified_ip_dict[row[self._csv_column_name]]
                    writer.writerow(row)
                else:
                    continue

    def check(self) -> None:
        """
        Starts the verification procedure.

        Returns:
            None
        """

        if not self._csv_param:
            self._get_ip_from_string()
            self._logger.info("Detected the list of IPv4 addresses.")
            self._verified_ip_dict = {ip: None for ip in self._ip_list if self._check_for_entry(ip)}
            self._perform_isp_check()
            self._print_results()
        else:
            self._get_ip_from_csv()
            self._logger.info("Detected the CSV file with IPv4 addresses.")
            self._verified_ip_dict = {str(ip): None for ip in self._ip_list if self._check_for_entry(ip)}
            self._perform_isp_check()
            self._export_results_to_csv()
