# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

import requests
import time
from enum import Enum


class Limit(Enum):
    Sleep = 0,
    Ignore = 1
    # self.rem does not get out of sync
    # def _limit_sync(self, header):
    #     """ Get remaining request """
    #     return
    #     if 'x-ratelimit-remaining' in header:
    #         print(self.rem, int(header['x-ratelimit-remaining']))
    #         self.rem = int(header['x-ratelimit-remaining'])


class TMDbAPY():
    """ keep tracks of request per 10 seconds, do everything to avoid request failure,
        wait if to many request were placed"""

    def __init__(self, api_key, policy=Limit.Sleep):
        self.key = api_key
        self._address = 'http://api.themoviedb.org/3/'
        self.rem = 40
        self.time_start = None
        # What should we do if we exceed the request rate
        self.policy = policy

    def _safe_limit_check(self):
        """ Check if we are allowed to make a request to the API"""
        if self.rem == 40:
            self.time_start = time.time()
        elif time.time() - self.time_start >= 11:
            self.rem = 40
            self.time_start = time.time()
        elif self.rem <= 0:
            t = 11 - (time.time() - self.time_start)

            if t <= 0:
                self.rem = 40
                self.time_start = time.time()
            else:
                if self.policy == Limit.Sleep:
                    time.sleep(t)
                elif self.policy == Limit.Ignore:
                    return False

        self.rem -= 1
        return True

    def _status_code_handle(self, answer, retry_function=None):
        if 'status_code' in answer:
            if answer['status_code'] == 25:
                pass
                # self.rem = 0
                # if retry_function is not None:
                #     return retry_function()

        return None

    def _return_result(self, result, retry_function=None):
        if 'results' in result.json():
            return result.json()['results']
        else:
            return self._status_code_handle(result.json(), retry_function)

    def tv_search(self, name, year=None):
        make_request = self._safe_limit_check()

        if make_request:
            if year is not None:
                r = requests.get(self._address + 'search/tv', params={'api_key': self.key, 'query': name, 'first_air_date_year': year})
            else:
                r = requests.get(self._address + 'search/tv', params={'api_key': self.key, 'query': name})

            return self._return_result(r, lambda: self.tv_search(name, year))

    def movie_search(self, name, year=None, adult=False):
        make_request = self._safe_limit_check()

        if make_request:
            if year is None:
                r = requests.get(self._address + 'search/movie', params={'api_key': self.key, 'query': name, 'include_adult': False})
            else:
                r = requests.get(self._address + 'search/movie', params={'api_key': self.key, 'query': name, 'year': year, 'include_adult': adult})

            return self._return_result(r, lambda: self.movie_search(name, year, adult))

    def tv(self, tv_id):
        self._safe_limit_check()
        r = requests.get(self._address + 'tv/' + str(tv_id), params={'api_key': self.key})
        return r.json()

    def tv_credits(self, tv_id):
        self._safe_limit_check()
        r = requests.get(self._address + 'tv/' + str(tv_id) + '/credits', params={'api_key': self.key})
        return r.json()

    def movies_top_rated(self):
        self._safe_limit_check()
        r = requests.get(self._address + 'movie/top_rated', params={'api_key': self.key})
        return r.json()

    def movie(self, movie_id):
        self._safe_limit_check()
        r = requests.get(self._address + 'movie/' + str(movie_id), params={'api_key': self.key})
        return r.json()

    def movie_review(self, movie_id):
        self._safe_limit_check()
        r = requests.get(self._address + 'movie/' + str(movie_id) + '/review', params={'api_key': self.key})
        return r.json()


if __name__ == '__main__':

    inst = TMDbAPY("844238e82e0809bc08bb0d3c1d0842aa")
    inst.tv_search("fight club")