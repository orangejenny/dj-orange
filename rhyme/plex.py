from plexapi.myplex import MyPlexAccount
from django.conf import settings

def plex_server():
    account = MyPlexAccount(settings.PLEX_USERNAME, settings.PLEX_PASSWORD)
    return account.resource(settings.PLEX_SERVER).connect()

def plex_library(server):
    return server.library.section('Music')
