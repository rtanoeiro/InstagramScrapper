"""
This module will be used to save login cookies on your computer in case
the usual instaloader.login function is requiring user input on the browser.

1. Login on Mozilla Firefox into Instagram.
2. After that you can run instagram_scrapper.py
    and it should get cookie and username from this module.
"""
# TODO: CONVERT INTO A CLASS
from argparse import ArgumentParser
from glob import glob
from os.path import expanduser
from platform import system
from sqlite3 import OperationalError, connect

try:
    from instaloader import ConnectionException, Instaloader
except ModuleNotFoundError:
    raise SystemExit("Instaloader not found.\n  pip install [--user] instaloader")

class InstagramLogin:
    def __init__(self) -> None:



    def get_cookiefile(self):
        default_cookiefile = {
            "Windows": "~/AppData/Roaming/Mozilla/Firefox/Profiles/*/cookies.sqlite",
            "Darwin": "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite",
        }.get(system(), "~/.mozilla/firefox/*/cookies.sqlite")
        cookiefiles = glob(expanduser(default_cookiefile))
        if not cookiefiles:
            raise SystemExit("No Firefox cookies.sqlite file found. Use -c COOKIEFILE.")
        return cookiefiles[0]


    def import_session(self, cookiefile, sessionfile):
        print(f"Using cookies from {cookiefile}.")
        conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
        try:
            cookie_data = conn.execute(
                "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com'"
            )
        except OperationalError:
            cookie_data = conn.execute(
                "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
            )
        instaloader = Instaloader(max_connection_attempts=1)
        instaloader.context._session.cookies.update(cookie_data)
        username = instaloader.test_login()
        if not username:
            raise SystemExit("Not logged in. Are you logged in successfully in Firefox?")
        print(f"Imported session cookie for {username}.")
        instaloader.context.username = username
        instaloader.save_session_to_file(sessionfile)

        return cookiefile, username


    def get_cookie_location(self):
        parser = ArgumentParser()
        parser.add_argument("-c", "--cookiefile")
        parser.add_argument("-f", "--sessionfile")
        args = parser.parse_args()
        try:
            cookiefile, username = self.import_session(args.cookiefile or self.get_cookiefile(), args.sessionfile)
        except (ConnectionException, OperationalError) as exception:
            raise SystemExit(f"Cookie import failed: {exception}")

        return cookiefile, username
