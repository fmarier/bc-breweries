#!/usr/bin/python3
"""
craft_breweries - List all BC craft breweries.

Displays the list of all BC craft breweries as shown on the
BC Craft Brewers Guild website.

Copyright (C) 2019, 2020  Francois Marier <francois@fmarier.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import gzip
import io
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from lxml import html  # nosec

VERSION = '0.1'
LIST_URL = 'https://bccraftbeer.com/our-breweries/'

KNOWN_BREWERIES = [
    '33 Acres Brewing',
    '4 Mile Brewing Co.',
    'A-FRAME Brewing',
    'Abandoned Rail Brewing Company',
    'Ace Brewing Company',
    'Alberni Brewing Company',
    'Andina Brewing Company',
    'Angry Hen Brewing Co',
    'Another Beer Company Inc',
    'Backcountry Brewing',
    'Backroads Brewing Company',
    'Bad Dog Brewing Company',
    'Bad Tattoo Brewing',
    'Barkerville Brewing',
    'Barley Mill Brew Pub',
    'Barley Station Brew Pub',
    'Barn Owl Brewing Company',
    'Barnside Brewing Co Ltd',
    'Batch 44 Brewery',
    'Beach Fire Brewing and Nosh House',
    'Beacon Brewing Ltd',
    "Beard's Brewing Co",
    'Beere Brewing',
    'Big Ridge Brewing Co.',
    'Black Kettle Brewing Co',
    'BNA Brewing',
    'Bomber Brewing',
    'Brassneck Brewery',
    'BREWHALL BEER CO.',
    'Bricklayer Brewing',
    'Bridge Brewing Co',
    'Bright Eye Brewing',
    'Bulkley Valley Brewery',
    'Callister Brewing Company',
    'Camp Beer Co',
    'Cannery Brewing Company',
    'Canoe Brewpub',
    'Category 12 Brewing',
    'Central City Brewers + Distillers',
    'Central City Brewpub',
    'Checkerhead Brewing',
    'Coast Mountain Brewing',
    'Container Brewing Ltd.',
    'Copper Brewing Co',
    'Craig Street Brewing Co.',
    'Crannóg Ales',
    'CrossRoads Brewing',
    'Cumberland Brewing',
    'Dageraad Brewing',
    'Dead Frog Brewery',
    'Deadfall Brewing Company',
    'Deep Cove Brewers & Distillers',
    'Devil\'s Bath Brewing Co.',
    'Dockside Brewing Company',
    'Dog Mountain Brewing',
    'Driftwood Brewery',
    'East Vancouver Brewing Co',
    'Electric Bicycle Brewing',
    'Empty Keg Brew House',
    'Erie Creek Brewing Co',
    'Faculty Brewing Co',
    'Farm Country Brewing Inc',
    'Farmhouse Brewing Co',
    'Fern + Cedar Brewing',
    'Fernie Brewing Company',
    'Field House Brewing',
    'Firehall Brewery',
    'Fisher Peak Brewing Co / The Heid Out',
    'Five Roads Brewing Co',
    'Flashback Brewing Company',
    'Foamers Folly Brewing Co.',
    'Four Winds Brewing',
    'Fox Mountain Brewing Co',
    'Fraser Mills Fermentation Company',
    "Freddy's Brewpub",
    'Fuggles & Warlock Craftworks',
    'Galaxie Craft Brewhouse',
    'Gladstone Brewing',
    'Green Leaf Brewing Co',
    'Herald St. Brew Works',
    'High Mountain Brewing Company',
    'Highway 97 Brewing Co',
    'Home Town Beer Makers',
    'Hornby Island Brewing Co',
    'House of Funk Brewing Co',
    'Howe Sound Brewing',
    'Howl Brewing',
    'Hoyne Brewing Co. Ltd.',
    'île Sauvage Brewing Company',
    'Iron Road Brewing',
    'Jackknife Brewing',
    'Kelowna Beer Institute',
    'Kelowna Brewing Company (KBC)',
    'Kettle River Brewing Co',
    'Kind Brewing',
    'Kwantlen Polytechnic University Brewing',
    'Lakesider Brewing',
    'Land & Sea Brewing Company',
    'Lighthouse Brewery',
    'Lillooet Brewing Company',
    'Locality Brewing',
    'Longwood Brewery',
    'Longwood Brewpub',
    'LoveShack Libations',
    'Luppolo Brewing Company',
    'Main Street Brewing',
    'Maple Meadows Brewing',
    'Mariner Brewing',
    'Marten Brewing Company',
    'Mayne Island Brewing Company',
    'Mighty Peace Brewing Co.',
    'Monkey 9 Brewing Co',
    'Moody Ales',
    'Moon Under Water Brewery - Pub and Distillery',
    'Morrow Beer Company',
    'Mount Arrowsmith Brewing Co',
    'Mountainview Brewing Company',
    'Mt. Begbie Brewing Co.',
    'Neighbourhood Brewing',
    'Nelson Brewing Company',
    'New Tradition Brewing Company',
    'Noble Pig Brewhouse',
    'North Basin Brewing Co',
    'North Island College Craft Brewing and Malting Program',
    'North Point Brewing Co',
    'Northpaw Brew Co.',
    'Off The Rail Brewing Co',
    'Old Abbey Ales',
    'Old Yale Brewing Co.',
    'Over Time Beer Works',
    'Parallel 49 Brewing',
    'Patina Brewhouse & BBQ',
    'Pemberton Brewing Co',
    'Persephone Brewing Company',
    'Phillips Brewery',
    'Powell Brewery',
    'R&B Brewing Company',
    'Radium Brewing',
    'Ravens Brewing Company',
    'Red Arrow Brewing',
    'Red Bird Brewing Inc',
    'Red Collar Brewing Co.',
    'Red Truck Beer Company',
    'Ridge Brewing Company',
    'Riot Brewing Co',
    'Rossland Beer Company',
    'Rumpus Beer Company',
    'Russell Brewing Company',
    'Rusted Rake Brewing',
    'Rustic Reel Brewing Co',
    'Salt Spring Brewing Corporation',
    'Settlement Brewing',
    'Sherwood Mountain Brewhouse Ltd.',
    'Shore Line Brewing Co',
    'Silver Valley Brewing Co Ltd',
    'Slackwater Brewing',
    'Slow Hand Beer Company Inc',
    'Small Block Brewery',
    'Smithers Brewing Co',
    'Smugglers Trail Caskworks',
    'Sooke Brewing Company',
    'Sooke Oceanside Brewery',
    'Spinnakers Brewpub',
    'Steamworks Brewing Company',
    'Steel & Oak Brewing',
    'Storm Brewing Company',
    'Strange Fellows Brewing',
    'Strathcona Beer Company',
    'Streetcar Brewing',
    'Studio Brewing',
    'Superflux Beer Company',
    'Swans Brewery',
    'Tailout Brewing',
    'Tapworks Brewing Company',
    'Taylight Brewing Inc',
    'The 101 Brewhouse & Distillery',
    'The Bakery Brewing',
    'The Beer Farmers',
    'The Lions Head',
    'The Parkside Brewery',
    'The Tin Whistle Brewing Company',
    'Three Ranges Brewing',
    'Tiki Jon\'s Tiki Lounge & Brewery Ltd',
    'Tinhouse Brewing Inc',
    'Tofino Brewing Company',
    'Torchlight Brewing Co',
    'Townsite Brewing',
    'Trading Post Brewery',
    'Trading Post Brewing - District Wine Village',
    'Trail Beer Refinery',
    'Trench Brewing & Distilling',
    'Twa Dogs Brewery',
    'Twin City Brewing Company',
    'Twin Sails Brewing',
    'Ucluelet Brewing Company',
    'Unleashed Brewing Co',
    'Upscale Brewing',
    'Ursa Minor Brewing Corp (BC)',
    'V2V Blacks Hops Brewing Co.',
    'Vancouver Island Brewing',
    'Vice & Virtue Brewing Co.',
    'Welton Brewery Inc',
    'Wheelhouse Brewery',
    'Whistle Buoy Brewing Co.',
    'Whistler Brewing Company',
    'White Sails Brewing',
    'Whitetooth Brewing',
    'Wild North Brewing Co',
    'Wildeye Brewing',
    'Wolf Brewing Company',
    'Yaletown Brewing Co.',
    'Yellow Dog Brewery'
]

# pylint: disable=invalid-name
breweries = {}
new_breweries = []
all_breweries = []


def print_stats(quiet):
    """Output a summary of the number of known breweries."""
    need_newline = False
    if not quiet:
        print("Known breweries: %s" % len(KNOWN_BREWERIES))
        need_newline = True
    if new_breweries:
        print("New breweries: %s" % len(new_breweries))
        need_newline = True
    if need_newline:
        print("")


def print_brewery(ref, data):
    """Output details for a single brewery."""
    print("%s:" % ref)
    print("  %s" % data["url"])


def print_breweries(verbose, quiet):
    """Output all breweries with their metadata."""
    need_newline = False
    for ref in sorted(breweries):
        data = breweries[ref]
        if verbose or ref in new_breweries:
            print_brewery(ref, data)
            need_newline = True

    if len(KNOWN_BREWERIES) != len(all_breweries):
        if need_newline:
            print()
            need_newline = False

        for ref in sorted(KNOWN_BREWERIES):
            if ref not in all_breweries:
                print("%s is no longer listed" % ref)
                need_newline = True

    if not quiet:
        if need_newline:
            print()
        print(sorted(all_breweries))


def process_brewery(link):
    """Extract brewery metadata."""
    name = link.text.strip()
    url = link.values()[0]
    breweries[name] = {
        "name": name,
        "url": url,
    }

    all_breweries.append(name)
    if name not in KNOWN_BREWERIES:
        new_breweries.append(name)


def process_html(page):
    """Extract the list of breweries out of the page."""
    tree = html.fromstring(page)
    items = tree.xpath('//*[@id="list-inner"]/ul/li/a')
    for item in items:
        process_brewery(item)


def download_html(url):
    """Download the BC Craft Brewers Guild HTML in an efficient way."""
    request = Request(url, headers={'Accept-encoding': 'gzip'})
    response = urlopen(request)  # nosec

    if response.info().get('Content-Encoding') == 'gzip':
        buf = io.BytesIO(response.read())
        response = gzip.GzipFile(fileobj=buf)

    return response.read()


def main():
    """Parse arguments and start the whole process."""
    parser = argparse.ArgumentParser(
        description='Display the list of breweries as shown on %s.' % LIST_URL)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='display all brewery details')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='suppress output unless there are new breweries')
    parser.add_argument('-V', '--version', action='version',
                        version='craft_breweries %s' % VERSION)
    args = parser.parse_args()
    if args.verbose and args.quiet:
        print("Error: --quiet and --verbose are mutually exclusive",
              file=sys.stderr)
        return False

    try:
        process_html(download_html(LIST_URL))
    except HTTPError as e:
        print("Error while downloading the list: %s" % e, file=sys.stderr)
        return False
    except URLError as e:
        print("Error while downloading the list: %s" % e, file=sys.stderr)
        return False

    print_stats(args.quiet)
    print_breweries(args.verbose, args.quiet)
    return True


if main():
    sys.exit(0)
else:
    sys.exit(1)
