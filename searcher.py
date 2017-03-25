"""

If you run this program from the cmd you can search for a keyword in the last crawler result.

You can run this from the cmd with:
$ searcher.py search_titles keyword
$ searcher.py search_descriptions keyword
$ searcher.py search_full keyword

The search result is printed in a cmd compatible version. If you use this as class, data looks different.


TODO:
    - make use of some cool regex!
"""
import fire

from crawler import Crawler


class Searcher:
    """
    this class provides an interface to the crawlers last result.
    when initialized the self.data is synced with the latest crawler result in "./res/".

    important functions:
        - search_titles(keyword)
        searches all articles titles for the given in keyword and returns them as list.

        - search_descriptions(keyword)
        searches all articles descriptions for the given in keyword and returns them as list.

        - search_full(keyword)
        searches articles titles and descriptions for the given in keyword and returns them as list.

        - update()
        updates the internal dataset with the newest from "./results/".

    """

    def __init__(self):
        # init __CRAWLER instance for getting the data
        self.__CRAWLER = Crawler()
        # get the data
        self.data = self.__CRAWLER.get_last_article_result()

    def search_titles(self, keyword):
        """ searches all titles in self.data for the given in keyword.

        :param keyword: keyword to filter for
        :type keyword: str
        :return: list of all titles and the corresponding url
        """
        result = list()
        keyword = str(keyword).lower()
        for source in self.data:
            for article in source['articles']:
                if keyword in article['title'].lower():
                    tmp_result = dict(
                        title=article['title'],
                        url=article['url']
                    )
                    result.append(tmp_result)
        return result

    def search_descriptions(self, keyword):
        """ searches all descriptions in self.data for the given in keyword.

        :param keyword: keyword to filter for
        :type keyword: str
        :return: list of all descriptions and the corresponding url
        """
        result = list()
        keyword = str(keyword).lower()
        for source in self.data:
            for article in source['articles']:
                if article['description'] is not None:
                    if keyword in article['description'].lower():
                        tmp_result = dict(
                            description=article['description'],
                            url=article['url']
                        )
                        result.append(tmp_result)
        return result

    def search_full(self, keyword):
        """ searches all titles and descriptions in self.data for the given in keyword.

        :param keyword: keyword to filter for
        :type keyword: str
        :return: list of all titles and/or descriptions and the corresponding url
        """
        keyword = str(keyword).lower()
        full_result = list()
        # get independent search results and add them together
        description_results = self.search_descriptions(keyword)
        headline_results = self.search_titles(keyword)
        for headline in headline_results:
            for description in description_results:
                if headline['url'] == description['url']:
                    tmp_result = dict(
                        title=headline['title'],
                        description=description['description'],
                        url=headline['url']
                    )
                    full_result.append(tmp_result)
                    headline_results.remove(headline)
                else:
                    full_result.append(description)
        for headline in headline_results:
            full_result.append(headline)
        return full_result

    def update(self):
        """ updates self.data with the newest file in "./results/"
        """
        self.data = self.__CRAWLER.get_last_article_result()


#####
# the following functions are only for providing cli via fire library.
#####

def fire_search_title(keyword):
    searcher = Searcher()
    result = searcher.search_titles(keyword)
    fire_print(result)


def fire_search_description(keyword):
    searcher = Searcher()
    result = searcher.search_descriptions(keyword)
    fire_print(result)


def fire_search_full(keyword):
    searcher = Searcher()
    result = searcher.search_full(keyword)
    fire_print(result)


def fire_print(search_result):
    for element in search_result:
        print()
        try:
            print('Titel: {0}'.format(element['title']))
        except KeyError:
            pass
        try:
            print('Description: {0}'.format(element['description']))
        except KeyError:
            pass
        print('URL: {0}'.format(element['url']))


if __name__ == '__main__':
    payload = dict(
        search_full=fire_search_full,
        search_title=fire_search_title,
        search_description=fire_search_description
    )
    fire.Fire(payload)
