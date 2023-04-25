from src.config import Config
from src.app.logger import Logger
from datetime import datetime
import logging
import json
import os
import time
from pycti import OpenCTIApiClient
import glob
from getpass import getpass
import sys


class OpenCTI:
    """
    Description: Collecting ioc information via opencti
    """

    def __init__(self) -> None:
        """
        Constructor Method
        :param: none
        :return: none
        """
        # Variables
        self.api_url = input('API URL: ')
        self.api_token = getpass('API Token: ')
        date = datetime.today().strftime('%Y-%m-%d')
        self.data_dir = Config.DATA_DIR
        self.data_raw_dir = Config.DATA_RAW_DIR
        self.logger = Logger('OpenCTI')
        self.position_file = self.data_dir + date + '_indicator-position.txt'
        self.data_raw_file = self.data_raw_dir + date + ' _data-raw.log'
        self.data_IoC_dir = Config.DATA_IOC_DIR
        self.data_IoC_file = self.data_IoC_dir + 'opencti'

        print("""
██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗███████╗██████╗ 
██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║██╔════╝██╔══██╗
██║ █╗ ██║███████║   ██║   ██║     ███████║█████╗  ██████╔╝
██║███╗██║██╔══██║   ██║   ██║     ██╔══██║██╔══╝  ██╔══██╗
╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                                                     
        """)

    def check_connection(self):

        try:
            # OpenCTI initialization
            opencti_api_client = OpenCTIApiClient(self.api_url, self.api_token)

            final_indicators = []
            # Get all reports using the pagination
            data = opencti_api_client.indicator.list(
                first=1,
                after=None,
                withPagination=True,
                orderBy="created_at",
                orderMode="desc",
            )
            final_indicators += data["entities"]

            for indicator in final_indicators:
                print(f"""
Sample:
[{indicator["created"]}] - {indicator["id"]} - {indicator["pattern"]}
                      """)
            print("""
######################################
Starting..............................
######################################
            """)
            time.sleep(10)
            self.get_black_list()

        except Exception as e:
            self.logger.log(logging.WARNING, "Connection failed")
            self.logger.log(logging.ERROR, e)
            print(
                'Connection failed please make sure you entered your credentials correctly')

    def get_black_list(self, retry_count=30):
        """
        Used for read packets in given directory
            :param: none
            :return: none
        """
        try:
            # OpenCTI initialization
            opencti_api_client = OpenCTIApiClient(self.api_url, self.api_token)

            # # Get all reports using the pagination
            # custom_attributes = """
            #     id
            #     pattern_type
            #     created
            # """
            final_indicators = []
            # data = {"pagination": {"hasNextPage": True, "endCursor": None}}
            data = self.position()
            last_line = self.position_check(data["pagination"]["endCursor"])
            while data["pagination"]["hasNextPage"]:
                after = data["pagination"]["endCursor"]
                if after == last_line:
                    print("""
############################
# Same hash values found #
############################
                    """)
                    self.logger.log(logging.INFO, f"""
    => after:     "{after}"
    => last_Line: "{last_line}"
                    """)
                    self.exit_opencti()
                else:
                    self.position_write(after)
                    self.logger.log(logging.INFO, data["pagination"])
                    data = opencti_api_client.indicator.list(
                        first=5000,
                        after=after,
                        # customAttributes=custom_attributes,
                        withPagination=True,
                        orderBy="created_at",
                        orderMode="desc",
                    )
                    final_indicators += data["entities"]
                    self.data_write_raw_log(data)
                    time.sleep(2)

            for indicator in final_indicators:
                print("[" + indicator["created"] + "] " + indicator["id"])

            print("""
######################################
#Finished............................#
######################################
                """)

        except Exception as e:
            self.logger.log(logging.WARNING, "Script Crash")
            self.logger.log(logging.ERROR, e)
            if retry_count > 0:
                print("Connection lost will restart")
                print(f"""
{'#'*retry_count*(retry_count*5)}
Error occured. Retrying {retry_count} more times...
{'#'*retry_count*(retry_count*5)}
                """)
                time.sleep(60)
                print("""
######################################
Restart...............................
######################################
                """)
                self.get_black_list(retry_count - 1)
            else:
                print("Error occured and maximum retry count reached. Aborting...")

    def position(self) -> json:
        try:
            if os.path.isfile(self.position_file):
                with open(self.position_file, 'r', encoding='utf-8') as last_position:
                    last_line = last_position.readlines(
                    )[-1].strip().strip('"')
                if not last_line or last_line == 'null':
                    data = {"pagination": {
                        "hasNextPage": True, "endCursor": None}}
                else:
                    print(f"""
######################################
Last position: {last_line}
######################################
                    """)
                    last_line = last_line.strip().strip('"')
                    data = {"pagination": {"startCursor": last_line,
                                           "endCursor": last_line, "hasNextPage": True, 'hasPreviousPage': True}}
            else:
                if not os.path.exists(self.data_dir):
                    os.makedirs(self.data_dir)
                data = {"pagination": {"hasNextPage": True, "endCursor": None}}

            return data
        except Exception as e:
            self.logger.log(logging.WARNING, "Error while reading to file")
            self.logger.log(logging.ERROR, e)

    def position_write(self, after):
        try:
            if os.path.isfile(self.position_file):
                with open(self.position_file, 'r', encoding='utf-8') as position_file_check:
                    last_line = position_file_check.readlines(
                    )[-1].strip().strip('"')
                    if after != last_line:
                        with open(self.position_file, 'a', encoding='utf-8') as last_position:
                            if last_line != after:
                                json.dump(after, last_position)
                                last_position.write('\n')
            else:
                with open(self.position_file, 'w', encoding='utf-8') as last_position:
                    json.dump(after, last_position)
                    last_position.write('\n')
        except Exception as e:
            self.logger.log(logging.WARNING, "Error while reading to file")
            self.logger.log(logging.ERROR, e)

    def position_check(self, data):
        try:
            if os.path.exists(self.data_dir):
                file_list = glob.glob(
                    self.data_dir + '*_indicator-position.txt')
                file_list.sort(key=lambda x: os.path.getmtime(x))
                if len(file_list) > 1 and self.position_file != file_list[-1]:
                    if os.path.isfile(file_list[-1]):
                        print(f"""
######################################
Last File: {file_list[-1]}
######################################
                        """)
                        with open(file_list[-1], 'r', encoding='utf-8') as position_file_check:
                            lines = position_file_check.readlines()
                            for i, line in enumerate(lines):
                                last_line = line.strip().strip('"')
                                if last_line != "null":
                                    print(f"""
Last Position: {i+1} {last_line}
                                    """)
                                    return last_line
                elif len(file_list) == 1 and self.position_file != file_list[-1]:
                    if os.path.isfile(file_list[-1]):
                        print(f"""
######################################
Last File: {file_list[-1]}
######################################
                        """)
                        with open(file_list[-1], 'r', encoding='utf-8') as position_file_check:
                            lines = position_file_check.readlines()
                            for i, line in enumerate(lines):
                                last_line = line.strip().strip('"')
                                if last_line != "null":
                                    print(f"""
Last Position: {last_line}
                                    """)
                                    return last_line

                        while len(file_list) > 2:
                            oldest_file = file_list.pop(0)
                            print(oldest_file)
                            os.remove(oldest_file)
                        return last_line
                elif len(file_list) > 1 and self.position_file == file_list[-1]:
                    if os.path.isfile(file_list[-2]):
                        print(f"""
    ######################################
    Last File: {file_list[-2]}
    ######################################
                            """)
                        with open(file_list[-2], 'r', encoding='utf-8') as position_file_check:
                            lines = position_file_check.readlines()
                            for i, line in enumerate(lines):
                                last_line = line.strip().strip('"')
                                if last_line != "null":
                                    print(f"""
    Last Position: {i+1} {last_line}
                                        """)
                                    return last_line

            return 1
        except Exception as e:
            self.logger.log(logging.WARNING, "Error while reading to file")
            self.logger.log(logging.ERROR, e)
            return 1

    def data_write_raw_log(self, data):
        try:
            data = data['entities']
            # if os.path.isfile(self.data_raw_file):
            #    if not os.path.exists(self.data_dir):
            #        os.makedirs(self.data_dir)
            if os.path.isfile(self.data_raw_file):
                if not os.path.exists(self.data_dir):
                    os.makedirs(self.data_dir)
                with open(self.data_raw_file, 'a', encoding='utf-8') as last_data_raw:
                    for i in data:
                        last_data_raw.write(json.dumps(i) + '\n')
                        if i['entity_type'] == 'Indicator':
                            if i['x_opencti_main_observable_type'] == 'IPv4-Addr':
                                type = i['x_opencti_main_observable_type']
                                # value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + ',' + i['name'] + ',' + i['createdBy']['name'] + ',' + i['description']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + \
                                    i['x_opencti_main_observable_type'] + ',' + \
                                    i['name'] + ',' + i['createdBy']['name']
                                if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)
                            elif i['x_opencti_main_observable_type'] == 'IPv6-Addr':
                                type = i['x_opencti_main_observable_type']
                                # value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + ',' + i['name'] + ',' + i['createdBy']['name'] + ',' + i['description']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + \
                                    i['x_opencti_main_observable_type'] + ',' + \
                                    i['name'] + ',' + i['createdBy']['name']
                                if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)
                            elif i['x_opencti_main_observable_type'] == 'Domain-Name':
                                type = i['x_opencti_main_observable_type']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + \
                                        ',' + \
                                    i['name'] + ',' + i['createdBy']['name'] + \
                                    ',' + i['description']
                                if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)
                            else:
                                type = i['x_opencti_main_observable_type']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + \
                                    ',' + \
                                i['name'] + ',' + i['createdBy']['name']
                                if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)

                        elif i['entity_type'] == 'Malware':
                            value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + \
                                ',' + i['name'] + ',' + \
                                i['createdBy']['name'] + ',' + i['description']
                            if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)

            else:
                self.data_create_folder(self.data_raw_dir)
                with open(self.data_raw_file, 'w', encoding='utf-8') as last_data_raw:
                    for i in data:

                        last_data_raw.write(json.dumps(i) + '\n')

                        if i['entity_type'] == 'Indicator':
                            if i['x_opencti_main_observable_type'] == 'IPv4-Addr':
                                type = i['x_opencti_main_observable_type']
                                # value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + ',' + i['name'] + ',' + i['createdBy']['name'] + ',' + i['description']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + \
                                    i['x_opencti_main_observable_type'] + ',' + \
                                    i['name'] + ',' + i['createdBy']['name']
                                if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)
                            elif i['x_opencti_main_observable_type'] == 'Domain-Name':
                                type = i['x_opencti_main_observable_type']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + \
                                    ',' + \
                                i['name'] + ',' + i['createdBy']['name'] + \
                                ',' + i['description']
                                if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)
                            elif i['x_opencti_main_observable_type'] == 'IPv6-Addr':
                                type = i['x_opencti_main_observable_type']
                                # value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + ',' + i['name'] + ',' + i['createdBy']['name'] + ',' + i['description']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + \
                                    i['x_opencti_main_observable_type'] + ',' + \
                                    i['name'] + ',' + i['createdBy']['name']
                            else:
                                type = i['x_opencti_main_observable_type']
                                value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + \
                                    ',' + \
                                    i['name'] + ',' + i['createdBy']['name']
                                if not self.check_duplicate_datum(i['name'],type):
                                    self.data_write_IoC_log(value, type)

                        elif i['entity_type'] == 'Malware':
                            value = i['entity_type'] + ',' + i['created_at'] + ',' + i['x_opencti_main_observable_type'] + \
                                ',' + i['name'] + ',' + \
                                i['createdBy']['name'] + ',' + i['description']
                            if not self.check_duplicate_datum(i['name'],type):
                                self.data_write_IoC_log(value, type)
        except Exception as e:
            self.logger.log(logging.WARNING, "Error while writing to file")
            self.logger.log(logging.ERROR, e)

    def data_remove_file(self, data_file_path, count=5):
        try:
            file_list = glob.glob(self.data_dir + '*_indicator-position.txt')
            file_list.sort(key=lambda x: os.path.getmtime(x))
        except Exception as e:
            self.logger.log(logging.WARNING, "Error while removed to file")
            self.logger.log(logging.ERROR, e)

    def data_create_folder(self, foldername):
        try:
            if not os.path.exists(foldername):
                os.makedirs(foldername)
        except Exception as e:
            self.logger.log(logging.WARNING, "Error while removed to file")
            self.logger.log(logging.ERROR, e)

    def data_write_IoC_log(self, data, type):
        try:
            file = self.data_IoC_file + '_' + type + '.log'

            if os.path.isfile(file):
                if not os.path.exists(self.data_dir):
                    os.makedirs(self.data_dir)
                with open(file, 'a', encoding='utf-8') as last_data_raw:
                    last_data_raw.write(data)
                    last_data_raw.write('\n')
            else:
                self.data_create_folder(self.data_IoC_dir)
                with open(file, 'w', encoding='utf-8') as last_data_raw:
                    last_data_raw.write(data)
                    last_data_raw.write('\n')
        except Exception as e:
            self.logger.log(logging.WARNING, "Error while writing to file")
            self.logger.log(logging.ERROR, e)

    def exit_opencti(self):
        sys.exit()

    def check_duplicate_datum(self, datum, type):
        try:
            file = self.data_IoC_file + '_' + type + '.log'
            if os.path.isfile(file):
                with open(file, 'r') as f:
                    for line in f:
                        name = line.split(',')[3]
                        if datum ==  name:
                            print(f"Duplicate Type: {type} | Duplicate Datum : {datum}")
                            return True
                return False
        except FileNotFoundError:
            return False
