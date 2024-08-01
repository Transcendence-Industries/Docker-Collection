import os
import json
import logging
import requests

IMMICH_HOST = str(os.environ["IMMICH_HOST"])
IMMICH_API_KEY = str(os.environ["IMMICH_API_KEY"])

SOURCE_PATH_PICTURES = str(os.environ["SOURCE_PATH_PICTURES"])
SOURCE_PATH_VIDEOS = str(os.environ["SOURCE_PATH_VIDEOS"])

INCLUDED_DIRECTORIES = str(os.environ["INCLUDED_DIRECTORIES"]).split(",")
INCLUDED_USERS = str(os.environ["INCLUDED_USERS"]).split(",")
DELETE_ALL_ALBUMS = str(os.environ["DELETE_ALL_ALBUMS"]) in ("True", "true")


def request_api(url, payload={}, method="GET"):
    url = IMMICH_HOST + url
    payload = json.dumps(payload)
    headers = {
        "x-api-key": IMMICH_API_KEY,
        "Accept": "application/json"
    }

    if method == "POST" or method == "PUT":
        headers["Content-Type"] =  "application/json"
    elif method == "DELETE":
        del headers["Accept"]

    try:
        response = requests.request(method, url, headers=headers, data=payload)
    except:
        logging.error(f"Error while requesting {method}:{url}")
        return None

    if (response.status_code >= 200 and response.status_code <= 299):
        try:
            return json.loads(response.text)
        except:
            logging.error(f"Error while parsing JSON repsonse from request {method}:{url}")
            return None
    else:
        logging.error(f"Error with code {response.status_code} for request {method}:{url} - {response.text}")
        return None


def get_users():
    users = {}

    response = request_api("/api/users")
    if response == None:
        logging.error("Fetching of users failed!")
        exit(1)

    for user in response:
        if user["name"] in INCLUDED_USERS:
            users[user["name"]] = user["id"]

    logging.debug(f"Fetched users: {users}")
    logging.info(f"Fetched {len(users)} users.")
    return users


def get_immich_albums(withAssets=False):
    response = request_api("/api/albums")
    albums = {}

    if response == None:
        logging.error("Fetching of immich-albums failed!")
        exit(1)

    for album in response:
        if withAssets:
            # TODO: Should be removable, but the 'assets' tag from the above request is always empty
            response2 = request_api("/api/albums/" + album["id"])

            albums[album["albumName"]] = {
                "id": album["id"],
                # "assets": album["assets"]
                "assets": [asset["id"] for asset in response2["assets"]]
            }
        else:
            albums[album["albumName"]] = { "id": album["id"] }

    logging.debug(f"Existing immich-albums: {albums}")
    logging.info(f"Found {len(albums)} immich-albums.")
    return albums  # { albumName: { "id": albumID, "assets": [assetID] } }


def get_source_albums():
    if not os.path.exists(SOURCE_PATH_PICTURES):
        logging.error(f"Path {SOURCE_PATH_PICTURES} is not existent!")
        exit(1)
    elif not os.path.exists(SOURCE_PATH_VIDEOS):
        logging.error(f"Path {SOURCE_PATH_VIDEOS} is not existent!")
        exit(1)

    picture_dirs = [entry for entry in os.listdir(SOURCE_PATH_PICTURES) if os.path.isdir(os.path.join(SOURCE_PATH_PICTURES, entry))]
    video_dirs = [entry for entry in os.listdir(SOURCE_PATH_VIDEOS) if os.path.isdir(os.path.join(SOURCE_PATH_VIDEOS, entry))]
    picture_albums = {}
    video_albums = {}

    for p_dir in picture_dirs:
        for dir_path, dir_names, file_names in os.walk(os.path.join(SOURCE_PATH_PICTURES, p_dir)):
            if os.path.basename(dir_path) in INCLUDED_DIRECTORIES:
                picture_albums[p_dir] = [os.path.join(dir_path, file_name) for file_name in file_names]

    for v_dir in video_dirs:
        for dir_path, dir_names, file_names in os.walk(os.path.join(SOURCE_PATH_VIDEOS, v_dir)):
            if os.path.basename(dir_path) in INCLUDED_DIRECTORIES:
                video_albums[v_dir] = [os.path.join(dir_path, file_name) for file_name in file_names]

    logging.debug(f"Source (picture) albums: {picture_albums}")
    logging.debug(f"Source (video) albums: {video_albums}")
    logging.info(f"Found {len(picture_albums)} picture-albums and {len(video_albums)} video-albums.")
    return picture_albums, video_albums  # { albumName: [fileFullPath] }


def create_missing_albums(users, immich_albums, picture_albums, video_albums):
    new_albums = 0

    for album_name in set(picture_albums.keys()).union(video_albums.keys()):
        if album_name not in immich_albums.keys():
            payload = {
                "albumName": album_name,
                "albumUsers": [{ "role": "editor", "userId": user} for user in users],
                "assetIDs": [],
                "description": ""
            }

            request_api("/api/albums", payload=payload, method="POST")
            logging.debug(f"Created album '{album_name}'.")
            new_albums += 1

    logging.info(f"Created {new_albums} new albums.")


def update_album_content(immich_albums, picture_albums, video_albums):
    for album_name, album_details in immich_albums.items():
        album_id = album_details["id"]
        album_assets = album_details["assets"]

        source_assets = []
        new_assets = []

        if album_name in picture_albums.keys():
            source_assets.extend(picture_albums[album_name])
        if album_name in video_albums.keys():
            source_assets.extend(video_albums[album_name])

        for asset_path in source_assets:
            payload = {
                "originalPath": asset_path
            }

            response = request_api("/api/search/metadata", payload=payload, method="POST")
            asset_id = None

            try:
                if response["assets"]["total"] == 1:
                    asset_id = response["assets"]["items"][0]["id"]
                    logging.debug(f"Found ID for asset '{asset_path}'.")
                else:
                    logging.warning(f"Found more/less matches for asset '{asset_path}'.")
            except:
                logging.warning(f"Error during search for asset '{asset_path}'.")

            if asset_id and asset_id not in album_assets:
                new_assets.append(asset_id)

        payload = {
            "ids" : new_assets
        }

        request_api("/api/albums/" + album_id + "/assets", payload=payload, method="PUT")
        logging.debug(f"Added assets '{new_assets}' to album '{album_name}'.")
        logging.info(f"Added {len(new_assets)} assets to album '{album_name}'.")


def delete_albums(immich_albums):
    for album_name, album_details in immich_albums.items():
        request_api("/api/albums/" + album_details["id"], method="DELETE")
        logging.debug(f"Deleted album '{album_name}'.")
    logging.info(f"Deleted {len(immich_albums)} albums.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("----- START -----")

    i_albums = get_immich_albums()
    if DELETE_ALL_ALBUMS:
        delete_albums(i_albums)
        i_albums = get_immich_albums()

    p_albums, v_albums = get_source_albums()
    usr = get_users()
    create_missing_albums(list(usr.values()), i_albums, p_albums, v_albums)
    i_albums = get_immich_albums(withAssets=True)
    update_album_content(i_albums, p_albums, v_albums)

    logging.info("----- END -----")
