import glob
import os
from subprocess import call
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.rrule import rrule, DAILY

last_date = max([x.split(os.sep)[-1] for x in glob.glob("../data/*.json.gz")])[:10]
# print(datetime.strptime('%Y-%m-%d', last_date))
starting_date = parser.parse(last_date) + timedelta(days=1)
ending_date = datetime.now() - timedelta(days=1)

prefix = 'http://data.githubarchive.org/'
for dt in rrule(DAILY, dtstart = starting_date, until=ending_date):
    for cnt in range(24):
        date_url = prefix + dt.strftime('%Y-%m-%d') + '-' + str(cnt) + '.json.gz'

        call(['wget', date_url, '-P', '../data'])
