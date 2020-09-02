import requests
import json
import sys
import os


ARTIFACT_NAME = sys.argv[1]
ACCESS_TOKEN = sys.argv[2]
ACTION = sys.argv[3]
REPO_NAME = sys.argv[4]
ARTIFACTS_URL = 'https://api.github.com/repos/{}/actions/artifacts{}'
HEADERS = {
    'Authorization': 'token {}'.format(ACCESS_TOKEN),
    'Accept': 'application/vnd.github.v3+json'
}


def get_artifacts_info():
    r = requests.get(ARTIFACTS_URL.format(REPO_NAME, ''), headers=HEADERS)
    r.raise_for_status()
    return json.loads(r.text)


def get_artifact():
    if os.path.exists(ARTIFACT_NAME):
        os.unlink(ARTIFACT_NAME)

    info = get_artifacts_info()

    if info['total_count'] > 0:
        with requests.get(info['artifacts'][0]['archive_download_url'], headers=HEADERS, stream=True) as r:
            r.raise_for_status()
            with open(ARTIFACT_NAME, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)


def delete_artifacts():
    info = get_artifacts_info()

    # purge all artifacts
    for artifact in info['artifacts']:
        requests.delete(ARTIFACTS_URL.format(REPO_NAME, artifact['id']), headers=HEADERS)


if __name__ == '__main__':
    DISPATCHER = {
        'GET': get_artifact,
        'DELETE': delete_artifacts
    }

    # if bad action i want exception to be raised
    DISPATCHER[ACTION]()
