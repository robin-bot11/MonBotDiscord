# database.py
import json
import os
import shutil

DB_FILE = "database.json"
BACKUP_FILE = "database_backup.json"

class Database:
    def __init__(self):
        # Crée le fichier si il n'existe pas
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "warns": {},
                    "welcome": {},
                    "gyroles": [],
                    "lock_roles": {},
                    "rules": {},
                    "snipes": {}
                }, f, indent=4)
        self.load()

    # --- Chargement et sauvegarde ---
    def load(self):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # --- Backup / Restore ---
    def backup(self):
        """Créer une copie du fichier de base de données"""
        shutil.copy(DB_FILE, BACKUP_FILE)

    def restore(self):
        """Restaurer la base de données depuis le backup"""
        if os.path.exists(BACKUP_FILE):
            shutil.copy(BACKUP_FILE, DB_FILE)
            self.load()
            return True
        return False

    # --- Warns ---
    def add_warn(self, member_id, reason, staff, date):
        self.data.setdefault("warns", {}).setdefault(str(member_id), []).append({
            "reason": reason,
            "staff": staff,
            "date": date
        })
        self.save()

    def get_warns(self, member_id):
        return self.data.get("warns", {}).get(str(member_id), [])

    def del_warn(self, member_id, index):
        if str(member_id) in self.data.get("warns", {}):
            if 0 <= index < len(self.data["warns"][str(member_id)]):
                del self.data["warns"][str(member_id)][index]
                self.save()
                return True
        return False

    # --- Welcome ---
    def set_welcome_message(self, guild_id, message):
        self.data.setdefault("welcome", {}).setdefault(str(guild_id), {})["message"] = message
        self.save()

    def set_welcome_channel(self, guild_id, channel_id):
        self.data.setdefault("welcome", {}).setdefault(str(guild_id), {})["channel"] = channel_id
        self.save()

    def get_welcome(self, guild_id):
        return self.data.get("welcome", {}).get(str(guild_id), {})

    # --- Giveaway roles ---
    def add_gyrole(self, role_id):
        if role_id not in self.data.get("gyroles", []):
            self.data["gyroles"].append(role_id)
            self.save()

    def remove_gyrole(self, role_id):
        if role_id in self.data.get("gyroles", []):
            self.data["gyroles"].remove(role_id)
            self.save()

    def get_gyroles(self):
        return self.data.get("gyroles", [])

    # --- Lock roles ---
    def set_lock_roles(self, guild_id, roles):
        self.data.setdefault("lock_roles", {})[str(guild_id)] = roles
        self.save()

    def get_lock_roles(self, guild_id):
        return self.data.get("lock_roles", {}).get(str(guild_id), [])

    # --- Règlement ---
    def set_rule(self, guild_id, title, text, role_id, button_text, emoji):
        self.data.setdefault("rules", {})[str(guild_id)] = {
            "title": title,
            "text": text,
            "role": role_id,
            "button": button_text,
            "emoji": emoji
        }
        self.save()

    def get_rule(self, guild_id):
        return self.data.get("rules", {}).get(str(guild_id), {})

    # --- Snipes ---
    def set_snipe(self, channel_id, message):
        self.data.setdefault("snipes", {})[str(channel_id)] = message
        self.save()

    def get_snipe(self, channel_id):
        return self.data.get("snipes", {}).get(str(channel_id))
