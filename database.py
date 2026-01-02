import json
import os
import shutil

DB_FILE = "database.json"

class Database:
    def __init__(self):
        # Création du fichier s'il n'existe pas
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "warns": {},
                    "welcome": {},
                    "gyroles": [],
                    "lock_roles": {},
                    "rules": {},
                    "snipes": {},
                    "partner": {},
                    "logs": {}  # Nouvelle section pour les logs
                }, f, indent=4, ensure_ascii=False)
        self.load()

    # ------------------ Chargement et sauvegarde ------------------
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
    def add_warn(self, member_id, reason, staff, date):
        self.data["warns"].setdefault(str(member_id), [])
        self.data["warns"][str(member_id)].append({
            "reason": reason,
            "staff": staff,
            "date": date
        })
        self.save()

    def get_warns(self, member_id):
        return self.data["warns"].get(str(member_id), [])

    def del_warn(self, member_id, index):
        if str(member_id) in self.data["warns"]:
            if 0 <= index < len(self.data["warns"][str(member_id)]):
                del self.data["warns"][str(member_id)][index]
                self.save()
                return True
        return False

    # ------------------ Welcome ------------------
    def set_welcome_message(self, guild_id, message):
        self.data["welcome"].setdefault(str(guild_id), {})
        self.data["welcome"][str(guild_id)]["message"] = message
        self.save()

    def set_welcome_channel(self, guild_id, channel_id):
        self.data["welcome"].setdefault(str(guild_id), {})
        self.data["welcome"][str(guild_id)]["channel"] = channel_id
        self.save()

    def get_welcome(self, guild_id):
        return self.data["welcome"].get(str(guild_id), {})

    # ------------------ Giveaway roles ------------------
    def add_gyrole(self, role_id):
        if role_id not in self.data["gyroles"]:
            self.data["gyroles"].append(role_id)
            self.save()

    def remove_gyrole(self, role_id):
        if role_id in self.data["gyroles"]:
            self.data["gyroles"].remove(role_id)
            self.save()

    def get_gyroles(self):
        return self.data["gyroles"]

    # ------------------ Lock roles ------------------
    def set_lock_roles(self, guild_id, roles):
        self.data["lock_roles"][str(guild_id)] = roles
        self.save()

    def get_lock_roles(self, guild_id):
        return self.data["lock_roles"].get(str(guild_id), [])

    # ------------------ Règlement ------------------
    def set_rule(self, guild_id, title, text, role_id, button_text, emoji):
        self.data["rules"][str(guild_id)] = {
            "title": title,
            "text": text,
            "role": role_id,
            "button": button_text,
            "emoji": emoji
        }
        self.save()

    def get_rule(self, guild_id):
        return self.data["rules"].get(str(guild_id), {})

    # ------------------ Snipes ------------------
    def set_snipe(self, channel_id, message):
        self.data["snipes"][str(channel_id)] = message
        self.save()

    def get_snipe(self, channel_id):
        return self.data["snipes"].get(str(channel_id))

    # ------------------ Partenariat ------------------
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

    # ------------------ Logs ------------------
    def set_log_channel(self, guild_id, log_type, channel_id):
        self.data.setdefault("logs", {})
        self.data["logs"].setdefault(str(guild_id), {})
        self.data["logs"][str(guild_id)][log_type] = channel_id
        self.save()

    def get_log_channel(self, guild_id, log_type):
        return self.data.get("logs", {}).get(str(guild_id), {}).get(log_type)
