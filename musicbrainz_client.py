"""musicbrainz_client.py — talks to the MusicBrainz API to check if an ISRC
or ISWC already exists for a different recording or work.

MusicBrainz asks every app to send a real contact in the User-Agent header.
This is not an API key, it is just how they identify who is using the service.
Docs: https://musicbrainz.org/doc/MusicBrainz_API
"""

import time
import requests

BASE_URL = "https://musicbrainz.org/ws/2"

# MusicBrainz wants a name, a version, and a contact (email or URL).
USER_AGENT = "PreFlight/2.0 ( https://github.com/RiccardoDurante/preflight )"

# MusicBrainz allows about 1 request per second. We remember the time of the
# last request, and if not enough time has passed, we wait before sending
# the next one.
_last_request_time = 0.0
MIN_SECONDS_BETWEEN_REQUESTS = 1.0


def _wait_for_rate_limit():
    global _last_request_time

    now = time.time()
    seconds_since_last_request = now - _last_request_time

    if seconds_since_last_request < MIN_SECONDS_BETWEEN_REQUESTS:
        time_to_wait = MIN_SECONDS_BETWEEN_REQUESTS - seconds_since_last_request
        time.sleep(time_to_wait)

    _last_request_time = time.time()


def search_recordings_by_isrc(isrc):
    """
    Ask MusicBrainz which recordings are registered under this ISRC.

    Returns a list of dicts, one per recording found. Each dict has:
        - "title": the recording title
        - "artist": the main artist name (empty string if unknown)
        - "mbid": the MusicBrainz id of the recording

    Returns an empty list if nothing was found, or if the ISRC is empty.
    """
    if not isrc:
        return []

    _wait_for_rate_limit()

    url = f"{BASE_URL}/isrc/{isrc}"
    params = {"fmt": "json", "inc": "artist-credits"}
    headers = {"User-Agent": USER_AGENT}

    response = requests.get(url, params=params, headers=headers, timeout=10)

    # 404 means "no recording with this ISRC". Not an error for us.
    if response.status_code == 404:
        return []

    # 503 means "you are going too fast". We wait a bit and try one more time.
    if response.status_code == 503:
        time.sleep(2.0)
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 404:
            return []

    response.raise_for_status()

    data = response.json()
    recordings = data.get("recordings", [])

    results = []
    for recording in recordings:
        title = recording.get("title", "")
        mbid = recording.get("id", "")

        artist_name = ""
        artist_credits = recording.get("artist-credit", [])
        if len(artist_credits) > 0:
            first_credit = artist_credits[0]
            artist_info = first_credit.get("artist", {})
            artist_name = artist_info.get("name", "")

        result = {
            "title": title,
            "artist": artist_name,
            "mbid": mbid,
        }
        results.append(result)

    return results


def search_works_by_iswc(iswc):
    """
    Ask MusicBrainz which works (compositions) are registered under this ISWC.

    Returns a list of dicts, one per work found. Each dict has:
        - "title": the work's title
        - "composers": a list of composer/writer names linked to this work
        - "mbid": the MusicBrainz id of the work

    Returns an empty list if nothing was found, or if the ISWC is empty.
    """
    if not iswc:
        return []

    _wait_for_rate_limit()

    url = f"{BASE_URL}/iswc/{iswc}"
    params = {"fmt": "json", "inc": "artist-rels"}
    headers = {"User-Agent": USER_AGENT}

    response = requests.get(url, params=params, headers=headers, timeout=10)

    # 404 means "no work with this ISWC". Not an error for us.
    if response.status_code == 404:
        return []

    # 503 means "you are going too fast". We wait a bit and try one more time.
    if response.status_code == 503:
        time.sleep(2.0)
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 404:
            return []

    response.raise_for_status()

    data = response.json()
    works = data.get("works", [])

    results = []
    for work in works:
        title = work.get("title", "")
        mbid = work.get("id", "")

        composers = []
        relations = work.get("relations", [])
        for relation in relations:
            artist_info = relation.get("artist", {})
            artist_name = artist_info.get("name", "")
            if artist_name:
                composers.append(artist_name)

        result = {
            "title": title,
            "composers": composers,
            "mbid": mbid,
        }
        results.append(result)

    return results


# Smoke test: `python musicbrainz_client.py`
if __name__ == "__main__":
    # A real ISRC, used as an example in MusicBrainz's own documentation.
    test_isrc = "GBDUW0000053"
    print(f"Searching MusicBrainz for ISRC: {test_isrc}")

    found = search_recordings_by_isrc(test_isrc)

    if len(found) == 0:
        print("No recordings found for this ISRC.")
    else:
        print(f"Found {len(found)} recording(s):")
        for recording in found:
            print(f"  - '{recording['title']}' by {recording['artist']} (mbid: {recording['mbid']})")

    # Smoke test for the ISWC search.
    print()
    test_iswc = "T-101.690.320-9"
    print(f"Searching MusicBrainz for ISWC: {test_iswc}")

    found_works = search_works_by_iswc(test_iswc)

    if len(found_works) == 0:
        print("No works found for this ISWC.")
    else:
        print(f"Found {len(found_works)} work(s):")
        for work in found_works:
            composer_names = ", ".join(work["composers"]) if work["composers"] else "(unknown)"
            print(f"  - '{work['title']}' by {composer_names} (mbid: {work['mbid']})")
