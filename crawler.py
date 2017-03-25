"""

If you run this program from the cmd, self.mainloop() will start.

You can run this from the cmd with:
$ crawler.py time
Crawler will then run and create a result in /results/ every "time" minutes.

TODO:
- add a progress bar to __get_all_articles()
- crop elements with status != ok out of the result

"""
import json
import os
import time

import requests
import fire


class Crawler:
    """
    this class provides an interface to the newsapi.org.
    you can use it to get all articles or to get the last search result of this class from file.

    important functions:
        - _get_all_articles()
        gets all articles and saves them into "./results". use with care!!

        - get_last_article_result()
        returns the last result from "./results" as list.

        - mainloop(minutes)
        starts a mainloop with sleep in minutes between crawls. created for use with fire.

    """

    def __init__(self):
        # creating paths
        self.__SEP = os.path.sep
        self.__BASE_PATH = os.path.abspath('.')
        self.__RESULTS_PATH = self.__BASE_PATH + self.__SEP + 'results'
        self.__RESULTS_ID_PATH = self.__RESULTS_PATH + self.__SEP + 'id'
        self.__API_KEY_PATH = self.__BASE_PATH + self.__SEP + 'api_key'
        # get API key from file
        self.__API_KEY = ''
        with open(self.__API_KEY_PATH, 'r') as fp:
            self.__API_KEY = fp.read()
            fp.close()
        # set base urls
        self.__ARTICLES_URL = 'https://newsapi.org/v1/articles'
        self.__SOURCES_URL = 'https://newsapi.org/v1/sources'
        # get sources
        self.__SOURCES = list()
        r = requests.get(self.__SOURCES_URL).text
        answer = json.loads(r)
        if answer['status'] != 'ok':
            raise ConnectionError
        for element in answer['sources']:
            self.__SOURCES.append(element)

    def get_sources(self):
        """ getter for resources available to the __CRAWLER.

        :return: all the sources available as list
        """
        result = list()
        for element in self.__SOURCES:
            result.append(element['name'])
        return result

    def _get_all_articles(self):
        """ makes an api-call and gets all articles from all sources.

        the result is saved at ./results/ID_result.json.
        the id is received from ./results/id via internal function. the function ensures, that no redundant ids are
        present.

        PLEASE USE WITH CARE!!
        the process takes some time and puts heavy load on the api. please don't use this too much. instead you can load
        the last result with self.get_last_article_result.

        :return: returns the __CRAWLER result as a list of dictionarys.
        """
        result = list()
        payload = dict(
            apiKey=self.__API_KEY
        )
        for element in self.__SOURCES:
            payload['source'] = element['id']
            r = requests.get(self.__ARTICLES_URL, payload).text
            r_json = json.loads(r)
            result.append(r_json)
            # wait two seconds to be kind to the api
            time.sleep(2)
        # m_id because only id would shadow internal python function
        m_id = self.__get_results_id()
        filename = m_id + '_result.json'
        filename_path = self.__RESULTS_PATH + self.__SEP + filename
        with open(filename_path, 'w') as fp:
            fp.write(json.dumps(result))
            fp.close()
        return result

    def get_last_article_result(self):
        """ loads the last result of "__get_all_articles()" from file.

        please use this instead of "__get_all_articles()" if you don't explicitly need up-to-date-data.
        the file to use is the current id - 1.

        :return: last article search result as list
        """
        m_id = self.__secret_get_last_results_id()
        filename = m_id + '_result.json'
        filename_path = self.__RESULTS_PATH + self.__SEP + filename
        with open(filename_path, 'r') as fp:
            result = json.loads(fp.read())
            fp.close()
        return result

    def __secret_get_last_results_id(self):
        """ returns the last used result id as a string. "secret" because this function only opens the file and does not
        change the id in there.

        :return: last used result id as string
        """
        # m_id because only id would shadow internal python function
        m_id = ''
        with open(self.__RESULTS_ID_PATH, 'r') as fp:
            m_id = int(fp.read()) - 1
            fp.close()
        return str(m_id)

    def __get_results_id(self):
        """ returns the file id for a search result to use.

        this function opens ./res/id and returns the id in there. to prevent redundant ids, this function will also
        increase the id by one and write it to the file.

        :return: id for result filename to be used.
        """
        # m_id because only id would shadow internal python function
        m_id = ''
        with open(self.__RESULTS_ID_PATH, 'r') as fp:
            m_id = int(fp.read())
            new_id = m_id + 1
            fp.close()
        with open(self.__RESULTS_ID_PATH, 'w') as fp:
            fp.write(str(new_id))
            fp.close()
        return str(m_id)

    def mainloop(self, minutes):
        print()
        print('Initializing Crawler...')
        crawler = Crawler()
        seconds = 60*int(minutes)
        print('Finished.')
        while True:
            print()
            print(50*'-')
            print('Starting to crawl...')
            crawler._get_all_articles()
            print('Crawling finished. Waiting for {0} minutes now...'.format(minutes))
            print(50*'-')
            time.sleep(seconds)

if __name__ == '__main__':
    crawler = Crawler()
    fire.Fire(crawler.mainloop)