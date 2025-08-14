import os
import logging
from mutagen.id3 import ID3, TIT2, TPE1, TALB, ID3NoHeaderError

DEBUG = bool(os.environ["DEBUG"])
SOURCE_PATH_MUSIC = str(os.environ["SOURCE_PATH_MUSIC"])
INCLUDED_DIRS = str(os.environ["INCLUDED_DIRS"]).split(",")
FORCE_DELETION = str(os.environ["FORCE_DELETION"]) in ("True", "true")
FORCE_OVERWRITE = str(os.environ["FORCE_OVERWRITE"]) in ("True", "true")


def change_track_tags(track_path, tags):
    basename = os.path.basename(track_path)

    try:
        audio = ID3(track_path)

        if FORCE_DELETION:
            del audio["TIT2"]
            del audio["TPE1"]
            del audio["TALB"]
            audio.save()
            logging.debug(f"Deleted tags for file '{basename}'.")

        audio = ID3(track_path)
    except ID3NoHeaderError:
        audio = ID3()

    changed = []

    if "TIT2" not in audio:
        audio["TIT2"] = TIT2(encoding=3, text=tags["title"])
        changed.append("title")
    if "TPE1" not in audio:
        audio["TPE1"] = TPE1(encoding=3, text=tags["artist"])
        changed.append("artist")
    if "TALB" not in audio:
        audio["TALB"] = TALB(encoding=3, text=tags["album"])
        changed.append("album")

    if changed or FORCE_OVERWRITE:
        audio.save(track_path, v2_version=3)
        logging.debug(
            f"Set tags '{','.join(changed)}' for file '{basename}'.")
    else:
        logging.debug(
            f"No tags set for file '{basename}', existing tags are '{audio.keys()}'.")


def check_and_set_tags(root_path):
    for artist_dir in os.listdir(root_path):
        artist_path = os.path.join(root_path, artist_dir)

        if os.path.isdir(artist_path):
            for album_dir in os.listdir(artist_path):
                album_path = os.path.join(artist_path, album_dir)
                logging.info(f"> Checking directory '{album_path}'...")

                # Tags from directories (artist -> album -> title.mp3)
                if os.path.isdir(album_path):
                    for track_file in os.listdir(album_path):
                        track_path = os.path.join(album_path, track_file)

                        if os.path.isfile(track_path) and track_file.endswith(".mp3"):
                            title = track_file.replace(".mp3", "")

                            change_track_tags(track_path, {
                                "artist": str(artist_dir),
                                "album": str(album_dir),
                                "title": str(title)
                            })
                else:  # Tags from filename (artist -> album - title.mp3)
                    """
                    for track_file in os.listdir(album_path):
                        track_path = os.path.join(album_path, track_file)

                        if os.path.isfile(track_path) and track_file.endswith(".mp3"):
                            base = track_file.replace(".mp3", "")

                            try:
                                album = base.split(" - ")[0]
                                title = base.split(" - ")[1]
                            except:
                                continue

                            change_track_tags(track_path, {
                                "artist": str(artist_dir),
                                "album": str(album),
                                "title": str(title)
                            })
                    """
                    pass


def main_entrypoint():
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
    logging.info("----- START -----")

    for dir in INCLUDED_DIRS:
        if os.path.isdir(os.path.join(SOURCE_PATH_MUSIC, dir)):
            logging.info(f"Checking directory '{dir}'...")
            check_and_set_tags(os.path.join(SOURCE_PATH_MUSIC, dir))
            logging.info("Done!")
        else:
            logging.warning(f"Invalid directory '{dir}'!")

    logging.info("----- END -----")


if __name__ == "__main__":
    main_entrypoint()
