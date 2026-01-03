import json
import os
import shutil
import time

DB_FILE = "database.json"
SNIPE_EXPIRATION = 86400  # 24 heures en secondes

class Database:
    def __init__(self):
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "warns": {},
                    "welcome": {},
                    "verification": {},
                    "gyroles": {},
                    "lock_roles": {},
                    "rules": {},
                    "snipes": {},
                    "partner": {},
                    "logs": {}
                }, f, indent=4, ensure_ascii=False)
        self.load()

    # ------------------ Load / Save ------------------
    def load(self):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ------------------ Backup / Restore ------------------
    def backup(self):
        shutil.copy(DB_FILE, "backup.json")
        print("✅ Base de données sauvegardée")

    def restore(self):
        if os.path.exists("backup.json"):
            shutil.copy("backup.json", DB_FILE)
            self.load()
            print("✅ Base de données restaurée")

    # ------------------ Warns ------------------
    def add_warn(self, guild_id, member_id, reason, staff, date):
        self.data.setdefault("warns", {})
        self.data["warns"].setdefault(str(guild_id), {})
        self.data["warns"][str(guild_id)].setdefault(str(member_id), [])
        self.data["warns"][str(guild_id)][str(member_id)].append({
            "reason": reason,
            "staff": staff,
            "date": date
        })
        self.save()

    def get_warns(self, guild_id, member_id):
        return self.data.get("warns", {}).get(str(guild_id), {}).get(str(member_id), [])

    def del_warn(self, guild_id, member_id, index):
        guild_warns = self.data.get("warns", {}).get(str(guild_id), {})
        if str(member_id) in guild_warns:
            if 0 <= index < len(guild_warns[str(member_id)]):
                del guild_warns[str(member_id)][index]
                self.save()
                return True
        return False

    # ------------------ Welcome ------------------
    def set_welcome(self, guild_id, channel_id=None, message=None, embed_data=None, enabled=True):
        self.data.setdefault("welcome", {})
        self.data["welcome"][str(guild_id)] = {
            "channel": channel_id,
            "message": message,
            "embed": embed_data,
            "enabled": enabled
        }
        self.save()

    def toggle_welcome(self, guild_id):
        guild_data = self.data.get("welcome", {}).get(str(guild_id))
        if guild_data:
            guild_data["enabled"] = not guild_data.get("enabled", True)
            self.data["welcome"][str(guild_id)] = guild_data
            self.save()
            return guild_data["enabled"]
        return None

    def get_welcome(self, guild_id):
        return self.data.get("welcome", {}).get(str(guild_id), {})

    # ------------------ Verification ------------------
    def set_verification(
        self,
        guild_id,
        role_valid,
        isolation_role=None,
        title=None,
        description=None,
        button_text=None,
        message_id=None,
        emoji=None
    ):
        self.data.setdefault("verification", {})
        self.data["verification"][str(guild_id)] = {
            "role_valid": role_valid,
            "isolation_role": isolation_role,
            "title": title,
            "description": description,
            "button_text": button_text,
            "message_id": message_id,
            "emoji": emoji,
            "tries": {}
        }
        self.save()

    def get_verification(self, guild_id):
        return self.data.get("verification", {}).get(str(guild_id), {})

    def add_try(self, guild_id, member_id):
        self.data.setdefault("verification", {})
        self.data["verification"].setdefault(str(guild_id), {})
        self.data["verification"][str(guild_id)].setdefault("tries", {})
        tries = self.data["verification"][str(guild_id)]["tries"].get(str(member_id), 0) + 1
        self.data["verification"][str(guild_id)]["tries"][str(member_id)] = tries
        self.save()
        return tries

    def reset_tries(self, guild_id, member_id):
        self.data.setdefault("verification", {})
        self.data["verification"].setdefault(str(guild_id), {})
        self.data["verification"][str(guild_id)]["tries"][str(member_id)] = 0
        self.save()

    # ------------------ Partner ------------------
    def set_partner_role(self, guild_id, role_id):
        self.data.setdefault("partner", {})
        self.data["partner"].setdefault(str(guild_id), {})
        self.data["partner"][str(guild_id)]["role"] = role_id
        self.save()

    def get_partner_role(self, guild_id):
        return self.data.get("partner", {}).get(str(guild_id), {}).get("role")

    def set_partner_channel(self, guild_id, channel_id):
        self.data.setdefault("partner", {})
        self.data["partner"].setdefault(str(guild_id), {})
        self.data["partner"][str(guild_id)]["channel"] = channel_id
        self.save()

    def get_partner_channel(self, guild_id):
        return self.data.get("partner", {}).get(str(guild_id), {}).get("channel")

    # ------------------ Snipes ------------------
    def set_snipe(self, channel_id, data):
        """Enregistre un snipe et écrase l'ancien"""
        self.data.setdefault("snipes", {})
        self.data["snipes"][str(channel_id)] = {
            "author": data["author"],
            "content": data["content"],
            "timestamp": int(time.time())
        }
        self.save()

    def get_snipe(self, channel_id):
        """Récupère le snipe si valide, sinon None"""
        snipes = self.data.get("snipes", {})
        snipe = snipes.get(str(channel_id))

        if not snipe:
            return None

        # Vérifie expiration
        if int(time.time()) - snipe["timestamp"] > SNIPE_EXPIRATION:
            del self.data["snipes"][str(channel_id)]
            self.save()
            return None

        return snipe

    def clear_all_snipes(self):
        """Supprime tous les snipes globaux"""
        self.data["snipes"] = {}
        self.save()

    def clear_guild_snipes(self, guild):
        """Supprime tous les snipes du serveur"""
        self.data.setdefault("snipes", {})
        for channel in guild.text_channels:
            self.data["snipes"].pop(str(channel.id), None)
        self.save()
