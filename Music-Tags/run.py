import os
import logging
from mutagen.easyid3 import EasyID3

SOURCE_PATH_MUSIC = str(os.environ["SOURCE_PATH_MUSIC"])
INCLUDED_DIRS = str(os.environ["INCLUDED_DIRS"]).split(",")


def check_and_set_tags(root_path):
    for artist_dir in os.listdir(root_path):
        artist_path = os.path.join(root_path, artist_dir)

        if os.path.isdir(artist_path):
            for album_dir in os.listdir(artist_path):
                album_path = os.path.join(artist_path, album_dir)

                if os.path.isdir(album_path):
                    for track_file in os.listdir(album_path):
                        track_path = os.path.join(album_path, track_file)

                        if os.path.isfile(track_path) and track_file.endswith(".mp3"):
                            title = track_file.replace(".mp3", "")
                            audio = EasyID3(track_path)
                            changed = []

                            if "artist" not in audio.keys():
                                audio["artist"] = str(artist_dir)
                                changed.append("artist")
                            if "album" not in audio.keys():
                                audio["album"] = str(album_dir)
                                changed.append("album")
                            if "title" not in audio.keys():
                                audio["title"] = str(title)
                                changed.append("title")

                            if changed:
                                audio.save()
                                logging.info(
                                    f"Set tags '{','.join(changed)}' for file '{track_path}'.")
                            else:
                                logging.info(
                                    f"No tags set for file '{track_path}'.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("----- START -----")

    for dir in INCLUDED_DIRS:
        if os.path.isdir(os.path.join(SOURCE_PATH_MUSIC, dir)):
            logging.info(f"Checking directory '{dir}'...")
            check_and_set_tags(os.path.join(SOURCE_PATH_MUSIC, dir))
            logging.info("Done!")
        else:
            logging.warning(f"Invalid directory '{dir}'!")

    logging.info("----- END -----")
