# database.py
import json
import os
from copy import deepcopy

class Database:
    def __init__(self, file_path="database.json"):
        self.file_path = file_path
        self.data = {
            "warns": {},
            "config": {}
        }
        self._load()

    # ------------------ LOAD ------------------
    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                print("Erreur chargement database.json, création d'une base neuve")
                self._save()
        else:
            self._save()

    # ------------------ SAVE ------------------
    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ------------------ WARNS ------------------
    def add_warn(self, guild_id, user_id, reason):
        guild_id = str(guild_id)
        user_id = str(user_id)

        self.data["warns"].setdefault(guild_id, {})
        self.data["warns"][guild_id].setdefault(user_id, [])

        self.data["warns"][guild_id][user_id].append(reason)
        self._save()

    def get_warns(self, guild_id, user_id):
        return self.data["warns"].get(str(guild_id), {}).get(str(user_id), [])

    def clear_warns(self, guild_id, user_id):
        guild_id = str(guild_id)
        user_id = str(user_id)

        if guild_id in self.data["warns"]:
            self.data["warns"][guild_id].pop(user_id, None)
            self._save()

    # ------------------ CONFIG ------------------
    def set_config(self, guild_id, key, value):
        guild_id = str(guild_id)
        self.data["config"].setdefault(guild_id, {})
        self.data["config"][guild_id][key] = value
        self._save()

    def get_config(self, guild_id, key, default=None):
        return self.data["config"].get(str(guild_id), {}).get(key, default)

    # ------------------ BACKUP ------------------
    def backup(self):
        with open("backup.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ------------------ RESTORE ------------------
    def restore(self):
        if not os.path.exists("backup.json"):
            raise FileNotFoundError("Aucune sauvegarde trouvée")

        with open("backup.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self._save()
