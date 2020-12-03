import argparse
import csv
import json
import os
import shutil

import requests

FIELD_CONFIG = {
    'language': {
        'multiple': True,
    }
}

def main(args):
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            doi = row.pop('doi')
            print(f"Processing {doi}...")
            print(update(doi, row, args.api_key, args.replace, args.domain).content.decode())
            if args.publish:
                print(publish(doi, args.api_key, args.domain, args.version_type).content.decode())
            print("Done")
            

def update(doi, fields, api_key=None, replace=False, domain="dataspire-test"):  # http://guides.dataverse.org/en/latest/api/native-api.html#edit-dataset-metadata
    replace_str = 'true' if replace else 'false'
    url = f'https://{domain}.sciencespo.fr/api/datasets/:persistentId/editMetadata/?persistentId={doi}&replace={replace}'
    headers = {'X-Dataverse-key': api_key}
    metadata = {'fields': []}
    for k, v in fields.items():
        field = {'typeName': k, 'value': v if not (k in FIELD_CONFIG and FIELD_CONFIG[k]['multiple']) else v.split('|')}
        metadata['fields'].append(field)
    print(json.dumps(metadata))
    return requests.put(url, data=json.dumps(metadata), headers=headers)

def publish(doi, api_key=None, domain="dataspire-test", version_type='minor'):  # http://guides.dataverse.org/en/latest/api/native-api.html#publish-a-dataset
    url = f'https://{domain}.sciencespo.fr/api/datasets/:persistentId/actions/:publish?persistentId={doi}&type={version_type}'
    headers = {'X-Dataverse-key': api_key}
    return requests.post(url, headers=headers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Updates datasets from csv.')
    parser.add_argument('filename', help='csv file with metadata')
    parser.add_argument('-k', '--key', dest='api_key', help='api key', required=True)
    parser.add_argument('-s', '--server-domain', default='dataspire-test', dest='domain', help='domain (e.g. dataspire-test for dataspire-test.sciencespo.fr')
    parser.add_argument('-r', '--replace', action='store_true', dest='replace', help='replace metadata value')
    parser.add_argument('-p', '--publish', action='store_true', dest='publish', help='publish dataset')
    parser.add_argument('--version-type', default='minor', dest='version_type', help='version type when publishing: minor or major')
    args = parser.parse_args()
    main(args)
