import json

from datetime import datetime, timedelta


def create_fixture(source_file, fixture_file):
    """
    Create fixture in json format for the Django
    model migration based on a provided txt file.
    """

    with open(source_file) as f:
        outages_json = json.load(f)

    for idx, item in enumerate(outages_json):
        item['pk'] = idx + 1
        item['model'] = 'service_outages.ServiceOutageRecord'
        start_time = datetime.strptime(item['startTime'], '%Y-%m-%d %H:%M:%S')
        end_time = start_time + timedelta(minutes=item['duration'])
        item['fields'] = {
            'service_id': item['id'],
            'duration': item['duration'],
            'start_time': datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S'),
        }
        del item['id']
        del item['duration']
        del item['startTime']

    with open(fixture_file, 'w') as fw:
        json.dump(outages_json, fw)


if __name__ == '__main__':
    create_fixture('outages.txt', '../fixtures/outages.json')
