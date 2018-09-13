from outils import Outils


class Resumes(object):
    """
    Classe pour la création et la modification des résumés statistiques mensuels
    """

    fichiers = ["bilan", "bilan-comptes", "detail", "cae", "lvr", "res"]
    positions = [3, 3, 2, 7, 7, 7]

    @staticmethod
    def base(edition, dossier_source, dossier_destination):
        """
        création des résumés statistiques mensuels
        :param edition: paramètres d'édition
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """
        for fichier in Resumes.fichiers:
            fichier_complet = fichier + "_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois)
            dossier_destination.ecrire(fichier_complet + ".csv", dossier_source.lire(fichier_complet + "_0.csv"))
        ticket_complet = "ticket_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois)
        ticket_texte = dossier_source.string_lire(ticket_complet + "_0.html")
        ticket_texte = ticket_texte.replace("..", ".")
        dossier_destination.string_ecrire(ticket_complet + ".html", ticket_texte)

    @staticmethod
    def mise_a_jour(edition, clients, dossier_source, dossier_destination, maj, f_html_sections):
        """
        modification des résumés mensuels au niveau du client dont la facture est modifiée 
        :param edition: paramètres d'édition
        :param clients: clients importés
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param maj: données modifiées pour le client pour les différents fichiers
        :param f_html_sections: section html modifiée pour le client
        """
        if len(maj) != len(Resumes.fichiers):
            info = "Résumés : erreur taille tableau"
            Outils.affiche_message(info)
            return

        for i in range(len(Resumes.fichiers)):
            fichier_complet = Resumes.fichiers[i] + "_" + str(edition.annee) + "_" + \
                              Outils.mois_string(edition.mois) + ".csv"
            donnees_csv = Resumes.ouvrir_csv_sans_client(
                dossier_source, fichier_complet, edition.client_unique, Resumes.positions[i])
            with dossier_destination.writer(fichier_complet) as fichier_writer:
                for ligne in donnees_csv:
                    fichier_writer.writerow(ligne)
                for ligne in maj[i]:
                    fichier_writer.writerow(ligne)

        ticket_complet = "ticket_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".html"
        section = list(f_html_sections.values())[0]
        nom_client = clients.donnees[edition.client_unique]['abrev_labo'] + " (" + edition.client_unique + ")"
        Resumes.maj_ticket(dossier_source, dossier_destination, ticket_complet, section, edition.client_unique,
                           nom_client)

    @staticmethod
    def maj_ticket(dossier_source, dossier_destination, nom_fichier, section, code, nom_client):
        """
        mise à jour (ou en cas d'annulation) du ticket html concernant le client modifié
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param nom_fichier: nom de fichier du ticket résumé
        :param section: section du client à mettre à jour
        :param code: code du client à mettre à jour
        :param nom_client: nom pour le menu du client
        """
        ticket_texte = dossier_source.string_lire(nom_fichier)
        index1, index2, clients_liste = Resumes.select_clients(ticket_texte)
        client_present = False
        for nom in clients_liste:
            if code in nom:
                client_present = True
                break

        if client_present:
            index1, index2 = Resumes.section_position(ticket_texte, code)
            if index1 is not None:
                texte = ticket_texte[:index1] + section + ticket_texte[index2:]
                texte = texte.replace("..", ".")
                dossier_destination.string_ecrire(nom_fichier, texte)
        else:
            clients_liste.append(nom_client)
            clients_liste = sorted(clients_liste)
            position = -1
            if index1 is not None:
                nouveau_select = r'''<select name="client" onchange="changeClient(this)">'''
                i = 0
                for nom in clients_liste:
                    if code in nom:
                        position = i
                    nouveau_select += r'''<option value="''' + str(i) + r'''">''' + str(nom) + r'''</option>'''
                    i += 1
                nouveau_select += r'''</select>'''
                texte = ticket_texte[:index1] + nouveau_select + ticket_texte[index2:]

                if position > -1:
                    index1 = clients_liste[position+1].find('(')
                    if index1 > -1:
                        index2 = clients_liste[position+1].find(')', index1)
                        if index2 > -1:
                            client_suivant = clients_liste[position+1][(index1+1):index2]
                            index1, index2 = Resumes.section_position(texte, client_suivant)
                            if index1 is not None:
                                texte = texte[:index1] + section + texte[index1:]
                                texte = texte.replace("..", ".")
                                dossier_destination.string_ecrire(nom_fichier, texte)

    @staticmethod
    def suppression(suppression, dossier_source, dossier_destination):
        """
        suppression des résumés mensuels au niveau du client dont la facture est supprimée
        :param suppression: paramètres de suppression
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """

        Resumes.supprimmer(suppression.client_unique, suppression.mois, suppression.annee, dossier_source,
                           dossier_destination)

    @staticmethod
    def supprimmer(client_unique, mois, annee, dossier_source, dossier_destination):
        """
        suppression des résumés mensuels au niveau du client
        :param client_unique: client concerné
        :param mois: mois concerné
        :param annee: année concernée
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """

        for i in range(len(Resumes.fichiers)):
            fichier_complet = Resumes.fichiers[i] + "_" + str(annee) + "_" + Outils.mois_string(mois) + ".csv"
            donnees_csv = Resumes.ouvrir_csv_sans_client(
                dossier_source, fichier_complet, client_unique, Resumes.positions[i])
            with dossier_destination.writer(fichier_complet) as fichier_writer:
                for ligne in donnees_csv:
                    fichier_writer.writerow(ligne)

        ticket_complet = "ticket_" + str(annee) + "_" + Outils.mois_string(mois) + ".html"
        ticket_texte = dossier_source.string_lire(ticket_complet)
        index1, index2 = Resumes.section_position(ticket_texte, client_unique)
        if index1 is not None:
            ticket_texte = ticket_texte[:index1] + ticket_texte[index2:]
            ticket_texte = ticket_texte.replace("..", ".")

        index1, index2, clients_liste = Resumes.select_clients(ticket_texte)
        if index1 is not None:
            nouveau_select = r'''<select name="client" onchange="changeClient(this)">'''
            i = 0
            for nom in clients_liste:
                if client_unique not in nom:
                    nouveau_select += r'''<option value="''' + str(i) + r'''">''' + \
                                      str(nom) + r'''</option>'''
                    i += 1
            nouveau_select += r'''</select>'''
            texte = ticket_texte[:index1] + nouveau_select + ticket_texte[index2:]
            texte = texte.replace("..", ".")
            dossier_destination.string_ecrire(ticket_complet, texte)

    @staticmethod
    def annulation_suppression(annulsuppr, dossier_source, dossier_destination, dossier_source_backup):
        """
        annulation de modification des résumés mensuels au niveau du client dont la facture est supprimée
        :param annulsuppr: paramètres d'annulation de suppression
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param dossier_source_backup: Une instance de la classe dossier.DossierSource pour récupérer les
                                        données à remettre
        """

        if annulsuppr.version == 0:
            suffixe = "_0"
        else:
            suffixe = "_" + str(annulsuppr.version) + "_" + annulsuppr.client_unique

        Resumes.annuler(suffixe, annulsuppr.client_unique, annulsuppr.mois, annulsuppr.annee, dossier_source,
                        dossier_destination, dossier_source_backup)

    @staticmethod
    def annulation(annulation, dossier_source, dossier_destination, dossier_source_backup):
        """
        annulation de modification des résumés mensuels au niveau du client dont la facture est supprimée 
        :param annulation: paramètres d'annulation
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param dossier_source_backup: Une instance de la classe dossier.DossierSource pour récupérer les 
                                        données à remettre
        """
        if annulation.recharge_version == 0:
            suffixe = "_0"
        else:
            suffixe = "_" + str(annulation.recharge_version) + "_" + annulation.client_unique

        Resumes.annuler(suffixe, annulation.client_unique, annulation.mois, annulation.annee, dossier_source,
                        dossier_destination, dossier_source_backup)

    @staticmethod
    def annuler(suffixe, client_unique, mois, annee, dossier_source, dossier_destination, dossier_source_backup):
        """
        annulation de modification des résumés mensuels au niveau du client dont la facture est supprimée
        :param suffixe: suffixe dossier version
        :param client_unique: client concerné
        :param mois: mois concerné
        :param annee: année concernée
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param dossier_source_backup: Une instance de la classe dossier.DossierSource pour récupérer les
                                        données à remettre
        """
        for i in range(len(Resumes.fichiers)):
            fichier_backup = Resumes.fichiers[i] + "_" + str(annee) + "_" + Outils.mois_string(mois) + suffixe + ".csv"
            donnees_backup = Resumes.ouvrir_csv_seulement_client(
                dossier_source_backup, fichier_backup, client_unique, Resumes.positions[i])

            fichier_complet = Resumes.fichiers[i] + "_" + str(annee) + "_" + Outils.mois_string(mois) + ".csv"
            donnees_csv = Resumes.ouvrir_csv_sans_client(
                dossier_source, fichier_complet, client_unique, Resumes.positions[i])
            with dossier_destination.writer(fichier_complet) as fichier_writer:
                for ligne in donnees_csv:
                    fichier_writer.writerow(ligne)
                for ligne in donnees_backup:
                    fichier_writer.writerow(ligne)

        ticket_backup = "ticket_" + str(annee) + "_" + Outils.mois_string(mois) + suffixe + ".html"
        ticket_backup_texte = dossier_source_backup.string_lire(ticket_backup)
        index1, index2 = Resumes.section_position(ticket_backup_texte, client_unique)
        section = ""
        if index1 is not None:
            section = ticket_backup_texte[index1:index2]

        nom_client = ""
        index1, index2, clients_liste_backup = Resumes.select_clients(ticket_backup_texte)
        for nom in clients_liste_backup:
            if client_unique in nom:
                nom_client = nom
                break
        ticket_complet = "ticket_" + str(annee) + "_" + Outils.mois_string(mois) + ".html"

        Resumes.maj_ticket(dossier_source, dossier_destination, ticket_complet, section, client_unique, nom_client)

    @staticmethod
    def ouvrir_csv_sans_client(dossier_source, fichier, code_client, position_code):
        """
        ouverture d'un csv comme string sans les données d'un client donné
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param fichier: nom du fichier csv
        :param code_client: code du client à ignorer
        :param position_code: position colonne du code client dans le csv
        :return: donnees du csv modifiées en tant que string
        """
        donnees_csv = []
        try:
            fichier_reader = dossier_source.reader(fichier)
            for ligne in fichier_reader:
                if ligne == -1:
                    continue
                if ligne[position_code] != code_client:
                    donnees_csv.append(ligne)
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : " + fichier)
        return donnees_csv

    @staticmethod
    def ouvrir_csv_seulement_client(dossier_source, fichier, code_client, position_code):
        """
        ouverture d'un csv comme string seulement pour les données d'un client donné
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param fichier: nom du fichier csv
        :param code_client: code du client à prendre en compte
        :param position_code: position colonne du code client dans le csv
        :return: donnees du csv modifiées en tant que string
        """
        donnees_csv = []
        try:
            fichier_reader = dossier_source.reader(fichier)
            for ligne in fichier_reader:
                if ligne == -1:
                    continue
                if ligne[position_code] == code_client:
                    donnees_csv.append(ligne)
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : " + fichier)
        return donnees_csv

    @staticmethod
    def section_position(texte, code_client):
        """
        retrouve la section html concernant le client
        :param texte: le texte html dans lequel on cherche
        :param code_client: code du client dont on cherche la section
        :return: le début de la section, et le début de la suite
        """
        index1 = texte.find('<section id="' + code_client + '">')
        index2 = texte.find('</section>', index1)
        taille = 10
        if index1 > -1:
            if index2 > -1:
                return index1, index2 + taille
            else:
                info = "Fin de section non trouvée"
                print(info)
                return None, None
        else:
            info = "Section attendue non trouvée"
            print(info)
            return None, None

    @staticmethod
    def select_clients(texte):
        """
        récupère le select des clients du html
        :param texte: le texte html dans lequel on cherche
        :return: le début du select, et le début de la suite, la liste des clients dans le select
        """
        index1 = texte.find('<select name="client"')
        if index1 > -1:
            index2 = texte.find('</select>', index1)
            if index2 > -1:
                select_texte = texte[index1:index2+9]
                clients_liste = []
                ind = select_texte.find('</option>')
                while -1 < ind < len(select_texte):
                    ind2 = select_texte.rfind('>', 0, ind)
                    if ind2 > -1:
                        part = select_texte[ind2+1:ind]
                        clients_liste.append(part)
                    ind = select_texte.find('</option>', ind+5)
                return index1, index2 + 9, clients_liste
            else:
                info = "Fin de select non trouvée"
                print(info)
                return None, None, None
        else:
            info = "Select attendu non trouvé"
            print(info)
            return None, None, None
