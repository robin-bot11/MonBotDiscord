import discord

COLOR = 0x6b00cb

def get_category_embed(category):
    """
    Retourne un embed pour la catégorie donnée avec toutes ses commandes.
    Chaque catégorie est dans un seul embed pour éviter le scroll.
    """

    embed = discord.Embed(color=COLOR)

    # ---------------- Fun ----------------
    if category.lower() == "fun":
        embed.title = "📂 Fun"
        embed.description = "Commandes amusantes pour votre serveur."
        embed.add_field(name="+8ball <question>", value="Pose une question et le bot répond.", inline=False)
        embed.add_field(name="+meme", value="Envoie un meme aléatoire.", inline=False)
        embed.add_field(name="+say <texte>", value="Le bot répète votre texte.", inline=False)

    # ---------------- Modération ----------------
    elif category.lower() == "modération":
        embed.title = "📂 Modération"
        embed.description = "Commandes pour gérer votre serveur."
        embed.add_field(name="+ban <@membre> [raison]", value="Bannit un membre.", inline=False)
        embed.add_field(name="+kick <@membre> [raison]", value="Expulse un membre.", inline=False)
        embed.add_field(name="+mute <@membre> [raison]", value="Mute un membre.", inline=False)
        embed.add_field(name="+unmute <@membre>", value="Unmute un membre.", inline=False)
        embed.add_field(name="+warn <@membre> [raison]", value="Avertit un membre.", inline=False)
        embed.add_field(name="+infractions <@membre>", value="Affiche les infractions d'un membre.", inline=False)

    # ---------------- Logs ----------------
    elif category.lower() == "logs":
        embed.title = "📂 Logs"
        embed.description = "Configuration des salons de logs."
        embed.add_field(name="+setlog <type> <#salon>", value="Configure le salon pour les logs.\nTypes: role, mod, voice, channel, message, member.", inline=False)

    # ---------------- Owner ----------------
    elif category.lower() == "owner":
        embed.title = "📂 Owner"
        embed.description = "Commandes réservées au propriétaire du bot."
        embed.add_field(name="+shutdown", value="Éteint le bot.", inline=False)
        embed.add_field(name="+poweron", value="Rallume le bot.", inline=False)
        embed.add_field(name="+restart", value="Redémarre le bot.", inline=False)
        embed.add_field(name="+eval <code>", value="Exécute du code Python.", inline=False)
        embed.add_field(name="+purgeall", value="Supprime tous les messages d'un salon.", inline=False)
        embed.add_field(name="+say <texte>", value="Le bot parle dans un salon.", inline=False)
        embed.add_field(name="+status <texte>", value="Change le statut du bot.", inline=False)
        embed.add_field(name="+setprefix <nouveau préfixe>", value="Change le préfixe du bot.", inline=False)
        embed.add_field(name="+backupconfig", value="Sauvegarde la configuration du bot.", inline=False)
        embed.add_field(name="+restoreconfig", value="Restaure la configuration sauvegardée.", inline=False)

    # ---------------- Giveaway ----------------
    elif category.lower() == "giveaway":
        embed.title = "📂 Giveaway"
        embed.description = "Commandes pour gérer les giveaways."
        embed.add_field(name="+gyveaway", value="Lancer un giveaway.", inline=False)
        embed.add_field(name="+gyrole", value="Définir les rôles autorisés à lancer des giveaways.", inline=False)
        embed.add_field(name="+gyend", value="Terminer un giveaway avant l'heure.", inline=False)
        embed.add_field(name="+gyrestart", value="Relancer un giveaway terminé.", inline=False)

    # ---------------- Welcome ----------------
    elif category.lower() == "welcome":
        embed.title = "📂 Bienvenue / Welcome"
        embed.description = "Système de messages de bienvenue."
        embed.add_field(name="+setwelcome <message>", value="Configurer le message de bienvenue.\nVariables autorisées: {user}, {server}, {members}", inline=False)
        embed.add_field(name="+setwelcomechannel <#salon>", value="Configurer le salon pour les messages de bienvenue.", inline=False)

    # ---------------- Message / Channel ----------------
    elif category.lower() == "messagechannel":
        embed.title = "📂 Message & Channel"
        embed.description = "Commandes pour gérer les salons et messages."
        embed.add_field(name="+clear <nombre>", value="Supprime le nombre de messages spécifié.", inline=False)
        embed.add_field(name="+lock <#salon>", value="Verrouille le salon.", inline=False)
        embed.add_field(name="+unlock <#salon>", value="Déverrouille le salon.", inline=False)
        embed.add_field(name="+slowmode <#salon> <secondes>", value="Configure le slowmode.", inline=False)

    # ---------------- Partnership ----------------
    elif category.lower() == "partnership":
        embed.title = "📂 Partenariat"
        embed.description = "Gestion des partenariats sur votre serveur."
        embed.add_field(name="+setpartnerrole <@rôle>", value="Définit le rôle à ping pour un lien d'invitation.\nSeul le propriétaire peut l'utiliser.", inline=False)
        embed.add_field(name="+setpartnerchannel <#salon>", value="Configure le salon où les liens d'invitation seront détectés.", inline=False)
        embed.add_field(name="Détection automatique", value="Lorsqu'un lien Discord est posté, le rôle configuré est mentionné automatiquement.", inline=False)

    # ---------------- Policy / Règlement ----------------
    elif category.lower() == "policy":
        embed.title = "📂 Règlement / Policy"
        embed.description = "Gestion du règlement avec embed et bouton."
        embed.add_field(name="+reglement", value="Assistant pour configurer le règlement étape par étape.", inline=False)
        embed.add_field(name="+showreglement", value="Affiche le règlement avec le bouton d'acceptation.", inline=False)
        embed.add_field(name="Gestion rôles supprimés", value="Prévient automatiquement le propriétaire et le salon si le rôle lié au règlement est supprimé.", inline=False)

    # ---------------- Snipe ----------------
    elif category.lower() == "snipe":
        embed.title = "📂 Snipe"
        embed.description = "Affiche les messages supprimés dans les salons."
        embed.add_field(name="+snipe", value="Affiche le dernier message supprimé dans le salon.", inline=False)
        embed.add_field(name="Listener automatique", value="Chaque message supprimé est automatiquement sauvegardé.", inline=False)

    # ---------------- Catégorie non trouvée ----------------
    else:
        embed.title = "❌ Catégorie inconnue"
        embed.description = f"Aucune commande trouvée pour `{category}`."

    return embed
