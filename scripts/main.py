#!/usr/bin/python
# -*- coding: utf8 -*-
import argparse
import csv
import logging
import os
import sys
import urlparse
from time import strftime, sleep
from config.config_log import GetConfig
from inmoscrape import InmoScrapers

# Debugging options
import ipdb
import traceback

GetConfig.config_log()

def info(type, value, tb):
    traceback.print_exception(type, value, tb)
    print
    ipdb.pm()

sys.excepthook = info


# exceptionObj
def displayException(ex):
    template = "An exception of type {0} occured. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    # logging.exception("Unexpected error: %s", message)
    return message
# End debugging options

##
methods = {}
methods["get_data_from_encuentra24"] = "get_data_from_encuentra24"
##

values_to_tuple = ""
for key in methods.keys():
    values_to_tuple = values_to_tuple + "'%s'," % key

available_methods = eval("%s" % values_to_tuple)

##
available_browsers = ("firefox", "phantomjs")
##

def inmoscrape():
    try:
        logging.info("Starting InmoScrape")

        # validating that the folder sites_csv has been already created
        SITES_CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sites_csv')
        SITES_CSV_DIR_ABS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites_csv')
        if not os.path.exists(SITES_CSV_DIR):
            logging.warning("Dir: '%s' does not exist, going to creat it\n\nPlease go to the dir: %s\nOpen the file 'sites.csv' (we have created the file for you), and bellow the word 'url' place the url where you want to start to get info\nThen try to start the app again", SITES_CSV_DIR, SITES_CSV_DIR_ABS)
            os.makedirs(SITES_CSV_DIR)
            sites_csv_file = open("%s/sites.csv" % SITES_CSV_DIR, "w")
            fieldnames = ["url"]
            writer = csv.DictWriter(sites_csv_file, fieldnames=fieldnames)
            writer.writeheader()
            sites_csv_file.close()
            return
        #

        # listing available sites_csv files
        values_to_tuple = ""
        for available_file in os.listdir(SITES_CSV_DIR):
            if available_file.endswith(".csv"):
                values_to_tuple = values_to_tuple + "'%s'," % available_file

        available_files = eval("%s" % values_to_tuple)
        ##

        parser = argparse.ArgumentParser(description='Wellcome to InmoScrape')
        parser.add_argument('-tm', '--test_method', action='store', choices=available_methods, dest='method_to_test', default="", help="Specifies the method that you want to test")
        # TODO evaluate if firefox can be by default
        parser.add_argument('-b', '--browser', action='store', dest='browser', choices=available_browsers, default="phantomjs", help="Specifies the browser that will be used by the app, by default it'll be used phantomjs")
        parser.add_argument('-f', '--file_name', action='store', dest='file_name', choices=available_files, default="sites.csv", help="Specifies the file that you've created and where you've placed the url site to get info, by default it'll be used the file: 'sites.csv'")
        parser.add_argument('-im', '--ignore_method', action='append', choices=available_methods, dest='methods_to_ignore', default=[], help="Specifies the methods that you want to skip")
        parser.add_argument('-ud', '--use_display', action='store', dest='use_display', choices=("on", "off",), default="off", help="Specifies if the bot will be use pyvirtualdisplay. By default it'll not be used")
        parser.add_argument('-sr', '--store_results_in_csv', action='store', dest='store_results_in_csv', choices=("on", "off",), default="on", help="Specifies if the bot will be saving the results in a csv file. By default it's setted as on")
        parser.add_argument('--version', action='version', version='InmoScrape V0.1', help="Display app version")
        arguments = parser.parse_args()

        # placing dict to config
        config = {}

        # getting browser
        browser = arguments.browser
        config["browser"] = browser

        if browser != "firefox" and arguments.use_display == "on":
            logging.error("You can use argument 'use_display' only when you select firefox as browser")
            return
        else:
            config["use_display"] = {}
            if arguments.use_display == "on":
                config["use_display"]["active"] = True
            else:
                config["use_display"]["active"] = False

        file_name = arguments.file_name
        if not os.path.isfile("%s/%s" % (SITES_CSV_DIR, file_name)):
            logging.error("File: '%s/%s' doesn't exist", SITES_CSV_DIR, file_name)
            return

        if not file_name.endswith("csv"):
            logging.error("File: '%s/%s' isn't an csv file", SITES_CSV_DIR, file_name)
            return

        base_resources = {
            "sites": [],
        }

        # reading csv to validate it
        logging.info("Going to read file: %s/%s", SITES_CSV_DIR, file_name)
        sites_csv_file = open("%s/%s" % (SITES_CSV_DIR, file_name), "r")
        csv_reader = csv.DictReader(sites_csv_file)

        for row in csv_reader:
            if "url" in row:
                # in a future this will be part of a separated method, by the moment wll be here
                if row["url"]:
                    up = urlparse.urlparse(row["url"])
                    if up.netloc == "www.encuentra24.com":
                        d_site_url = {
                            "url": row["url"],
                        }
                        base_resources["sites"].append(d_site_url)
                        # colocando este break para leer solo y una sola url de manera tal que se ejecute solo una, en caso de que se deseen leer mas de un mismo archivo, seimplemente eliminar el break
                        break
                    else:
                        logging.warning("URL not allowed: %s", row["url"])
                        return
                else:
                    logging.warning("File: '%s/%s' is empty \n\nPlease go to the dir: %s\nOpen the file '%s', and bellow the word 'url' ('url' should be the header) place the url where you want to start to get info\nThen try to start the app again", SITES_CSV_DIR, file_name, SITES_CSV_DIR_ABS, file_name)
                    return
            else:
                logging.error("File: '%s/%s' doesn't have 'url' column \n\nPlease go to the dir: %s\nOpen the file '%s', and you have to set as header the word 'url',then bellow of it, place the url where you want to start to get info\nThen try to start the app again", SITES_CSV_DIR, file_name, SITES_CSV_DIR_ABS, file_name)
                return

        # validating that base resources is not empty
        if len(base_resources["sites"]) <= 0:
            logging.warning("File: '%s/%s' is empty \n\nPlease go to the dir: %s\nOpen the file '%s', and bellow the word 'url' ('url' should be the header) place the url where you want to start to get info\nThen try to start the app again", SITES_CSV_DIR, file_name, SITES_CSV_DIR_ABS, file_name)
            return

        # config store_results_in_csv
        config["store_results_in_csv"] = {
                "store": False,
                "dir_to_store": "",
                "file_name": "",
        }

        if arguments.store_results_in_csv == "on":
            # setting dir to result
            dir_to_results = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results/%s" % (strftime("%Y%m%d")))
            dir_to_results_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results/%s" % (strftime("%Y%m%d")))
            if not os.path.exists(dir_to_results):
                logging.warning("Dir to results doesn't exist going to creat it, You'll find your results into dire:\n%s", dir_to_results_abs)
                os.makedirs(dir_to_results)

            config["store_results_in_csv"]["store"] = True
            config["store_results_in_csv"]["dir_to_store"] = dir_to_results_abs
            config["store_results_in_csv"]["filename"] = "results_%s.csv" % (strftime("%Y%m%d%H%M%S"))
            logging.info("ATTENTION Your results will be saved in:\n%s/%s", dir_to_results_abs, config["store_results_in_csv"]["filename"])

        # user data
        user_data = {}
        #

        results = {}
        if arguments.method_to_test:
            logging.info("Test mode has been seted as TRUE, only '%s' will be executed", arguments.method_to_test)
            results[arguments.method_to_test] = eval("InmoScrapers.%s(user_data, base_resources, config)" % methods[arguments.method_to_test])
            ipdb.set_trace()
        else:
            # by the url's content, we'll be executing corresponding method
            for site in base_resources["sites"]:
                if "encuentra24.com" in site["url"]:
                    logging.info("Starting to get info from encuentra24.com")
                    results["encuentra24"] = eval("InmoScrapers.get_data_from_encuentra24(user_data, base_resources, config)")
                else:
                    logging.error("Don't exist any method to sites with url: %s", site["url"])
                    return
    except Exception as ex:
        exception_message = displayException(ex)
        logging.exception("In the Method: inmoscrape\n%s", exception_message)
# END method inmoscrape

if __name__ == "__main__":
    inmoscrape()
