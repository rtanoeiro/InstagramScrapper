"""
This module will be used to save login cookies on your computer in case
the usual instaloader.login function is requiring user input on the browser.

1. Login on Mozilla Firefox into Instagram.
2. After that you can run instagram_scrapper.py
    and it should get cookie and username from this module.
"""
from argparse import ArgumentParser
from glob import glob
from os.path import expanduser
from platform import system
from sqlite3 import OperationalError, connect
import logging
import sys
import io

try:
    from instaloader import ConnectionException, Instaloader
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Instaloader not found.\n  pip install [--user] instaloader"
    ) from exc

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s"
)

def get_cookiefile():
    """
    This function will get the cookie file from the login on Mozilla

    Raises:
        SystemExit: In case there are no cookies, an error is thrown

    Returns:
        cookiefiles[0]: The path location to the cookie
    """
    default_cookiefile = {
        "Windows": "~/AppData/Roaming/Mozilla/Firefox/Profiles/*/cookies.sqlite",
        "Darwin": "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite",
    }.get(system(), "~/.mozilla/firefox/*/cookies.sqlite")
    cookiefiles = glob(expanduser(default_cookiefile))
    if not cookiefiles:
        raise SystemExit("No Firefox cookies.sqlite file found. Use -c COOKIEFILE.")
    return cookiefiles[0]

def import_session(cookiefile: str, sessionfile: str):
    """
    This function will be used to grab the username and cookie
    from the Mozilla Firefox Session

    Args:
        cookiefile (str): cookie file from get_cookiefile function
        sessionfile (str): filename where cookie is stored

    Raises:
        SystemExit: In case user is not logged in on Mozilla Firedox,
        this will thrown an error

    Returns:
        cookiefile, username: Returns the cookie file location and username
        that is logged in to be used on the get_cookie_file_and_username function
    """
    logging.info("Using cookies from %s", cookiefile)
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
        raise SystemExit(
            "Not logged in. Are you logged in successfully in Firefox?"
        )
    logging.info("Imported session cookie for %s.", username)
    instaloader.context.username = username

    buffer = io.StringIO()
    sys.stdout = buffer
    instaloader.save_session_to_file(sessionfile)
    sys.stdout = sys.__stdout__
    session_file = buffer.getvalue().replace("Saved session to ", "").replace("\n", "")

    return username, session_file

def get_username_and_session_file() -> str:
    """
    This function will get the cookie file location
    and username. These will be used load a Instagram Session.
    The session will then be used to create the instaloader context,
    user in many of the library class/functions

    Raises:
        SystemExit: In case the cookie import fails, an error is raised

    Returns:
        cookiefile, username: Returns the cookie file location and username
        that is logged in to be used on the get_cookie_file_and_username function
    """
    parser = ArgumentParser()
    parser.add_argument("-c", "--cookiefile")
    parser.add_argument("-f", "--sessionfile")
    args = parser.parse_args()
    try:
        username, session_file = import_session(
            args.cookiefile or get_cookiefile(), args.sessionfile
        )
    except (ConnectionException, OperationalError) as excecption:
        raise SystemExit("Cookie import failed") from excecption

    return username, session_file
