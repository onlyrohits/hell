import json
import os
import lockfile


class RapidaLockManager:
    DIR_PATH = os.path.expanduser("~/.rapida")
    LOCKFILE_PATH = os.path.join(DIR_PATH, "custom_properties.json.lock")
    JSON_PATH = os.path.join(DIR_PATH, "custom_properties.json")

    @staticmethod
    def check_files():
        os.makedirs(RapidaLockManager.DIR_PATH, exist_ok=True)
        with lockfile.LockFile(RapidaLockManager.LOCKFILE_PATH):
            if not os.path.exists(RapidaLockManager.JSON_PATH):
                with open(RapidaLockManager.JSON_PATH, 'w') as json_file:
                    json.dump({}, json_file)

    @staticmethod
    def write_custom_property(property_name, value):
        RapidaLockManager.check_files()
        with lockfile.LockFile(RapidaLockManager.LOCKFILE_PATH):
            with open(RapidaLockManager.JSON_PATH, "r") as json_file:
                properties = json.load(json_file)

            properties[property_name] = value

            with open(RapidaLockManager.JSON_PATH, "w") as json_file:
                json.dump(properties, json_file)

    @staticmethod
    def clear_all_properties():
        RapidaLockManager.check_files()
        with lockfile.LockFile(RapidaLockManager.LOCKFILE_PATH):
            with open(RapidaLockManager.JSON_PATH, "w") as json_file:
                json.dump({}, json_file)

    @staticmethod
    def remove_custom_property(property_name):
        RapidaLockManager.check_files()
        with lockfile.LockFile(RapidaLockManager.LOCKFILE_PATH):
            with open(RapidaLockManager.JSON_PATH, "r") as json_file:
                properties = json.load(json_file)

            if property_name in properties:
                del properties[property_name]

                with open(RapidaLockManager.JSON_PATH, "w") as json_file:
                    json.dump(properties, json_file)


RapidaLockManager.check_files()
