#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
import os
import requests
import random
import string
import zipfile
from pyvirtualdisplay import Display
from requests.exceptions import RequestException, HTTPError, Timeout, TooManyRedirects, ConnectionError
import unicodecsv

from splinter import Browser
from splinter.driver.webdriver.phantomjs import WebDriver as PhantomJSWebDriver
from time import sleep, strftime

# Debugging options
import sys
import ipdb
import traceback

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


class InmoScrapers:

    """
    Method to generate random string
    """
    @staticmethod
    def get_random_string():
        logging.info("Class InmoScrapers - method: get_random_string")
        min_len = 5
        max_len = 7
        options_to_choice = string.letters+string.digits
        random_string = ""
        random_string = random.choice(string.letters) + random_string.join([random.choice(options_to_choice) for i in range(random.randint(min_len, (max_len - 1)))])
        return random_string

    @staticmethod
    def get_browser(config={}):
        logging.info("Class InmoScrapers - method: get_browser")
        process_info = {}
        process_info["success"] = False
        process_info["message"] = ""
        process_info["result"] = {}

        if "main_info_source" in config:
            MAIN_INFO_SOURCE = config["main_info_source"]
        else:
            MAIN_INFO_SOURCE = ""

        try:
            # service args
            if not ("phantomjs_service_args" in config):
                phantomjs_service_args = [
                    '--ignore-ssl-errors=true',
                    '--ssl-protocol=tlsv1',
                    '--web-security=false',
                    # '--proxy=23.250.72.202:25599',
                    # '--proxy-auth=jbrewski85:y4aJetY4Y', #Optional
                    # '--proxy-type=http',
                ]
            else:
                phantomjs_service_args = config["phantomjs_service_args"]

            # browsers
            if not ("browser" in config):
                browser = Browser("phantomjs", service_args=phantomjs_service_args)
            else:
                if config["browser"] == "firefox":
                    if config["use_display"]["active"]:
                        # pyvirtualdisplay
                        display = Display(visible=0, size=(1280, 800))
                        display.start()
                        config["use_display"]["display"] = display
                        #
                    browser = Browser()
                elif config["browser"] == "phantomjs":
                    browser = Browser("phantomjs", service_args=phantomjs_service_args)
                else:
                    browser = Browser("phantomjs", service_args=phantomjs_service_args)

            browser.driver.set_window_size(1280, 800)
            ######

            process_info["success"] = True
            process_info["message"] = "[%s] Browser has been instanced" % (MAIN_INFO_SOURCE,)
            process_info["result"]["browser"] = browser
            process_info["result"]["config"] = config
            return process_info

        except Exception as ex:
            exception_message = displayException(ex)
            logging.exception("[%s]At the moment to set up browser settings\n%s", MAIN_INFO_SOURCE, exception_message)
            process_info["message"] = "[%s]At the moment to set up browser settings\n%s" % (MAIN_INFO_SOURCE, exception_message)
            return process_info

    @staticmethod
    def stop_display(config, display):
        logging.info("Class InmoScrapers - Method: stop_display")
        try:
            display.stop()
        except Exception as ex:
            displayException(ex)
            logging.exception("When stoping the display")

    @staticmethod
    def close_browser(config, browser):
        logging.info("Class InmoScrapers - Method: close_browser")
        try:
            browser.quit()
            if "use_display" in config:
                if config["use_display"]["active"]:
                    InmoScrapers.stop_display(config, config["use_display"]["display"])
        except Exception as ex:
            displayException(ex)
            logging.exception("When closing the browser")

    @staticmethod
    def validate_config(config):
        logging.info("Class InmoScrapers - Method: validate_config")
        process_info = {}
        process_info["success"] = False
        process_info["message"] = ""
        process_info["errors"] = {}
        process_info["result"] = {}

        if config:
            if "main_info_source" in config:
                MAIN_INFO_SOURCE = config["main_info_source"]
            else:
                MAIN_INFO_SOURCE = ""

            if "browser" in config:
                if config["browser"] in ["chrome", "firefox", "phantomjs"]:
                    logging.info("[%s]Argument browser: '%s' is correct", MAIN_INFO_SOURCE, config["browser"])
                else:
                    logging.error("[%s]Wrong value '%s' to argument 'browser', please check it", MAIN_INFO_SOURCE, config["browser"])
                    process_info["message"] = "[%s]Wrong value '%s' to argument'browser', please check it" % (MAIN_INFO_SOURCE, config["browser"])
                    return process_info
            else:
                config["browser"] = "phantomjs"

            if "use_display" in config:
                if isinstance(config["use_display"], dict):
                    if "active" in config["use_display"]:
                        if isinstance(config["use_display"]["active"], bool):
                            if config["use_display"]["active"]:
                                logging.info("[%s]Pyvirtualdisplay will be used if your browser is firefox", MAIN_INFO_SOURCE)
                            else:
                                logging.info("[%s]Pyvirtualdisplay will not be used if your browser is firefox", MAIN_INFO_SOURCE)
                        else:
                            logging.error("[%s]Unknown instance to: 'config[\"use_display\"][\"active\"]'. It should be a bool value", MAIN_INFO_SOURCE)
                            process_info["message"] = "[%s]Unknown instance to: 'config[\"use_display\"][\"active\"]'. It should be a bool value" % (MAIN_INFO_SOURCE)
                            return process_info
                    else:
                        config["use_display"]["active"] = False
                else:
                    logging.error("[%s]Unknown instance to: 'config[\"use_display\"]'. It should be a dict", MAIN_INFO_SOURCE)
                    process_info["message"] = "[%s]Unknown instance to: 'config[\"use_display\"]'. It should be a dict" % (MAIN_INFO_SOURCE,)
                    return process_info
            else:
                config["use_display"] = {
                    "active": False
                }

            if "store_results_in_csv" in config:
                if "store" in config["store_results_in_csv"]:
                    if isinstance(config["store_results_in_csv"]["store"], bool):
                        if config["store_results_in_csv"]["store"]:
                            logging.info("[%s]Argument 'store_results_in_csv' has been setted as True, resuls will be saved in a csv file. Going to check results dir", MAIN_INFO_SOURCE)
                            if "dir_to_store" in config["store_results_in_csv"]:
                                # esta colocado, validar que sea un directorio valido
                                if os.path.exists(config["store_results_in_csv"]["dir_to_store"]):
                                    if os.path.isdir(config["store_results_in_csv"]["dir_to_store"]):
                                        logging.info("[%s]Argument config[\"store_results_in_csv\"][\"dir_to_store\"]' is correct", MAIN_INFO_SOURCE)
                                        if not ("filename" in config["store_results_in_csv"]):
                                            config["store_results_in_csv"]["filename"] = "results_%s.csv" % (strftime("%Y%m%d%H%M%S"))
                                    else:
                                        logging.error("[%s]Dir setted in argument: config[\"store_results_in_csv\"][\"dir_to_store\"]' doesn't exist. Please make sure that dir exist and try again", MAIN_INFO_SOURCE)
                                        process_info["message"] = "[%s]Dir setted in argument: config[\"store_results_in_csv\"][\"dir_to_store\"]' doesn't exist. Please make sure that dir exist and try again" % (MAIN_INFO_SOURCE)
                                        return process_info
                                else:
                                    logging.error("[%s]Dir setted in argument: config[\"store_results_in_csv\"][\"dir_to_store\"]' doesn't exist. Please make sure that dir exist and try again", MAIN_INFO_SOURCE)
                                    process_info["message"] = "[%s]Dir setted in argument: config[\"store_results_in_csv\"][\"dir_to_store\"]' doesn't exist. Please make sure that dir exist and try again" % (MAIN_INFO_SOURCE)
                                    return process_info
                            else:
                                logging.error("[%s]Argument 'dir_to_store' hasn't been setted, please make sure that you are setting an argument: config[\"store_results_in_csv\"][\"dir_to_store\"]' with a absolute path to an existing dir", MAIN_INFO_SOURCE)
                                process_info["message"] = "[%s]Argument 'dir_to_store' hasn't been setted, please make sure that you are setting an argument: config[\"store_results_in_csv\"][\"dir_to_store\"]' with a absolute path to an existing dir" % (MAIN_INFO_SOURCE)
                                return process_info
                        else:
                            logging.info("[%s]Argument 'store_results_in_csv' has been setted as False, resuls wont be saved in a csv file", MAIN_INFO_SOURCE)
                            config["store_results_in_csv"]["dir_to_store"] = ""
                    else:
                        logging.error("[%s]Unknown instance to: 'config[\"store_results_in_csv\"][\"store\"]'. It should be a bool value", MAIN_INFO_SOURCE)
                        process_info["message"] = "[%s]Unknown instance to: 'config[\"store_results_in_csv\"][\"store\"]'. It should be a bool value" % (MAIN_INFO_SOURCE)
                        return process_info
                else:
                    config["store_results_in_csv"] = {
                        "store": False,
                        "dir_to_store": "",
                        "filename": "",
                    }
            else:
                config["store_results_in_csv"] = {
                    "store": False,
                    "dir_to_store": "",
                    "filename": "",
                }
        else:
            config = {
                "browser": "phantomjs",
                "use_display": {
                    "active": False,
                },
                "store_results_in_csv": {
                    "store": False,
                    "dir_to_store": "",
                    "filename": "",
                },
            }

        process_info["success"] = True
        process_info["message"] = "Config has been validated successfully "
        process_info["result"]["config"] = config
        return process_info
    # END

    @staticmethod
    def validate_base_resources_validators(config, base_resources, validators=[]):
        logging.info("Class InmoScrapers - Method: validate_base_resources_validators")
        process_info = {
            "success": False,
            "message": "",
            "result": {},
        }

        if "main_info_source" in config:
            MAIN_INFO_SOURCE = config["main_info_source"]
        else:
            MAIN_INFO_SOURCE = ""

        if not (validators):
            validators = ["sites"]

        validation_success = True
        if isinstance(base_resources, dict):
            for validator in validators:
                if validator == "sites":
                    if (validator in base_resources):
                        if isinstance(base_resources[validator], list):
                            if (len(base_resources[validator]) > 0):
                                logging.info("[%s]Argument base_resources[\"%s\"]' is correct", MAIN_INFO_SOURCE, validator)
                                process_info["message"] = process_info["message"] + "\n[%s]Argument base_resources[\"%s\"]' is correct" % (MAIN_INFO_SOURCE, validator)
                            else:
                                logging.error("[%s]Argument 'base_resources[\"%s\"]' is empty, please check it", MAIN_INFO_SOURCE, validator)
                                process_info["message"] = process_info["message"] + "\n[%s]Argument 'base_resources[\"%s\"]' is empty, please check it" % (MAIN_INFO_SOURCE, validator)
                                validation_success = False
                                break
                        else:
                            logging.error("[%s]Unknown instance to argument 'base_resources[\"%s\"]'. It should be of <type 'list'>", MAIN_INFO_SOURCE, validator)
                            process_info["message"] = process_info["message"] + "\n[%s]Unknown instance to argument 'base_resources[\"%s\"]'. It should be of <type 'list'>" % (MAIN_INFO_SOURCE, validator)
                            validation_success = False
                            break
                    else:
                        logging.error("[%s]Dict 'base resources' is malformed, it has to have a least one key: %s <type 'list'>", MAIN_INFO_SOURCE, validator)
                        process_info["message"] = process_info["message"] + "\n[%s]Dict 'base resources' is malformed, it has to have a least one key: %s <type 'list'>" % (MAIN_INFO_SOURCE, validator)
                        validation_success = False
                        break
                else:
                    logging.error("[%s]Unknown validator '%s' to the method 'validate_base_resources_validators'", MAIN_INFO_SOURCE, validator)
                    process_info["message"] = process_info["message"] + "[%s]Unknown validator '%s' to the method 'validate_base_resources_validators'" % (MAIN_INFO_SOURCE, validator)
                    validation_success = False
                    break
            # END for validators

            if validation_success:
                logging.info("[%s] Dict base resources has been validated successfully", MAIN_INFO_SOURCE)
                process_info["message"] = process_info["message"] + "\n[%s] Dict base resources has been validated successfully" % (MAIN_INFO_SOURCE)
                process_info["success"] = True

            return process_info
        else:
            logging.error("[%s]Unknown instance to argument 'base_resources'. It should be a dict value", MAIN_INFO_SOURCE)
            process_info["message"] = "[%s]Unknown instance to argument 'base_resources'. It should be a dict value" % (MAIN_INFO_SOURCE,)
            return process_info
    # END

    @staticmethod
    def validate_user_data(config, user_data):
        logging.info("Class InmoScrapers - Method: validate_user_data")
        process_info = {
            "success": False,
            "message": "",
            "result": {},
        }

        if "main_info_source" in config:
            MAIN_INFO_SOURCE = config["main_info_source"]
        else:
            MAIN_INFO_SOURCE = ""

        return process_info

    """
    This method recevies a specific broweser instance where you want to extract the info
    """
    @staticmethod
    def scraping_data_from_specific_encuentra24_ad(browser, config, first_ad=False):
        logging.info("Class InmoScrapers - method: scraping_data_from_specific_encuentra24_ad")
        process_info = {
            "success": False,
            "message": "",
            "result": {}
        }
        if "main_info_source" in config:
            MAIN_INFO_SOURCE = config["main_info_source"]
        else:
            MAIN_INFO_SOURCE = "encuentra24"
            config["main_info_source"] = MAIN_INFO_SOURCE

        if browser is None:
            logging.error("[%s]Browser is not instanced", MAIN_INFO_SOURCE)
            process_info["message"] = process_info["message"] + "\n[%s]Browser is not instanced" % (MAIN_INFO_SOURCE)
            return process_info

        d_ad_info = {
            "ad_id": "",
            "ad_title": "",
            "ad_url": "",
            "ad_offer_price": "",
            "ad_photo": "",
            "ad_info_list": [],
            "ad_info_str": "",
            "ad_details_list": [],
            "ad_details_str": "",
            "ad_product_features_list": [],
            "ad_product_features_str": "",
            "ad_contact_info_username": "",
            "ad_contact_info_attrs_list": [],
            "ad_contact_info_attrs_str": "",
            "ad_contact_info_phone": "",
            "ad_contact_info_cellphone": "",
        }
        # ad id xpath
        ad_id_xpath = "//span[@class = 'ad-id']"

        # ads title xpath
        ad_title_xpath = "//h1[@class = 'product-title']"

        try:
            logging.info("[%s]Getting data from: %s", MAIN_INFO_SOURCE, browser.url)

            counter_element_xpath = "//ul[@class = 'pager']/li[@class = 'hidden-xs hidden-sm']"
            if browser.is_element_present_by_xpath(counter_element_xpath):
                if browser.find_by_xpath(counter_element_xpath).last.text:
                    logging.info("[%s] %s", MAIN_INFO_SOURCE, browser.find_by_xpath(counter_element_xpath).last.text)

            # ad id
            if browser.is_element_present_by_xpath(ad_id_xpath):
                if browser.find_by_xpath(ad_id_xpath).value:
                    d_ad_info["ad_id"] = browser.find_by_xpath(ad_id_xpath).value

            # ad title
            if browser.is_element_present_by_xpath(ad_title_xpath):
                if browser.find_by_xpath(ad_title_xpath).value:
                    d_ad_info["ad_title"] = browser.find_by_xpath(ad_title_xpath).value.replace(";", " ").replace("|", " ")

            # ad url
            d_ad_info["ad_url"] = browser.url

            # ad offer price
            ad_offer_price_xpath = "//div[@class = 'offer-price']"
            if browser.is_element_present_by_xpath(ad_offer_price_xpath):
                if browser.find_by_xpath(ad_offer_price_xpath).text:
                    d_ad_info["ad_offer_price"] = browser.find_by_xpath(ad_offer_price_xpath).text.replace(";", " ")

            # ad photo
            ad_photo_xpath = "//div[@id = 'tabPhotos']/descendant::div[contains(@class, 'slick-current slick-active')]/a/img"
            if browser.is_element_present_by_xpath(ad_photo_xpath):
                if browser.find_by_xpath(ad_photo_xpath)["src"]:
                    d_ad_info["ad_photo"] = browser.find_by_xpath(ad_photo_xpath)["src"]

            # general info to the ad
            ad_info_xpath = "//div[@class = 'ad-info']/div/div/div/ul/li"
            ad_info_list = []
            if browser.is_element_present_by_xpath(ad_info_xpath):
                for i in range(0, len(browser.find_by_xpath(ad_info_xpath))):
                    ad_info_str = ""
                    ad_specific_infoname_xpath = "%s[%d]/span[@class = 'info-name']" % (ad_info_xpath, (i + 1))
                    ad_specific_infovalue_xpath = "%s[%d]/span[@class = 'info-value']" % (ad_info_xpath, (i + 1))
                    if browser.is_element_present_by_xpath(ad_specific_infoname_xpath):
                        ad_info_str = ad_info_str + browser.find_by_xpath(ad_specific_infoname_xpath).text.replace(";", " ")

                    if browser.is_element_present_by_xpath(ad_specific_infovalue_xpath):
                        ad_info_str = ad_info_str + " " + browser.find_by_xpath(ad_specific_infovalue_xpath).text.replace(";", " ")

                    ad_info_list.append(ad_info_str)
                # end for i in range
            # end if

            # parsing ad info list to a str
            if len(ad_info_list) > 0:
                d_ad_info["ad_info_str"] = "|".join(ad_info_list)
                d_ad_info["ad_info_list"] = ad_info_list

            # details to the add
            ad_details_xpath = "//div[@class = 'ad-details']/div/div/div/ul/li"
            ad_details_list = []
            if browser.is_element_present_by_xpath(ad_details_xpath):
                for i in range(0, len(browser.find_by_xpath(ad_details_xpath))):
                    ad_detail_str = ""
                    ad_specific_infoname_xpath = "%s[%d]/span[@class = 'info-name']" % (ad_details_xpath, (i + 1))
                    ad_specific_infovalue_xpath = "%s[%d]/span[@class = 'info-value']" % (ad_details_xpath, (i + 1))
                    if browser.is_element_present_by_xpath(ad_specific_infoname_xpath):
                        ad_detail_str = ad_detail_str + browser.find_by_xpath(ad_specific_infoname_xpath).text.replace(";", " ")

                    if browser.is_element_present_by_xpath(ad_specific_infovalue_xpath):
                        ad_detail_str = ad_detail_str + " " + browser.find_by_xpath(ad_specific_infovalue_xpath).text.replace(";", " ")

                    ad_details_list.append(ad_detail_str)
                # end for i in range
            # end if

            # parsing ad details list to a str
            if len(ad_details_list) > 0:
                d_ad_info["ad_details_str"] = "|".join(ad_details_list)
                d_ad_info["ad_details_list"] = ad_details_list

            # ad product features
            ad_product_features_xpath = "//ul[@class = 'product-features']/li"
            ad_product_features_list = []
            if browser.is_element_present_by_xpath(ad_product_features_xpath):
                for ad_product_feature in browser.find_by_xpath(ad_product_features_xpath):
                    if ad_product_feature.text:
                        ad_product_features_list.append(ad_product_feature.text.replace(";", " "))
                # end for
            # end if

            # parsing ad product features list to a str
            if len(ad_product_features_list) > 0:
                d_ad_info["ad_product_features_str"] = "|".join(ad_product_features_list)
                d_ad_info["ad_product_features_list"] = ad_product_features_list

            # ad contact info
            # ad contact info username
            ad_contact_info_username_xpath = "//div[@class = 'user-info']/span[@class = 'user-name']"
            if browser.is_element_present_by_xpath(ad_contact_info_username_xpath):
                if browser.find_by_xpath(ad_contact_info_username_xpath).text:
                    d_ad_info["ad_contact_info_username"] = browser.find_by_xpath(ad_contact_info_username_xpath).text.replace(";", " ")

            # ad contact info attrs
            ad_contact_info_attrs_xpath = "//div[@class = 'user-info']/span[@class = 'text-attr']"
            ad_contact_info_attrs_list = []
            if browser.is_element_present_by_xpath(ad_contact_info_attrs_xpath):
                for ad_contact_info_attr in browser.find_by_xpath(ad_contact_info_attrs_xpath):
                    ad_contact_info_attrs_list.append(ad_contact_info_attr.text.replace(";", " "))

            # parsing ad contact info attrs list to a str
            if len(ad_contact_info_attrs_list) > 0:
                d_ad_info["ad_contact_info_attrs_str"] = "|".join(ad_contact_info_attrs_list)
                d_ad_info["ad_contact_info_attrs_list"] = ad_contact_info_attrs_list

            # ad contact info phone
            ad_contact_info_phone_xpath = "//div[@class = 'contact-phone']/span[@class = 'phone icon icon-call']"
            if browser.is_element_present_by_xpath(ad_contact_info_phone_xpath):
                if browser.find_by_xpath(ad_contact_info_phone_xpath).text:
                    d_ad_info["ad_contact_info_phone"] = browser.find_by_xpath(ad_contact_info_phone_xpath).text.split("\n")[0]

            # ad contact info cellphone
            ad_contact_info_cellphone_xpath = "//div[@class = 'contact-phone']/span[@class = 'cellphone icon icon-call-mobile']"
            if browser.is_element_present_by_xpath(ad_contact_info_cellphone_xpath):
                if browser.find_by_xpath(ad_contact_info_cellphone_xpath).text:
                    d_ad_info["ad_contact_info_cellphone"] = browser.find_by_xpath(ad_contact_info_cellphone_xpath).text.split("\n")[0]

            ################
            if config["store_results_in_csv"]["store"]:
                fieldnames = [
                    "ad_id",
                    "ad_title",
                    "ad_url",
                    "ad_offer_price",
                    "ad_photo",
                    "ad_info_str",
                    "ad_details_str",
                    "ad_product_features_str",
                    "ad_contact_info_username",
                    "ad_contact_info_attrs_str",
                    "ad_contact_info_phone",
                    "ad_contact_info_cellphone",
                ]

                fields_to_save = {
                    "ad_id": d_ad_info["ad_id"],
                    "ad_title": d_ad_info["ad_title"],
                    "ad_url": d_ad_info["ad_url"],
                    "ad_offer_price": d_ad_info["ad_offer_price"],
                    "ad_photo": d_ad_info["ad_photo"],
                    "ad_info_str": d_ad_info["ad_info_str"],
                    "ad_details_str": d_ad_info["ad_details_str"],
                    "ad_product_features_str": d_ad_info["ad_product_features_str"],
                    "ad_contact_info_username": d_ad_info["ad_contact_info_username"],
                    "ad_contact_info_attrs_str": d_ad_info["ad_contact_info_attrs_str"],
                    "ad_contact_info_phone": d_ad_info["ad_contact_info_phone"],
                    "ad_contact_info_cellphone": d_ad_info["ad_contact_info_cellphone"],
                }

                try:
                    file_csv = open("%s/%s" % (config["store_results_in_csv"]["dir_to_store"], config["store_results_in_csv"]["filename"]), "a+")
                    csv_dictwriter = unicodecsv.DictWriter(file_csv, fieldnames=fieldnames, encoding='utf-8-sig', delimiter=";")

                    if first_ad:
                        csv_dictwriter.writeheader()

                    csv_dictwriter.writerow(fields_to_save)
                    logging.info("[%s]Info to ad: %s has been wrote successfully in csv file", MAIN_INFO_SOURCE, d_ad_info["ad_id"])
                except Exception as ex:
                    exception_message = displayException(ex)
                    logging.exception("[%s]An exception has occurred at the moment to write in csv file to the ad:\n\tAD Id.: %s\n\tAd URL: %s\n%s", MAIN_INFO_SOURCE, d_ad_info["ad_id"], d_ad_info["ad_url"], displayException)
                    process_info["message"] = process_info["message"] + "\n[%s]An exception has occurred at the moment to write in csv file to the ad:\n\tAD Id.: %s\n\tAd URL: %s\n%s" % (MAIN_INFO_SOURCE, d_ad_info["ad_id"], d_ad_info["ad_url"], displayException)
            # end if config["store_results_in_csv"]["store"]
        except Exception as ex:
            exception_message = displayException(ex)
            logging.exception("[%s]An exception has occurred getting info from the ad with url: %s\n%s", MAIN_INFO_SOURCE, browser.url, exception_message)
            process_info["message"] = process_info["message"] + "\n[%s]An exception has occurred getting info from the ad with url: %s\n%s" % (MAIN_INFO_SOURCE, browser.url, displayException)

        #################
        process_info["success"] = True
        logging.info("Process to extract info to the ad has been finished, please check your results")
        process_info["message"] = process_info["message"] + "\nProcess to extract info to the ad has been finished, please check your results"
        process_info["result"] = d_ad_info
        return process_info
        #################
    # END

    @staticmethod
    def get_data_from_encuentra24(user_data, base_resources, config):
        logging.info("Class InmoScrapers - method: get_data_from_encuentra24")

        process_info = {
            "success": False,
            "message": "",
            "result": {}
        }

        if "main_info_source" in config:
            MAIN_INFO_SOURCE = config["main_info_source"]
        else:
            MAIN_INFO_SOURCE = "encuentra24"
            config["main_info_source"] = MAIN_INFO_SOURCE

        validate_config = InmoScrapers.validate_config(config)
        if validate_config["success"]:
            config = validate_config["result"]["config"]
            logging.info("%s", validate_config["message"])
        else:
            logging.error("%s", validate_config["message"])
            process_info["message"] = validate_config["message"]
            return process_info

        validate_base_resources = InmoScrapers.validate_base_resources_validators(config, base_resources, validators=["sites", ])
        if not validate_base_resources["success"]:
            logging.error("%s", validate_base_resources["message"])
            process_info["message"] = validate_base_resources["message"]
            return process_info

        browser_results = InmoScrapers.get_browser(config)
        if browser_results["success"]:
            browser = browser_results["result"]["browser"]
            config = browser_results["result"]["config"]
        else:
            logging.error("%s", browser_results["message"])
            process_info["message"] = browser_results["message"]
            return process_info

        ads_results = []
        for site in base_resources["sites"]:
            """
            d_site_result = {
                "success": False,
                "message": "",
                "result": [],
            }
            """
            try:
                browser.visit(site["url"])

                # validating if the main url is a list or a specific ad
                list_view_toggle_id = "listViewToggle"
                gallery_view_toggle_id = "galleryViewToggle"

                # ad id xpath
                ad_id_xpath = "//span[@class = 'ad-id']"

                # ads title xpath
                ad_title_xpath = "//h1[@class = 'product-title']"

                if browser.is_element_present_by_id(list_view_toggle_id, 1) or browser.is_element_present_by_id(gallery_view_toggle_id, 1):
                    logging.info("[%s]Starting from a list, going to extract the first element", MAIN_INFO_SOURCE)

                    list_elements_xpath = "//div[@id = 'listingview']/div/article/div[@class = 'ann-box-details']/a"
                    if not browser.is_element_present_by_xpath(list_elements_xpath):
                        logging.error("[%s]List elements haven't been detected, maybe the list supplied is empty, please check and try again", MAIN_INFO_SOURCE)
                        process_info["message"] = process_info["message"] + "\n[%s]List elements haven't been detected, maybe the list supplied is empty, please check and try again" % (MAIN_INFO_SOURCE)
                        return process_info

                    first_ad_link = browser.find_by_xpath(list_elements_xpath)[0]["href"]
                    if not first_ad_link:
                        logging.error("[%s]Link to the first element to the list is empty, please check it and try again", MAIN_INFO_SOURCE)
                        process_info["message"] = process_info["message"] + "\n[%s]Link to the first element to the list is empty, please check it and try again" % (MAIN_INFO_SOURCE)
                        return process_info

                    browser.visit(first_ad_link)
                elif browser.is_element_present_by_xpath(ad_id_xpath) or browser.is_element_present_by_xpath(ad_title_xpath):
                    logging.info("[%s]Starting from a specific ad, going to extract its info", MAIN_INFO_SOURCE)
                else:
                    logging.error("[%s]Elements to check if supplied url is a list or a specific post haven't been detected, please check url supplied and make sure that is a correct url\nURL: %s", MAIN_INFO_SOURCE, site["url"])
                    process_info["message"] = process_info["message"] + "\n[%s]Elements to check if supplied url is a list or a specific post haven't been detected, please check url supplied and make sure that is a correct url\nURL: %s" % (MAIN_INFO_SOURCE, site["url"])
                    return process_info

                # to check if exists more ads
                exists_more_ads = False

                # to allow execute the bucle to the first element
                first_ad = True

                # possible ideas: set a config to get an specific ammount of ads
                while(first_ad or exists_more_ads):
                    process_ad_result = InmoScrapers.scraping_data_from_specific_encuentra24_ad(browser, config, first_ad)

                    if not process_ad_result["success"]:
                        logging.error("%s", process_ad_result["message"])
                        process_info = process_info + "\n%s" % process_ad_result["message"]
                        return process_info

                    ads_results.append(process_ad_result["result"])

                    ###########################
                    first_ad = False
                    # next ads
                    next_ad_xpath = "//ul[@class = 'pager']/li/a[@class = 'next']"

                    if not browser.is_element_present_by_xpath(next_ad_xpath):
                        logging.info("[%s]No elements could be found to check if exists or not more ads. Going to check if exist more elements with list alternative method", MAIN_INFO_SOURCE)
                        exists_more_ads = False
                        continue

                    next_ad_link = browser.find_by_xpath(next_ad_xpath)["href"]
                    if not next_ad_link:
                        logging.info("[%s]Link to next site is empty, doesn't exist more ads. Going to check if exist more elements with list alternative method", MAIN_INFO_SOURCE)
                        exists_more_ads = False
                        continue

                    exists_more_ads = True
                    sleep(2)
                    browser.visit(next_ad_link)
                    #############################
                # END while

                # finding element to go back to the list
                list_element_xpath = "//ul[@class = 'pager']/li/a[@class = 'prev']"
                if not browser.is_element_present_by_xpath(list_element_xpath):
                    logging.info("[%s]No elements could be found to check if exists or not more ads. Doesn't exist more ads (alternative to check by the list)", MAIN_INFO_SOURCE)
                    continue

                list_element_link = browser.find_by_xpath(list_element_xpath).first["href"]
                if not list_element_link:
                    logging.info("[%s]Link to list page is empty, maybe doesn't exist more ads (alternative to check by the list)", MAIN_INFO_SOURCE)
                    continue

                if not "#page=100" in list_element_link:
                    browser.visit(list_element_link + "#page=100")
                else:
                    browser.visit(list_element_link)

                sleep(10)
                next_button_xpath = "//ul[@class = 'pagination']/li[@class = 'arrow']/a[@title = 'Continuar']"
                if not browser.is_element_present_by_xpath(next_button_xpath):
                    logging.info("[%s]Hasn't been found button to the next page of results. Doesn't exist more results", MAIN_INFO_SOURCE)
                    continue

                next_button_link = browser.find_by_xpath(next_button_xpath)["href"]
                logging.info("[%s]URL to next page: %s", MAIN_INFO_SOURCE, next_button_link)
                if not next_button_link:
                    logging.info("[%s]Link to the next page of results is empty. Doesn't exist more results", MAIN_INFO_SOURCE)
                    continue

                browser.visit(next_button_link)
                sleep(5)
                browser.reload()
                sleep(5)

                exists_more_ads = True

                while exists_more_ads:
                    origin_list_url = browser.url
                    ads_url_list = []

                    ad_list_elements_xpath = "//div[@id = 'listingview']/div/article/div[@class = 'ann-box-details']/a"
                    if not browser.is_element_present_by_xpath(ad_list_elements_xpath):
                        logging.error("[%s]Ad elements haven't been detected in the list, maybe the list is empty and doesn't exist mored ads", MAIN_INFO_SOURCE)
                        process_info["message"] = process_info["message"] + "\n[%s]Ad elements haven't been detected in the list, maybe the list is empty and doesn't exist mored ads" % (MAIN_INFO_SOURCE)
                        exists_more_ads = False
                        continue

                    # getting all ads url from the list
                    for ad_list_element in browser.find_by_xpath(ad_list_elements_xpath):
                        if ad_list_element["href"]:
                            ads_url_list.append(ad_list_element["href"])

                    # going to each element in the list
                    for ad_url in ads_url_list:
                        browser.visit(ad_url)
                        process_ad_result = InmoScrapers.scraping_data_from_specific_encuentra24_ad(browser, config, first_ad)
                        if not process_ad_result["success"]:
                            logging.error("%s", process_ad_result["message"])
                            process_info = process_info + "\n%s" % process_ad_result["message"]
                            return process_info

                        ads_results.append(process_ad_result["result"])
                    # END for ad_url in ads_url_list

                    # going back to origin list to cheack if exist more list
                    logging.info("[%s]Returning to: %s", MAIN_INFO_SOURCE, origin_list_url)
                    browser.visit(origin_list_url)

                    sleep(10)
                    # checking for more lists
                    next_button_xpath = "//ul[@class = 'pagination']/li[@class = 'arrow']/a[@title = 'Continuar']"
                    if not browser.is_element_present_by_xpath(next_button_xpath):
                        logging.info("[%s]Hasn't been found button to the next page of results. Doesn't exist more results", MAIN_INFO_SOURCE)
                        exists_more_ads = False
                        continue

                    next_button_link = browser.find_by_xpath(next_button_xpath)["href"]
                    logging.info("[%s]URL to next page: %s", MAIN_INFO_SOURCE, next_button_link)
                    if not next_button_link:
                        logging.info("[%s]Link to the next page of results is empty. Doesn't exist more results", MAIN_INFO_SOURCE)
                        exists_more_ads = False
                        continue

                    browser.visit(next_button_link)
                    sleep(5)
                    browser.reload()
                    sleep(5)
                # END while
            except Exception as ex:
                exception_message = displayException(ex)
                logging.exception("[%s]An exception has ocurred in the method 'get_data_from_encuentra24'\n%s", MAIN_INFO_SOURCE, exception_message)
                process_info["message"] = process_info["message"] + "\n[%s]An exception has ocurred in the method 'get_data_from_encuentra24'\n%s" % (MAIN_INFO_SOURCE, exception_message)
        # END for site in base_resources["sites"]

        # closing browser
        InmoScrapers.close_browser(config, browser)

        #################
        process_info["success"] = True
        logging.info("Process to extract info from %s has been finished, please check your results",  MAIN_INFO_SOURCE)
        process_info["message"] = process_info["message"] + "\nProcess to extract info from %s has been finished, please check your results" % MAIN_INFO_SOURCE
        process_info["result"] = ads_results
        return process_info
        #################
    # END method get_data_from_encuentra24

# END class InmoScrapers
