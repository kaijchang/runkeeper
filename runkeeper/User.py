import requests

from datetime import datetime

import typing


class User:
    def __init__(self, username: str):
        self.username = username

    def get_activities(self, month: int = None, year: int = None) -> typing.List[typing.Dict[str, str]]:
        """
        :param month: month of specified year to fetch activities for
        :type month: int
        :param year: year to fetch activities for
        :type year: int
        :return: list of activities from the specified month
        :rtype: dict
        """
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        start_date = datetime(year, month, 1)
        return requests.get('https://runkeeper.com/activitiesByDateRange', params={
            'userName': self.username,
            'startDate': start_date.strftime('%b-%d-%Y')
        }).json()['activities'][str(start_date.year)][start_date.strftime('%b')]
