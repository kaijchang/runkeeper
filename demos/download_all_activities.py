import os
import json

from runkeeper import Account

if not os.path.exists('activities') or not os.path.isdir('activities'):
    os.mkdir('activities')

account = Account(os.environ.get('RK_USERNAME'), os.environ.get('RK_PASSWORD'))

activity_count = account.get_activity_count()

for year in activity_count:
    for month in activity_count[year]:
        activities = account.get_activities(month, year)
        for activity in activities:
            activity_data = account.get_activity_data(activity['activity_id'])
            trip_point_data = account.get_trip_point_data(activity_data['trip_uuid'])
            with open('activities/' + '-'.join((activity['year'], activity['monthNum'], activity['dayOfMonth'],
                                                activity['mainText'], str(activity['activity_id']))) + '.json', 'w') as activity_file:
                activity_file.write(json.dumps({
                    'summary': activity_data,
                    'points': trip_point_data
                }))
