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
                    "gyroles": {},
                    "lock_roles": {},
                    "rules": {},
                    "snipes": {},
                    "partner": {},
                    "logs": {}
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
    def set_welcome_message(self, guild_id, message):
        self.data.setdefault("welcome", {})
        self.data["welcome"].setdefault(str(guild_id), {})
        self.data["welcome"][str(guild_id)]["message"] = message
        self.save()

    def set_welcome_channel(self, guild_id, channel_id):
        self.data.setdefault("welcome", {})
        self.data["welcome"].setdefault(str(guild_id), {})
        self.data["welcome"][str(guild_id)]["channel"] = channel_id
        self.save()

    def get_welcome(self, guild_id):
        return self.data.get("welcome", {}).get(str(guild_id), {})

    # ------------------ Giveaway roles (isolés par serveur) ------------------
    def add_gyrole(self, guild_id, role_id):
        self.data.setdefault("gyroles", {})
        self.data["gyroles"].setdefault(str(guild_id), [])
        if role_id not in self.data["gyroles"][str(guild_id)]:
            self.data["gyroles"][str(guild_id)].append(role_id)
            self.save()

    def remove_gyrole(self, guild_id, role_id):
        if str(guild_id) in self.data.get("gyroles", {}):
            if role_id in self.data["gyroles"][str(guild_id)]:
                self.data["gyroles"][str(guild_id)].remove(role_id)
                self.save()

    def get_gyroles(self, guild_id):
        return self.data.get("gyroles", {}).get(str(guild_id), [])

    # ------------------ Lock roles ------------------
    def set_lock_roles(self, guild_id, roles):
        self.data.setdefault("lock_roles", {})
        self.data["lock_roles"][str(guild_id)] = roles
        self.save()

    def get_lock_roles(self, guild_id):
        return self.data.get("lock_roles", {}).get(str(guild_id), [])

    # ------------------ Règlement ------------------
    def set_rule(self, guild_id, title, text, role_id, button_text, emoji, image=None):
        self.data.setdefault("rules", {})
        self.data["rules"][str(guild_id)] = {
            "title": title,
            "text": text,
            "role": role_id,
            "button": button_text,
            "emoji": emoji,
            "image": image
        }
        self.save()

    def get_rule(self, guild_id):
        return self.data.get("rules", {}).get(str(guild_id), {})

    # ------------------ Snipes ------------------
    def set_snipe(self, channel_id, message):
        self.data.setdefault("snipes", {})
        self.data["snipes"][str(channel_id)] = message
        self.save()

    def get_snipe(self, channel_id):
        return self.data.get("snipes", {}).get(str(channel_id))

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
