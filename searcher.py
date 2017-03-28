"""

If you run this program from the cmd you can search for a keyword in the last crawler result.

You can run this from the cmd with:
$ searcher.py search keyword

The search result is printed in a cmd compatible version and saved to "./search_results/result.json".

TODO:
    - make use of some cool regex!
"""
import json
import os

import fire

from crawler import Crawler


class Searcher:
    """
    this class provides an interface to the crawlers last result.
    when initialized the self.data is synced with the latest crawler result in "./res/"
    and made searchable.

    important functions:
        - manual_search(keyword, safe=True)
        searches all articles titles for the given in keyword and returns them as list.

        - search(keyword)
        updates the current dataset and does a full search based on all users in self.users and the
        filters set there.

        - update()
        updates the internal dataset with the newest from "./crawler_results/".

    """

    def __init__(self):
        # setting paths
        self.__SEP = os.path.sep
        self.__BASE_PATH = os.path.abspath('.')
        self.__RESULTS_PATH = self.__BASE_PATH + self.__SEP + 'search_results'
        self.__USERS_PATH = self.__BASE_PATH + self.__SEP + 'users.json'
        # init __CRAWLER instance for getting the data
        self.__CRAWLER = Crawler()
        # get the data
        self.data = self.__CRAWLER.get_last_article_result()
        # get users
        with open(self.__USERS_PATH, 'r') as fp:
            self.__USERS = json.loads(fp.read())
            fp.close()

    def manual_search(self, keyword, save=True):
        """
        this function is for a search from the command line. Gets saved to
        "./search_results/manual_search_result.json" per default.
        $ searcher.py search keyword
        :param keyword: keyword to search for
        :param save: boolean; if set to true, result is saved to file.
        :return: result
        """
        self.update()
        # do the searching stuff

        keyword = str(keyword).lower()
        full_result = list()
        for source in self.data:
            for article in source['articles']:
                if article['description'] is not None:
                    if keyword in article['description'].lower() or keyword in article['title'].lower():
                        full_result.append(article)
                else:
                    if keyword in article['title'].lower():
                        full_result.append(article)
        # save result to file
        if save:
            filename = "manual_search_result.json"
            filename_path = self.__RESULTS_PATH + self.__SEP + filename
            with open(filename_path, "w") as fp:
                fp.write(json.dumps(full_result))
                fp.close()
            return full_result
        else:
            return full_result

    def search(self):
        """
        updates the current dataset and does a full search based on all users in self.users and the
        filters set there. the result is saved to "./search_results/result.json".
        :return: result-dictionary - [{"username" : "name",
                                    "results": ["filter":"filtername", "results":[list of articles]]]
        """
        self.update()
        result = []
        # iterate through each user and its filters
        for user in self.__USERS:
            tmp_result = dict(
                username=user['name'],
                results=list()
            )
            for filter in user['filters']:
                keyword = filter['keyword'].lower()
                filter_result = dict(
                    filter=keyword,
                    results=list()
                )
                # do the searching things
                for source in self.data:
                    for article in source['articles']:
                        if article['description'] is not None:
                            if keyword in article['description'].lower() or keyword in article['title'].lower():
                                # if result, write into the users tmp_result
                                filter_result['results'].append(article)
                        else:
                            if keyword in article['title'].lower():
                                filter_result['results'].append(article)
                if len(filter_result['results']) > 0:
                    tmp_result['results'].append(filter_result)
            result.append(tmp_result)
        # write the whole thing to disk
        filename = self.__RESULTS_PATH + self.__SEP + "result.json"
        with open(filename, 'w') as fp:
            fp.write(json.dumps(result))
            fp.close()
        return result

    def update(self):
        """ updates self.data with the newest file in "./crawler_results/"
        """
        self.data = self.__CRAWLER.get_last_article_result()


#####
# the following functions are only for providing cli via fire library.
#####

def fire_search(keyword):
    searcher = Searcher()
    result = searcher.manual_search(keyword, save=False)
    fire_print(result)


def fire_print(search_result):
    for element in search_result:
        print()
        print(50 * '-')
        for key in element.keys():
            print("{0}: {1}".format(key, element[key]))
        print(50 * '-')


if __name__ == '__main__':
    payload = dict(
        search=fire_search
    )
    fire.Fire(payload)