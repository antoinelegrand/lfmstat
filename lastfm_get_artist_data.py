# Last.fm artist data download
# Script to retrieve artist data from last.fm DB for a given user

# written for python 3
# using re for Regular Expressions
# using requests for URL access
# using xml.etree for XML parsing

# command line parameters
# Last.fm user name
# Last.fm API key

import re
import sys
import requests
import datetime
import xml.etree.ElementTree as ET

debug = 0
live = 0

def runLive():
    if (live==1):
        return True

def dbgout(string):
    if (debug==1):
        print(string, file=traceFile)

def timeStamp():
    dt = datetime.datetime.now().isoformat()
    ts = re.sub(r"[:T.]", '_', dt)
    return ts

def buildUrl(command):
    urlRoot = 'http://ws.audioscrobbler.com/2.0/'
    urlCmd = '?method=' + command
    urlUser = '&user=' + lfmUserName
    urlAPIKey = '&api_key=' + lfmAPIKey
    url = urlRoot + urlCmd + urlUser + urlAPIKey
    return url

def cleanUpNameForFileSystem(name):
    cleanName = re.sub(r"[ \/\?\!\>\:\;]+", '_', name)
    return cleanName

def downloadArtistInfoFromLFMToFile(artistName, fileName):
    r = requests.get(buildUrl('artist.getInfo&artist=' + artistName))
    artistInfo = r.text
    artistInfoFile = open(fileName, 'w', encoding='utf-8')
    print(artistInfo, file=artistInfoFile)
    artistInfoFile.close()

# init variables and files

lfmUserName = sys.argv[1] 
lfmAPIKey = sys.argv[2]

ts = timeStamp()
traceFile = open("lastfm_stats_log_%s.txt" % ts, 'w', encoding='utf-8')
if (runLive()):
    topArtistsFile = open('lastfm_topartists.xml', 'w', encoding='utf-8')
else:
    topArtistsFile = open('lastfm_topartists.xml', 'r', encoding='utf-8')
resultsFile = open("lastfm_stats_results_%s.txt" % ts, 'w', encoding='utf-8')

dbgout("LastFm top artists for %s" % lfmUserName)

if (runLive()):
    # get top artists from last.fm
    dbgout('get from lfm top artists for: ' + lfmUserName)
    r = requests.get(buildUrl('user.getTopArtists&limit=1000'))
    dbgout(r)
    dbgout(r.text)
    print(r.text, file=topArtistsFile)

topArtistsFile.close()

# fill table from xml

noArtists = 0
artistData = {}
topArtistsTree = ET.parse('lastfm_topartists.xml')
root = topArtistsTree.getroot()
for entry in root[0]:
    # get details from top artists xml
    artistRank = entry.get('rank')
    artistName = entry[0].text
    try:
        print("%s: %s" % (artistRank, artistName))
    except:
        print("%s: %s" % (artistRank, '[not printable]'))
        
    artistInfoFileName = "lastfm_info_%s.xml" % cleanUpNameForFileSystem(artistName)
    artistPlaycount = entry[1].text
    dbgout("rank: %s" % artistRank)
    dbgout("name: %s" % artistName)
    dbgout("playcount: %s" % artistPlaycount)

    # check for presence of artist info file
    issueOpeningArtistInfoFile = False
    try:
        artistInfoFile = open(artistInfoFileName, 'r', encoding='utf-8')
    except:
        issueOpeningArtistInfoFile = True
        
    # if running live, update artist info from lfm
    if (runLive() or issueOpeningArtistInfoFile):
        # get info about current artist from lfm and copy to file
        downloadArtistInfoFromLFMToFile(artistName, artistInfoFileName)

    # parse file to generate info tree    
    try:    
        artistInfoTree = ET.parse(artistInfoFileName)
        artistBioTree = artistInfoTree.find('artist').find('bio')
        try: 
            artistSummary = artistBioTree.find('summary').text
        except:
            artistSummary = ''        
        try:
            artistPlaceFormed = artistBioTree.find('placeformed').text
        except:
            artistPlaceFormed = ''
        dbgout("summary: %s" % artistSummary)
        dbgout("origin: %s" % artistPlaceFormed)

        artistData[artistRank] = {artistName, artistPlaycount, artistPlaceFormed}
        print(artistName + ', ' + artistPlaycount + ', ' + artistPlaceFormed, file=resultsFile)

    except:
        issueOpeningArtistInfoFile = True
        dbgout("issue opening file %s for artist %s!" % (artistInfoFileName, artistName))
        
   
    noArtists += 1

dbgout('number of artists = %d' % noArtists)

topArtistsFile.close()
traceFile.close()
resultsFile.close()
