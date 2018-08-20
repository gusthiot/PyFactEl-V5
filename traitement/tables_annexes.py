from outils import Outils
from latex import Latex


class TablesAnnexes(object):

    @staticmethod
    def table_tps_res_xmu(code_client, reservations, machines, users):
        """
        Tps RES X/M/U - Table Client Détail Temps Réservations/Machine/User
        :param code_client: code du client concerné
        :param reservations: réservations importées
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """

        if code_client in reservations.sommes:
            structure = r'''{|c|c|c|c|c|}'''
            legende = r'''Détail des réservations machines par utilisateur'''
            contenu = r'''
                \cline{4-5}
                \multicolumn{3}{c}{} & \multicolumn{2}{|c|}{Durée réservée} \\
                \cline{4-5}
                \multicolumn{3}{c|}{} & HP & HC \\
                \hline
                '''

            somme = reservations.sommes[code_client]

            machines_reservees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_reservees.items()):
                for nom_machine, id_machine in sorted(mics.items()):

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'hp': Outils.format_heure(somme[id_machine]['res_hp']),
                                    'hc': Outils.format_heure(somme[id_machine]['res_hc'])}
                    contenu += r'''
                            \multicolumn{3}{|l|}{\textbf{%(machine)s}} & \hspace{5mm} %(hp)s &
                            \hspace{5mm} %(hc)s \\
                            \hline
                            ''' % dico_machine

                    utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                smu = somme[id_machine]['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'hp': Outils.format_heure(smu['res_hp']),
                                             'hc': Outils.format_heure(smu['res_hc'])}
                                contenu += r'''
                                        \multicolumn{3}{|l|}{\hspace{5mm} %(user)s} & %(hp)s & %(hc)s \\
                                        \hline
                                        ''' % dico_user
                                for p1 in smu['data']:
                                    res = reservations.donnees[p1]
                                    login = Latex.echappe_caracteres(res['date_debut']).split()
                                    temps = login[0].split('-')
                                    date = temps[0]
                                    for p2 in range(1, len(temps)):
                                        date = temps[p2] + '.' + date
                                    if len(login) > 1:
                                        heure = login[1]
                                    else:
                                        heure = ""

                                    sup = ""
                                    if res['date_suppression'] != "":
                                        sup = "Supprimé le : " + res['date_suppression']
                                    dico_pos = {'date': date, 'heure': heure, 'sup': Latex.echappe_caracteres(sup),
                                                'hp': Outils.format_heure(res['duree_fact_hp']),
                                                'hc': Outils.format_heure(res['duree_fact_hc'])}
                                    contenu += r'''
                                                \hspace{10mm} %(date)s & %(heure)s & %(sup)s & %(hp)s \hspace{5mm} &
                                                 %(hc)s \hspace{5mm} \\
                                                \hline
                                            ''' % dico_pos

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_tps_m_cae_xmu(code_client, acces, contenu_cae_xmu):
        """
        Tps_M CAE X/M/U - Table Client Récap Temps mach avec pénalités /Machine/User
        :param code_client: code du client concerné
        :param acces: accès importés
        :param contenu_cae_xmu: contenu généré pour cette table
        :return: table au format latex
        """

        if code_client in acces.sommes and contenu_cae_xmu != "":
            structure = r'''{|l|c|c|}'''
            legende = r'''Récapitulatif des utilisations machines par utilisateur'''
            contenu = r'''
                \cline{2-3}
                \multicolumn{1}{c|}{} & HP & HC \\
                \hline'''

            contenu += contenu_cae_xmu

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_tps_penares_xmu(code_client, scl, sommes_acces, sommes_reservations, machines, users):
        """
        Tps Penares X/M/U - Table Client Durées Pénalités réserv./Machine/User
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces: sommes des accès importés
        :param sommes_reservations: sommes des réservations importées
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """

        if code_client in sommes_reservations:
            structure = r'''{|l|c|c|c|c|c|c|}'''
            legende = r'''Statistiques des réservations et des utilisations machines'''
            contenu = r'''
                \cline{3-7}
                \multicolumn{2}{c}{} & \multicolumn{3}{|c|}{Réservation} & Utilisation & Pénalités \\
                \hline
                 & & Durée & Taux & Util. Min. & Durée & Durée \\
                \hline'''

            ac_somme = None
            if code_client in sommes_acces:
                ac_somme = sommes_acces[code_client]['machines']

            machines_utilisees = Outils.machines_in_somme(scl['res'], machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    re_hp = sommes_reservations[code_client][id_machine]['res_hp']
                    re_hc = sommes_reservations[code_client][id_machine]['res_hc']
                    tx_hp = machines.donnees[id_machine]['tx_occ_eff_hp']
                    tx_hc = machines.donnees[id_machine]['tx_occ_eff_hc']

                    ac_hp = 0
                    ac_hc = 0
                    if ac_somme and id_machine in ac_somme:
                        ac_hp = ac_somme[id_machine]['duree_hp']
                        ac_hc = ac_somme[id_machine]['duree_hc']

                    tot_hp = scl['res'][id_machine]['tot_hp']
                    tot_hc = scl['res'][id_machine]['tot_hc']

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'ac_hp': Outils.format_heure(ac_hp), 'ac_hc': Outils.format_heure(ac_hc),
                                    're_hp': Outils.format_heure(re_hp), 're_hc': Outils.format_heure(re_hc),
                                    'tot_hp': Outils.format_heure(tot_hp), 'tot_hc': Outils.format_heure(tot_hc)}

                    sclu = scl['res'][id_machine]['users']
                    utilisateurs = Outils.utilisateurs_in_somme(sclu, users)

                    if re_hp > 0:
                        contenu += r'''
                            %(machine)s & HP & \hspace{5mm} %(re_hp)s & & & \hspace{5mm} %(ac_hp)s
                            & \hspace{5mm} %(tot_hp)s \\
                             \hline
                             ''' % dico_machine

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    ac = sclu[id_user]['ac_hp']
                                    re = sclu[id_user]['re_hp']
                                    mini = sclu[id_user]['mini_hp']
                                    tot = sclu[id_user]['tot_hp']
                                    if ac > 0 or re > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'ac': Outils.format_heure(ac),
                                                     're': Outils.format_heure(re), 'tx': tx_hp,
                                                     'mini': Outils.format_heure(mini),
                                                     'tot': Outils.format_heure(tot)}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HP & %(re)s & %(tx)s & %(mini)s & %(ac)s
                                            & %(tot)s \\
                                            \hline
                                            ''' % dico_user

                    if re_hc > 0:
                        contenu += r'''
                            %(machine)s & HC & \hspace{5mm} %(re_hc)s & & & \hspace{5mm} %(ac_hc)s
                            & \hspace{5mm} %(tot_hc)s  \\
                             \hline
                             ''' % dico_machine

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    ac = sclu[id_user]['ac_hc']
                                    re = sclu[id_user]['re_hc']
                                    mini = sclu[id_user]['mini_hc']
                                    tot = sclu[id_user]['tot_hc']
                                    if ac > 0 or re > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'ac': Outils.format_heure(ac),
                                                     're': Outils.format_heure(re), 'tx': tx_hc,
                                                     'mini': Outils.format_heure(mini),
                                                     'tot': Outils.format_heure(tot)}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HC & %(re)s & %(tx)s & %(mini)s & %(ac)s
                                            & %(tot)s \\
                                            \hline
                                            ''' % dico_user

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_xr(code_client, scl, sommes_reservations, machines):
        """
        Prix XR - Table Client Récap Pénalités Réservations
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_reservations: sommes des réservations importées
        :param machines: machines importées
        :return: table au format latex
        """

        if code_client in sommes_reservations:
            structure = r'''{|l|c|c|r|r|}'''
            legende = r'''Pénalités de réservation'''

            contenu = r'''
                \cline{3-5}
                \multicolumn{2}{c|}{} & Pénalités & \multicolumn{1}{c|}{PU} & \multicolumn{1}{c|}{Montant} \\
                \cline{3-5}
                \multicolumn{2}{c|}{} & Durée & \multicolumn{1}{c|}{CHF/h} & \multicolumn{1}{c|}{CHF} \\
                \hline
                '''

            machines_utilisees = Outils.machines_in_somme(scl['res'], machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    re_somme = sommes_reservations[code_client][id_machine]

                    tot_hp = scl['res'][id_machine]['tot_hp']
                    tot_hc = scl['res'][id_machine]['tot_hc']

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'pu_hp': Outils.format_2_dec(re_somme['pu_hp']),
                                    'pu_hc': Outils.format_2_dec(re_somme['pu_hc']),
                                    'mont_hp': Outils.format_2_dec(scl['res'][id_machine]['mont_hp']),
                                    'mont_hc': Outils.format_2_dec(scl['res'][id_machine]['mont_hc']),
                                    'tot_hp': Outils.format_heure(tot_hp), 'tot_hc': Outils.format_heure(tot_hc)}

                    if tot_hp > 0:
                        contenu += r'''%(machine)s & HP & %(tot_hp)s & %(pu_hp)s & %(mont_hp)s \\
                             \hline
                             ''' % dico_machine

                    if tot_hc > 0:
                        contenu += r'''%(machine)s & HC & %(tot_hc)s & %(pu_hc)s & %(mont_hc)s \\
                             \hline
                             ''' % dico_machine

            dico_frais = {'rm': Outils.format_2_dec(scl['rm']), 'rm_d': Outils.format_2_dec(scl['rm_d']),
                          'r': Outils.format_2_dec(scl['r']), 'rr': Outils.format_2_dec(scl['rr'])}
            contenu += r'''
                \multicolumn{4}{|r|}{Arrondi} & %(rm_d)s \\
                \hline
                \multicolumn{4}{|r|}{Total} & %(rm)s \\
                \hline
                \multicolumn{4}{|r|}{Rabais} & %(rr)s \\
                \hline
                \multicolumn{4}{|r|}{\textbf{Total à payer}} & \textbf{%(r)s} \\
                \hline
                ''' % dico_frais

            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def contenu_tps_m_cae_xmu(code_client, scl, sommes_acces, machines, users, comptes):
        """
        contenu Tps_M CAE X/M/U - Table Client Récap Temps mach avec pénalités /Machine/User
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param users: users importés
        :param comptes: comptes importés
        :return: contenu
        """

        contenu = ""
        if code_client in sommes_acces:
            somme = sommes_acces[code_client]['machines']
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    if id_machine in scl['res']:
                        pur_hp = somme[id_machine]['pur_hp']
                        pur_hc = somme[id_machine]['pur_hc']
                        tx_hp = machines.donnees[id_machine]['tx_occ_eff_hp']
                        tx_hc = machines.donnees[id_machine]['tx_occ_eff_hc']
                        if (pur_hc > 0 and tx_hc > 0) or (pur_hp > 0 and tx_hp > 0):
                            dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                            'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                            'hc': Outils.format_heure(somme[id_machine]['duree_hc'])}
                            contenu += r'''
                               \textbf{%(machine)s} & \hspace{5mm} %(hp)s & \hspace{5mm} %(hc)s \\
                                \hline
                                ''' % dico_machine

                            utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                            for nom, upi in sorted(utilisateurs.items()):
                                for prenom, ids in sorted(upi.items()):
                                    for id_user in sorted(ids):
                                        smu = somme[id_machine]['users'][id_user]
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hp': Outils.format_heure(smu['duree_hp']),
                                                     'hc': Outils.format_heure(smu['duree_hc'])}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & %(hp)s & %(hc)s \\
                                            \hline
                                            ''' % dico_user

                                        comptes_utilises = Outils.comptes_in_somme(smu['comptes'], comptes)

                                        for num_compte, id_compte in sorted(comptes_utilises.items()):
                                            smuc = smu['comptes'][id_compte]
                                            compte = comptes.donnees[id_compte]
                                            intitule_compte = Latex.echappe_caracteres(compte['numero']
                                                                                       + " - " + compte['intitule'])
                                            dico_compte = {'compte': intitule_compte,
                                                           'hp': Outils.format_heure(smuc['duree_hp']),
                                                           'hc': Outils.format_heure(smuc['duree_hc'])}
                                            contenu += r'''
                                                \hspace{10mm} %(compte)s & %(hp)s \hspace{5mm} & %(hc)s \hspace{5mm} \\
                                                \hline
                                                ''' % dico_compte
        return contenu

    @staticmethod
    def table_prix_lvr_xdj(code_client, scl, sommes_livraisons, generaux, contenu_prix_lvr_xdj_tab):
        """
        Prix LVR X/D/J - Table Client Récap Prestations livr./code D/Compte
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_livraisons: sommes des livraisons importées
        :param generaux: paramètres généraux
        :param contenu_prix_lvr_xdj_tab: contenu généré de la table
        :return: table au format latex
        """

        if code_client in sommes_livraisons:
            structure = r'''{|l|r|r|r|}'''
            legende = r'''Récapitulatif des prestations livrées'''

            contenu = ""
            i = 0
            for article in generaux.articles_d3:
                if contenu_prix_lvr_xdj_tab[article.code_d] != "":
                    dico = {'cmt': Outils.format_2_dec(scl['sommes_cat_m'][article.code_d]),
                            'crt': Outils.format_2_dec(scl['sommes_cat_r'][article.code_d]),
                            'ct': Outils.format_2_dec(scl['tot_cat'][article.code_d])}
                    contenu_prix_lvr_xdj_tab[article.code_d] += r'''
                    Total & %(cmt)s & %(crt)s & %(ct)s \\
                    \hline
                    ''' % dico
                    if i == 0:
                        i += 1
                    else:
                        contenu += r'''\multicolumn{4}{c}{} \\'''
                        contenu += contenu_prix_lvr_xdj_tab[article.code_d]

            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_cae_xj(code_client, scl, sommes_acces, client, contenu_prix_cae_xj):
        """
        Prix CAE X/J - Table Client Récap Procédés/Compte
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces: sommes des accès importés
        :param client: données client
        :param contenu_prix_cae_xj: contenu généré de la table
        :return: table au format latex
        """

        if code_client in sommes_acces:
            structure = r'''{|l|l|r|r|r|r|r|r|}'''
            legende = r'''Récapitulatif des procédés'''

            contenu = r'''
                \cline{3-8}
                \multicolumn{2}{c}{} & \multicolumn{2}{|c|}{Procédés} & \multicolumn{1}{c|}{Rabais}
                & \multicolumn{2}{c|}{Facture} & Montant \\
                \cline{1-7}
                Projet & Type & Machine & M.O. opér. & Déduc. HC & Montant & Rabais & \multicolumn{1}{c|}{net} \\
                \hline
                '''

            contenu += contenu_prix_cae_xj

            rht = client['rh'] * scl['dht']
            dico = {'mat': Outils.format_2_dec(scl['mat']), 'mr': Outils.format_2_dec(scl['somme_t_mr']),
                    'mm': Outils.format_2_dec(scl['somme_t_mm']), 'mot': Outils.format_2_dec(scl['mot']),
                    'mt': Outils.format_2_dec(scl['mt']), 'rht': Outils.format_2_dec(rht)}
            contenu += r'''
                Total & & %(mat)s & %(mot)s & %(rht)s & %(mm)s & %(mr)s & %(mt)s \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_xe(scl, client):
        """
        Prix XE - Table Client Emolument
        :param scl: sommes client calculées
        :param client: données client
        :return: table au format latex
        """

        structure = r'''{|r|r|r|r|}'''
        legende = r'''Émolument mensuel'''

        dico = {'emb':  Outils.format_2_dec(client['emb']), 'tot': Outils.format_2_dec(scl['mt']),
                'rabais': Outils.format_2_dec(scl['er']), 'emo': scl['e']}

        contenu = r'''
            \hline
            \multicolumn{1}{|l|}{Émolument de base}
            & \multicolumn{1}{l|}{Total Procédés} &
            \multicolumn{1}{l|}{Rabais émolument} & \multicolumn{1}{l|}{Émolument} \\
            \hline
            %(emb)s & %(tot)s & %(rabais)s & %(emo)s \\
            \hline
            ''' % dico

        return Latex.tableau(contenu, structure, legende)

    @staticmethod
    def table_prix_xa(scl, generaux):
        """
        Prix XA - Table Client Récap Articles
        :param scl: sommes client calculées
        :param generaux: paramètres généraux
        :return: table au format latex
        """

        structure = r'''{|l|r|r|r|}'''
        legende = r'''Récapitulatif des articles'''

        dico = {'emom': Outils.format_2_dec(scl['em']), 'emor': Outils.format_2_dec(scl['er']),
                'emo': Outils.format_2_dec(scl['e']), 'resm': Outils.format_2_dec(scl['rm']),
                'resr': Outils.format_2_dec(scl['rr']), 'res': Outils.format_2_dec(scl['r']),
                'int_emo': Latex.echappe_caracteres(generaux.articles[0].intitule_long),
                'int_res': Latex.echappe_caracteres(generaux.articles[1].intitule_long),
                'int_proc': Latex.echappe_caracteres(generaux.articles[2].intitule_long),
                'mm': Outils.format_2_dec(scl['somme_t_mm']),
                'mr': Outils.format_2_dec(scl['somme_t_mr']), 'mt': Outils.format_2_dec(scl['mt'])}

        contenu = r'''
            \cline{2-4}
            \multicolumn{1}{l|}{} & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
            & \multicolumn{1}{c|}{Total} \\
            \hline
            %(int_emo)s & %(emom)s & %(emor)s & %(emo)s \\
            \hline
            %(int_res)s & %(resm)s & %(resr)s & %(res)s \\
            \hline
            %(int_proc)s & %(mm)s & %(mr)s & %(mt)s \\
            \hline
            ''' % dico

        for article in generaux.articles_d3:
            dico = {'intitule': Latex.echappe_caracteres(article.intitule_long),
                    'mm': Outils.format_2_dec(scl['sommes_cat_m'][article.code_d]),
                    'mr': Outils.format_2_dec(scl['sommes_cat_r'][article.code_d]),
                    'mj': Outils.format_2_dec(scl['tot_cat'][article.code_d])}
            contenu += r'''
                %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                \hline
                ''' % dico

        contenu += r'''\multicolumn{3}{|r|}{Total}
            & ''' + Outils.format_2_dec(scl['somme_t']) + r'''\\
            \hline
            '''

        return Latex.tableau(contenu, structure, legende)

    @staticmethod
    def table_prix_bonus_xj(code_client, scl, sommes_acces, contenu_prix_bonus_xj):
        """
        Prix Bonus X/J - Table Client Récap Bonus/Compte
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces:  sommes des accès importés
        :param contenu_prix_bonus_xj: contenu généré de la table
        :return: table au format latex
        """

        if code_client in sommes_acces:
            structure = r'''{|l|r|}'''
            legende = r'''Récapitulatif des bonus'''

            contenu = r'''
                \cline{2-2}
                \multicolumn{1}{c}{} & \multicolumn{1}{|c|}{Bonus (Points)} \\
                \hline
                Compte & \multicolumn{1}{c|}{Déduc. HC} \\
                \hline
                '''
            contenu += contenu_prix_bonus_xj

            dico = {'bht': scl['somme_t_mb']}
            contenu += r'''Total & \multicolumn{1}{c|}{%(bht)s} \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_xaj(scl, generaux, contenu_prix_xaj):
        """
        Prix XA/J - Table Client Récap Articles/Compte
        :param scl: sommes client calculées
        :param generaux: paramètres généraux
        :param contenu_prix_xaj: contenu généré de la table
        :return: table au format latex
        """

        structure = r'''{|l|l|r|r|'''
        legende = r'''Récapitulatif des projets'''

        contenu = r'''
            \hline
            Projet & Type & \multicolumn{1}{c|}{Procédés}'''

        for article in generaux.articles_d3:
            structure += r'''r|'''
            contenu += r''' & \multicolumn{1}{c|}{
            ''' + Latex.echappe_caracteres(article.intitule_court) + r'''}'''
        structure += r'''}'''
        contenu += r'''& \multicolumn{1}{c|}{Total} \\
            \hline
            '''

        contenu += contenu_prix_xaj

        dico = {'procedes': Outils.format_2_dec(scl['mt']),
                'total': Outils.format_2_dec((scl['somme_t']-scl['r']-scl['e']))}

        contenu += r'''Total article & & %(procedes)s''' % dico

        for categorie in generaux.codes_d3():
            contenu += r''' & ''' + Outils.format_2_dec(scl['tot_cat'][categorie])

        contenu += r'''& %(total)s \\
            \hline
            ''' % dico

        return Latex.long_tableau(contenu, structure, legende)

    @staticmethod
    def table_prix_xf(scl, generaux, filtre, contenu_prix_xf):
        """
        Prix XF - Table Client Récap Postes de la facture
        :param scl: sommes client calculées
        :param generaux: paramètres généraux
        :param filtre: si nul pour code n
        :param contenu_prix_xf: contenu généré de la table
        :return: table au format latex
        """

        brut = scl['rm'] + scl['somme_t_mm'] + scl['em']
        for cat, tt in scl['sommes_cat_m'].items():
            brut += tt
        if scl['somme_t'] > 0 or (filtre == "NON" and brut > 0):
            structure = r'''{|c|l|r|r|r|}'''
            legende = r'''Récapitulatif des postes de la facture'''

            dico = {'emom': Outils.format_2_dec(scl['em']), 'emor': Outils.format_2_dec(scl['er']),
                    'emo': Outils.format_2_dec(scl['e']), 'resm': Outils.format_2_dec(scl['rm']),
                    'resr': Outils.format_2_dec(scl['rr']), 'res': Outils.format_2_dec(scl['r']),
                    'int_emo': Latex.echappe_caracteres(generaux.articles[0].intitule_long),
                    'int_res': Latex.echappe_caracteres(generaux.articles[1].intitule_long),
                    'p_emo': generaux.poste_emolument, 'p_res': generaux.poste_reservation}

            contenu = r'''
                \hline
                N. Poste & Poste & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
                & \multicolumn{1}{c|}{Total} \\
                \hline'''
            if scl['em'] > 0 and not (filtre == "OUI" and scl['e'] == 0):
                contenu += r'''
                    %(p_emo)s & %(int_emo)s & %(emom)s & %(emor)s & %(emo)s \\
                    \hline''' % dico
            if scl['rm'] > 0 and not (filtre == "OUI" and scl['r'] == 0):
                contenu += r'''
                    %(p_res)s & %(int_res)s & %(resm)s & %(resr)s & %(res)s \\
                    \hline
                    ''' % dico

            contenu += contenu_prix_xf

            contenu += r'''\multicolumn{4}{|r|}{Total}
                & ''' + Outils.format_2_dec(scl['somme_t']) + r'''\\
                \hline
                '''
            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_qte_lvr_jdu(code_client, id_compte, intitule_compte, generaux, livraisons, users):
        """
        Qté LVR J/D/U - Table Compte Détail Quantités livrées/Prestation (code D)/User
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param generaux: paramètres généraux
        :param livraisons: livraisons importées
        :param users: users importés
        :return: table au format latex
        """

        structure = r'''{|l|c|c|c|}'''
        legende = r'''Détails des prestations livrées'''

        contenu = r'''
            '''
        i = 0
        somme = livraisons.sommes[code_client][id_compte]
        for article in generaux.articles_d3:
            if article.code_d in somme:
                if i == 0:
                    i += 1
                else:
                    contenu += r'''\multicolumn{4}{c}{} \\
                        '''
                contenu += r'''
                    \hline
                    \multicolumn{1}{|l|}{
                    \textbf{''' + intitule_compte + " - " + Latex.echappe_caracteres(article.intitule_long) + r'''
                    }} & Quantité & Unité & Rabais \\
                    \hline
                    '''
                for no_prestation, sip in sorted(somme[article.code_d].items()):
                    dico_prestations = {'nom': Latex.echappe_caracteres(sip['nom']),
                                        'num': no_prestation,
                                        'quantite': "%.1f" % sip['quantite'],
                                        'unite': Latex.echappe_caracteres(sip['unite']),
                                        'rabais': Outils.format_2_dec(sip['rabais'])}
                    contenu += r'''
                        %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s
                        & \hspace{5mm} %(rabais)s \\
                        \hline
                        ''' % dico_prestations

                    utilisateurs = Outils.utilisateurs_in_somme(sip['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                spu = sip['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'quantite': "%.1f" % spu['quantite'],
                                             'unite': Latex.echappe_caracteres(sip['unite']),
                                             'rabais': Outils.format_2_dec(spu['rabais'])}
                                contenu += r'''
                                    \hspace{5mm} %(user)s & %(quantite)s & %(unite)s & %(rabais)s \\
                                    \hline
                                ''' % dico_user

                                for pos in spu['data']:
                                    liv = livraisons.donnees[pos]
                                    rem = ""
                                    dl = ""
                                    if liv['remarque'] != "":
                                        rem = "; Remarque : " + liv['remarque']
                                    if liv['date_livraison'] != "":
                                        dl = "Dt livraison: " + liv['date_livraison'] + ";"
                                    op = users.donnees[liv['id_operateur']]
                                    dico_pos = {'date_liv': Latex.echappe_caracteres(dl),
                                                'quantite': "%.1f" % liv['quantite'],
                                                'rabais': Outils.format_2_dec(liv['rabais_r']),
                                                'id': Latex.echappe_caracteres(liv['id_livraison']),
                                                'unite': Latex.echappe_caracteres(sip['unite']),
                                                'responsable': Latex.echappe_caracteres(op['prenom'] + " " + op['nom']),
                                                'commande': Latex.echappe_caracteres(liv['date_commande']),
                                                'remarque': Latex.echappe_caracteres(rem)}
                                    contenu += r'''
                                        \hspace{10mm} %(date_liv)s N. livraison: %(id)s
                                        & %(quantite)s \hspace{5mm} & %(unite)s & %(rabais)s \hspace{5mm} \\
        
                                        \hspace{10mm} \scalebox{.8}{Commande: %(commande)s;
                                        Resp: %(responsable)s%(remarque)s} & & & \\
                                        \hline
                                    ''' % dico_pos

        return Latex.long_tableau(contenu, structure, legende)

    @staticmethod
    def table_tps_cae_jkmu(code_client, id_compte, intitule_compte, users, machines, couts, acces):
        """
        Tps CAE J/K/M/U - Table Compte Détail Temps CAE/Catégorie Machine/Machine/User
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param users: users importés
        :param machines: machines importées
        :param couts: catégories coûts importées
        :param acces: accès importés
        :return: table au format latex
        """

        if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:
            structure = r'''{|l|l|l|c|c|c|}'''
            legende = r'''Détails des utilisations machines'''

            contenu = r'''
                \hline
                \multicolumn{3}{|l|}{\multirow{2}{*}{\scriptsize{\textbf{''' + intitule_compte + r'''}}}}
                & \multicolumn{2}{c|}{Machine} & Main d'oeuvre \\
                \cline{4-6}
                \multicolumn{3}{|l|}{} & HP & HC &  \\
                \hline
                '''

            somme = acces.sommes[code_client]['comptes'][id_compte]
            som_cat = acces.sommes[code_client]['categories'][id_compte]

            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                dico_cat = {'hp': Outils.format_heure(som_cat[id_cout]['duree_hp']),
                            'hc': Outils.format_heure(som_cat[id_cout]['duree_hc']),
                            'mo': Outils.format_heure(som_cat[id_cout]['mo'])}
                contenu += r'''
                    \multicolumn{3}{|l|}
                    {\textbf{''' + Latex.echappe_caracteres(couts.donnees[id_cout]['intitule']) + r'''}} &
                     \hspace{5mm} %(hp)s & \hspace{5mm} %(hc)s &
                     \hspace{5mm} %(mo)s \\
                    \hline''' % dico_cat

                for nom_machine, id_machine in sorted(mics.items()):

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                    'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                    'mo': Outils.format_heure(somme[id_machine]['mo'])}
                    contenu += r'''
                        \multicolumn{3}{|l|}{\hspace{2mm} \textbf{%(machine)s}} & \hspace{3mm} %(hp)s & 
                        \hspace{3mm} %(hc)s & \hspace{3mm} %(mo)s \\
                        \hline
                        ''' % dico_machine

                    utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                smu = somme[id_machine]['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'hp': Outils.format_heure(smu['duree_hp']),
                                             'hc': Outils.format_heure(smu['duree_hc']),
                                             'mo': Outils.format_heure(smu['mo'])}
                                contenu += r'''
                                    \multicolumn{3}{|l|}{\hspace{5mm} %(user)s} & %(hp)s & %(hc)s & %(mo)s \\
                                    \hline
                                ''' % dico_user
                                for p1 in smu['data']:
                                    cae = acces.donnees[p1]
                                    login = Latex.echappe_caracteres(cae['date_login']).split()
                                    temps = login[0].split('-')
                                    date = temps[0]
                                    for p2 in range(1, len(temps)):
                                        date = temps[p2] + '.' + date
                                    if len(login) > 1:
                                        heure = login[1]
                                    else:
                                        heure = ""

                                    rem = ""
                                    if id_user != cae['id_op']:
                                        op = users.donnees[cae['id_op']]
                                        rem += "op : " + op['nom'] + " " + op['prenom']
                                    if cae['remarque_op'] != "":
                                        if rem != "":
                                            rem += "; "
                                        rem += "rem op : " + cae['remarque_op']
                                    if cae['remarque_staff'] != "":
                                        if rem != "":
                                            rem += "; "
                                        rem += "rem CMi : " + cae['remarque_staff']

                                    dico_pos = {'date': date, 'heure': heure,
                                                'rem': Latex.echappe_caracteres(rem),
                                                'hp': Outils.format_heure(cae['duree_machine_hp']),
                                                'hc': Outils.format_heure(cae['duree_machine_hc']),
                                                'mo': Outils.format_heure(cae['duree_operateur'])}
                                    contenu += r'''
                                        \hspace{10mm} %(date)s & %(heure)s & \parbox{5cm}{%(rem)s}
                                        & %(hp)s \hspace{5mm} & %(hc)s \hspace{5mm} & %(mo)s \hspace{5mm} \\
                                        \hline
                                    ''' % dico_pos

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_cout_lvr_jd(code_client, id_compte, intitule_compte, sco, generaux, sommes_livraisons):
        """
        Coût LVR J/D - Table Compte Récap Coûts Prestations livrées/code D
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param generaux: paramètres généraux
        :param sommes_livraisons: sommes des livraisons importées
        :return: table au format latex
        """

        contenu = ""
        structure = r'''{|l|r|c|r|r|r|r|}'''
        legende = r'''Coûts des prestations livrées'''
        if code_client in sommes_livraisons and id_compte in sommes_livraisons[code_client]:
            somme = sommes_livraisons[code_client][id_compte]
            for article in generaux.articles_d3:
                if article.code_d in somme:
                    elu1 = article.eligible_U1
                    elu2 = article.eligible_U2
                    elu3 = article.eligible_U3
                    if elu1 == "NON" and elu2 == "NON" and elu3 == "NON":
                        continue

                    if contenu != "":
                        contenu += r'''
                            \multicolumn{7}{c}{} \\
                            '''

                    contenu += r'''
                        \hline
                        \multicolumn{1}{|l|}{
                        \textbf{''' + intitule_compte + " - " + Latex.echappe_caracteres(article.intitule_long) + r'''
                        }} & \multicolumn{1}{c|}{Quantité} & Unité & \multicolumn{1}{c|}{P.U.}
                        & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
                        & \multicolumn{1}{c|}{Net} \\
                        \hline
                        '''
                    for no_prestation, sip in sorted(somme[article.code_d].items()):
                        dico = {'nom': Latex.echappe_caracteres(sip['nom']), 'num': no_prestation,
                                'quantite': "%.1f" % sip['quantite'], 'unite': Latex.echappe_caracteres(sip['unite']),
                                'pux': Outils.format_2_dec(sip['pux']),
                                'montantx': Outils.format_2_dec(sip['montantx']),
                                'rabais': Outils.format_2_dec(sip['rabais']),
                                'netx': Outils.format_2_dec((sip['montantx'] - sip['rabais']))}
                        contenu += r'''
                            %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s & %(pux)s & 
                            %(montantx)s & %(rabais)s & %(netx)s \\
                            \hline
                            ''' % dico
                    dico = {'montantx_d': Outils.format_2_dec(sco['sommes_cat_m_x_d'][article.code_d]),
                            'rabais_d': Outils.format_2_dec(sco['sommes_cat_r_d'][article.code_d]),
                            'montantx': Outils.format_2_dec(sco['sommes_cat_m_x'][article.code_d]),
                            'rabais': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                            'netx': Outils.format_2_dec(sco['tot_cat_x'][article.code_d])}

                    contenu += r'''
                        \multicolumn{4}{|r|}{Arrondi} & %(montantx_d)s & %(rabais_d)s & \\
                        \hline
                        \multicolumn{4}{|r|}{Total} & %(montantx)s & %(rabais)s & %(netx)s \\
                        \hline
                        ''' % dico
        if contenu != "":
            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_cout_cae_jkm(code_client, id_compte, intitule_compte, couts, machines, sommes_acces):
        """
        Coût CAE J/K/M - Table Compte Récap Coûts Procédés/Catégorie Machine/Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param couts: catégories coûts importées
        :param machines: machines importées
        :param sommes_acces: sommes des accès importés
        :return: table au format latex
        """

        if code_client in sommes_acces and id_compte in sommes_acces[code_client]['comptes']:
            structure = r'''{|l|c|c|r|r|r|r|r|r|r|r|}'''
            legende = r'''Coûts d'utilisation des machines et main d'oeuvre par catégorie'''
            contenu = ""

            somme = sommes_acces[code_client]['comptes'][id_compte]
            som_cat = sommes_acces[code_client]['categories'][id_compte]
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                if contenu != "":
                    contenu += r'''
                        \multicolumn{7}{c}{} \\
                        '''

                contenu += r'''
                    \hline
                    \textbf{''' + intitule_compte + r'''} & \multicolumn{2}{c|}{Durée}
                    & \multicolumn{4}{c|}{PU [CHF/h]} & \multicolumn{4}{c|}{Montant [CHF]} \\
                    \hline
                    \textbf{''' + Latex.echappe_caracteres(couts.donnees[id_cout]['intitule']) + r'''}
                    & Mach. & Oper. & \multicolumn{1}{c|}{U1} & \multicolumn{1}{c|}{U2}
                    & \multicolumn{1}{c|}{U3} & \multicolumn{1}{c|}{Oper.} & \multicolumn{1}{c|}{U1}
                    & \multicolumn{1}{c|}{U2} & \multicolumn{1}{c|}{U3} & \multicolumn{1}{c|}{Oper.} \\
                    \hline
                    '''

                for nom_machine, id_machine in sorted(mics.items()):
                    duree = somme[id_machine]['duree_hp'] + somme[id_machine]['duree_hc']

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'duree': Outils.format_heure(duree),
                                    'mo': Outils.format_heure(somme[id_machine]['mo']),
                                    'cu1': Outils.format_2_dec(couts.donnees[id_cout]['U1']),
                                    'cu2': Outils.format_2_dec(couts.donnees[id_cout]['U2']),
                                    'cu3': Outils.format_2_dec(couts.donnees[id_cout]['U3']),
                                    'cmo': Outils.format_2_dec(couts.donnees[id_cout]['MO']),
                                    'mu1': Outils.format_2_dec(somme[id_machine]['mu1']),
                                    'mu2': Outils.format_2_dec(somme[id_machine]['mu2']),
                                    'mu3': Outils.format_2_dec(somme[id_machine]['mu3']),
                                    'mmo': Outils.format_2_dec(somme[id_machine]['mmo'])}
                    contenu += r'''
                        %(machine)s & %(duree)s & %(mo)s & %(cu1)s & %(cu2)s & %(cu3)s & %(cmo)s & %(mu1)s
                        & %(mu2)s & %(mu3)s & %(mmo)s \\
                        \hline
                        ''' % dico_machine

                dico_cat = {'mu1': Outils.format_2_dec(som_cat[id_cout]['mu1']),
                            'mu2': Outils.format_2_dec(som_cat[id_cout]['mu2']),
                            'mu3': Outils.format_2_dec(som_cat[id_cout]['mu3']),
                            'mmo': Outils.format_2_dec(som_cat[id_cout]['mmo'])}

                contenu += r'''
                    \multicolumn{7}{|r|}{Total} & %(mu1)s & %(mu2)s & %(mu3)s & %(mmo)s \\
                    \hline
                    ''' % dico_cat

            return Latex.long_tableau(contenu, structure, legende)

        else:
            return ""

    @staticmethod
    def table_cout_ja(code_client, id_compte, generaux, sco, sommes_livraisons):
        """
        Coût JA - Table Compte Récap  Articles
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param generaux: paramètres généraux
        :param sco: sommes compte calculées
        :param sommes_livraisons: sommes des livraisons importées
        :return: table au format latex
        """

        structure = r'''{|l|r|r|r|}'''
        legende = r'''Coûts d'utilisation '''

        dico = {'mu1': Outils.format_2_dec(sco['mu1']), 'mu2': Outils.format_2_dec(sco['mu2']),
                'mu3': Outils.format_2_dec(sco['mu3']), 'mmo': Outils.format_2_dec(sco['mmo'])}
        tot1 = sco['mu1'] + sco['mmo']
        tot2 = sco['mu2'] + sco['mmo']
        tot3 = sco['mu3'] + sco['mmo']

        contenu = r'''
            \cline{2-4}
            \multicolumn{1}{l|}{} & \multicolumn{1}{c|}{1} & \multicolumn{1}{c|}{2} & 
            \multicolumn{1}{c|}{3} \\
            \hline
            Coûts d'utilisation machine & %(mu1)s & %(mu2)s & %(mu3)s \\
            \hline
            Coûts main d'oeuvre opérateur & %(mmo)s & %(mmo)s & %(mmo)s \\
            \hline
            ''' % dico

        if code_client in sommes_livraisons and id_compte in sommes_livraisons[code_client]:
            somme = sommes_livraisons[code_client][id_compte]
            for article in generaux.articles_d3:
                if article.code_d in somme:
                    elu1 = article.eligible_U1
                    elu2 = article.eligible_U2
                    elu3 = article.eligible_U3
                    if elu1 == "NON" and elu2 == "NON" and elu3 == "NON":
                        continue
                    netx = sco['tot_cat_x'][article.code_d]
                    u1 = 0
                    u2 = 0
                    u3 = 0
                    if elu1 == "OUI":
                        u1 = netx
                    if elu2 == "OUI":
                        u2 = netx
                    if elu3 == "OUI":
                        u3 = netx
                    tot1 += u1
                    tot2 += u2
                    tot3 += u3
                    dico_article = {'intitule': Latex.echappe_caracteres(article.intitule_long),
                                    'u1': Outils.format_2_dec(u1),
                                    'u2': Outils.format_2_dec(u2), 'u3': Outils.format_2_dec(u3)}
                    contenu += r'''
                        %(intitule)s & %(u1)s & %(u2)s & %(u3)s \\
                        \hline
                        ''' % dico_article

        dico_tot = {'tot1': Outils.format_2_dec(tot1), 'tot2': Outils.format_2_dec(tot2),
                    'tot3': Outils.format_2_dec(tot3)}
        contenu += r'''
            \multicolumn{1}{|r|}{Total} & %(tot1)s & %(tot2)s & %(tot3)s \\
            \hline
            ''' % dico_tot

        return Latex.tableau(contenu, structure, legende)

    @staticmethod
    def table_prix_cae_jm(code_client, id_compte, intitule_compte, sco, sommes_acces, machines, av_hc):
        """
        Prix CAE J/M - Table Compte Récap Procédés/Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param av_hc: avantage hc pour code n
        :return: table au format latex
        """

        if code_client in sommes_acces and id_compte in sommes_acces[code_client]['comptes']:
            structure = r'''{|l|c|c|c|r|r|r|r|r|}'''
            legende = r'''Procédés (machine + main d'oeuvre)'''

            contenu = r'''
                \cline{3-9}
                \multicolumn{2}{c}{} & \multicolumn{2}{|c|}{Machine} & \multicolumn{2}{c|}{PU [CHF/h]}
                & \multicolumn{2}{c|}{Montant [CHF]} & \multicolumn{1}{c|}{Déduc. HC} \\
                \hline
                \multicolumn{2}{|l|}{\textbf{''' + intitule_compte + r'''}} & Mach. & Oper.
                & \multicolumn{1}{c|}{Mach.} & \multicolumn{1}{c|}{Oper.} & \multicolumn{1}{c|}{Mach.}
                & \multicolumn{1}{c|}{Oper.} & \multicolumn{1}{c|}{''' + av_hc + r'''} \\
                \hline
                '''

            somme = sommes_acces[code_client]['comptes'][id_compte]

            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom, id_machine in sorted(mics.items()):
                    dico_machine = {'machine': Latex.echappe_caracteres(nom),
                                    'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                    'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                    'mo': Outils.format_heure(somme[id_machine]['mo']),
                                    'pu_m': Outils.format_2_dec(somme[id_machine]['pum']),
                                    'puo': Outils.format_2_dec(somme[id_machine]['puo']),
                                    'mai_hp': Outils.format_2_dec(somme[id_machine]['mai_hp']),
                                    'mai_hc': Outils.format_2_dec(somme[id_machine]['mai_hc']),
                                    'moi': Outils.format_2_dec(somme[id_machine]['moi']),
                                    'dhi': Outils.format_2_dec(somme[id_machine]['dhi'])}

                    mo_double = False
                    if somme[id_machine]['duree_hp'] > 0 and somme[id_machine]['duree_hc'] > 0:
                        mo_double = True

                    if somme[id_machine]['duree_hp'] > 0:
                        if mo_double:
                            contenu += r'''
                                \multirow{2}{*}{%(machine)s} & HP & %(hp)s & \multirow{2}{*}{%(mo)s} & %(pu_m)s 
                                & %(puo)s & %(mai_hp)s & \multirow{2}{*}{%(moi)s} & \\
                                \cline{2-3} 
                                \cline{5-7} 
                                \cline{9-9} 
                                ''' % dico_machine
                        else:
                            contenu += r'''
                                %(machine)s & HP & %(hp)s & %(mo)s & %(pu_m)s & %(puo)s & %(mai_hp)s
                                & %(moi)s & \\
                                \hline
                                ''' % dico_machine

                    if somme[id_machine]['duree_hc'] > 0:
                        if mo_double:
                            contenu += r'''
                                 & HC & %(hc)s & & %(pu_m)s & %(puo)s & %(mai_hc)s
                                &  & %(dhi)s \\
                                \hline
                                ''' % dico_machine
                        else:
                            contenu += r'''
                                %(machine)s & HC & %(hc)s & %(mo)s & %(pu_m)s & %(puo)s & %(mai_hc)s
                                & %(moi)s & %(dhi)s \\
                                \hline
                                ''' % dico_machine

            dico_tot = {'maij_d': Outils.format_2_dec(sco['somme_j_mach_mai_d']),
                        'moij_d': Outils.format_2_dec(sco['somme_j_mach_moi_d']),
                        'dhij_d': Outils.format_2_dec(sco['somme_j_dhi_d']),
                        'maij': Outils.format_2_dec(sco['somme_j_mach_mai']),
                        'moij': Outils.format_2_dec(sco['somme_j_mach_moi']),
                        'dhij': Outils.format_2_dec(sco['somme_j_dhi']),
                        'rabais': Outils.format_2_dec(sco['somme_j_mr']),
                        'bonus': Outils.format_2_dec(sco['somme_j_mb'])}
            contenu += r'''
                \multicolumn{6}{|r|}{Arrondi} & %(maij_d)s & %(moij_d)s & %(dhij_d)s \\
                \hline
                \multicolumn{6}{|r|}{Total} & %(maij)s & %(moij)s & %(dhij)s \\
                \hline
                ''' % dico_tot

            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_cout_cae_jk(code_client, id_compte, intitule_compte, sco, sommes_acces, couts):
        """
        Coût CAE J/K - Table Compte Récap Procédés/Catégorie Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_acces: sommes des accès importés
        :param couts: catégories coûts importées
        :return: table au format latex
        """

        if code_client in sommes_acces and id_compte in sommes_acces[code_client]['categories']:
            structure = r'''{|l|r|r|r|r|}'''
            legende = r'''Coûts d'utilisation des machines et main d'oeuvre'''
            contenu = r'''
                    \hline
                    \multirow{2}{*}{\textbf{''' + intitule_compte + r'''}}
                    & \multicolumn{4}{c|}{Montant [CHF]} \\
                    \cline{2-5}
                     & \multicolumn{1}{c|}{U1} & \multicolumn{1}{c|}{U2} & \multicolumn{1}{c|}{U3}
                     & \multicolumn{1}{c|}{M.O. Oper.} \\
                    \hline
                    '''

            som_cats = sommes_acces[code_client]['categories'][id_compte]

            for id_cout, som_cat in sorted(som_cats.items()):
                dico_cat = {'intitule': Latex.echappe_caracteres(couts.donnees[id_cout]['intitule']),
                            'mu1': Outils.format_2_dec(som_cat['mu1']),
                            'mu2': Outils.format_2_dec(som_cat['mu2']),
                            'mu3': Outils.format_2_dec(som_cat['mu3']),
                            'mmo': Outils.format_2_dec(som_cat['mmo'])}

                contenu += r'''
                    %(intitule)s & %(mu1)s & %(mu2)s & %(mu3)s & %(mmo)s \\
                    \hline
                    ''' % dico_cat

            dico_compte = {'mu1_d': Outils.format_2_dec(sco['mu1_d']),
                           'mu2_d': Outils.format_2_dec(sco['mu2_d']),
                           'mu3_d': Outils.format_2_dec(sco['mu3_d']),
                           'mmo_d': Outils.format_2_dec(sco['mmo_d']),
                           'mu1': Outils.format_2_dec(sco['mu1']),
                           'mu2': Outils.format_2_dec(sco['mu2']),
                           'mu3': Outils.format_2_dec(sco['mu3']),
                           'mmo': Outils.format_2_dec(sco['mmo'])}

            contenu += r'''
                \multicolumn{1}{|r|}{Arrondi} & %(mu1_d)s & %(mu2_d)s & %(mu3_d)s & %(mmo_d)s \\
                \hline
                \multicolumn{1}{|r|}{Total} & %(mu1)s & %(mu2)s & %(mu3)s & %(mmo)s \\
                \hline
                ''' % dico_compte

            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_avtg_jm(code_client, id_compte, intitule_compte, sco, sommes_acces, machines, av_hc):
        """
        Prix Avtg J/M - Table Compte Avantage HC (Rabais ou Bonus) par Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param av_hc: avantage hc pour code n
        :return: table au format latex
        """

        if code_client in sommes_acces and id_compte in sommes_acces[code_client]['comptes']:
            structure = r'''{|l|l|c|r|}'''
            legende = av_hc + r''' d’utilisation de machines en heures creuses'''

            contenu = r'''
                 \cline{3-4}
                \multicolumn{2}{l|}{}
                & Temps Mach. & Déduc. HC \\
                \hline
                \multicolumn{2}{|l|}{\textbf{''' + intitule_compte + r'''}} & [hh:mm] & 
                \multicolumn{1}{c|}{''' + av_hc + r'''}  \\
                \hline
                '''
            somme = sommes_acces[code_client]['comptes'][id_compte]

            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom, id_machine in sorted(mics.items()):
                    if somme[id_machine]['duree_hc'] > 0:
                        dico = {'machine': Latex.echappe_caracteres(nom),
                                'temps': Outils.format_heure(somme[id_machine]['duree_hc']),
                                'deduction': Outils.format_2_dec(somme[id_machine]['dhi'])}

                        contenu += r'''
                            %(machine)s & HC & %(temps)s & %(deduction)s \\
                            \hline
                            ''' % dico

            dico = {'dhi_d': Outils.format_2_dec(sco['somme_j_dhi_d']), 'dhij': Outils.format_2_dec(sco['somme_j_dhi'])}

            contenu += r'''
                \multicolumn{3}{|r|}{Arrondi} & %(dhi_d)s \\
                \hline
                \multicolumn{3}{|r|}{Total} & %(dhij)s \\
                \hline
                ''' % dico

            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_lvr_jd(code_client, id_compte, intitule_compte, sco, sommes_livraisons, generaux):
        """
        Prix LVR J/D - Table Compte Récap Prestations livrées/code D
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_livraisons: sommes des livraisons importées
        :param generaux: paramètres généraux
        :return: table au format latex
        """

        if code_client in sommes_livraisons and id_compte in sommes_livraisons[code_client]:
            somme = sommes_livraisons[code_client][id_compte]
            structure = r'''{|l|r|c|r|r|r|}'''
            legende = r'''Prestations livrées'''
            contenu_prests = ""
            for article in generaux.articles_d3:
                if article.code_d in somme:
                    if contenu_prests != "":
                        contenu_prests += r'''
                            \multicolumn{6}{c}{} \\
                            '''

                    contenu_prests += r'''
                        \hline
                        \multicolumn{1}{|l|}{
                        \textbf{''' + intitule_compte + " - " + Latex.echappe_caracteres(article.intitule_long) + r'''
                        }} & \multicolumn{1}{c|}{Quantité} & Unité & \multicolumn{1}{c|}{P.U.}
                        & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais} \\
                        \hline
                        '''
                    for no_prestation, sip in sorted(somme[article.code_d].items()):
                        dico_prestations = {'nom': Latex.echappe_caracteres(sip['nom']),
                                            'num': no_prestation,
                                            'quantite': "%.1f" % sip['quantite'],
                                            'unite': Latex.echappe_caracteres(sip['unite']),
                                            'pu': Outils.format_2_dec(sip['pu']),
                                            'montant': Outils.format_2_dec(sip['montant']),
                                            'rabais': Outils.format_2_dec(sip['rabais'])}
                        contenu_prests += r'''
                            %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s & %(pu)s & %(montant)s
                            & %(rabais)s  \\
                            \hline
                            ''' % dico_prestations
                    dico_prestations = {'montant_d': Outils.format_2_dec(sco['sommes_cat_m_d'][article.code_d]),
                                        'rabais_d': Outils.format_2_dec(sco['sommes_cat_r_d'][article.code_d]),
                                        'montant': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                        'rabais': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d])}
                    contenu_prests += r'''
                        \multicolumn{4}{|r|}{Arrondi} & %(montant_d)s & %(rabais_d)s  \\
                        \hline
                        \multicolumn{4}{|r|}{Total} & %(montant)s & %(rabais)s  \\
                        \hline
                        ''' % dico_prestations
            return Latex.tableau(contenu_prests, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_cae_jk(code_client, id_compte, intitule_compte, sco, sommes_acces, couts):
        """
        Prix CAE J/K - Table Compte Récap Procédés/Catégorie Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_acces: sommes des accès importés
        :param couts: catégories coûts importées
        :return: table au format latex
        """

        if code_client in sommes_acces and id_compte in sommes_acces[code_client]['comptes']:

            structure = r'''{|l|c|c|r|r|r|r|}'''
            legende = r'''Procédés (Machine + Main d'œuvre)'''
            contenu = r'''
                \cline{2-7}
                \multicolumn{1}{l|}{}
                & \multicolumn{2}{c|}{Temps [hh:mm]} & \multicolumn{2}{c|}{PU [CHF/h]}  &
                 \multicolumn{2}{c|}{Montant [CHF]} \\
                \hline
                \textbf{''' + intitule_compte + r'''} & Mach. & Oper. & \multicolumn{1}{c|}{Mach.} &
                 \multicolumn{1}{c|}{Oper.} & \multicolumn{1}{c|}{Mach.} & \multicolumn{1}{c|}{Oper.}  \\
                \hline
                '''

            som_cat = sommes_acces[code_client]['categories'][id_compte]

            for id_cout, cats in sorted(som_cat.items()):
                dico_cat = {'intitule': Latex.echappe_caracteres(couts.donnees[id_cout]['intitule']),
                            'duree': Outils.format_heure(som_cat[id_cout]['duree']),
                            'mo': Outils.format_heure(som_cat[id_cout]['mo']),
                            'pum': Outils.format_2_dec(som_cat[id_cout]['pum']),
                            'puo': Outils.format_2_dec(som_cat[id_cout]['puo']),
                            'mai': Outils.format_2_dec(som_cat[id_cout]['mai']),
                            'moi': Outils.format_2_dec(som_cat[id_cout]['moi'])}
                contenu += r'''
                    %(intitule)s & %(duree)s & %(mo)s & %(pum)s & %(puo)s & %(mai)s & %(moi)s  \\
                    \hline
                    ''' % dico_cat

            dico_cat = {'mai_d': Outils.format_2_dec(sco['somme_j_mai_d']),
                        'moi_d': Outils.format_2_dec(sco['somme_j_moi_d']),
                        'maij': Outils.format_2_dec(sco['somme_j_mai']),
                        'moij': Outils.format_2_dec(sco['somme_j_moi'])}

            contenu += r'''
                \multicolumn{5}{|r|}{Arrondi} & %(mai_d)s & %(moi_d)s \\
                \hline
                \multicolumn{5}{|r|}{Total} & %(maij)s & %(moij)s \\
                \hline
                ''' % dico_cat

            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_ja(sco, generaux):
        """
        Prix JA - Table Compte Récap Articles
        :param sco: sommes compte calculées
        :param generaux: paramètres généraux
        :return: table au format latex
        """

        structure = r'''{|l|r|r|r|}'''
        legende = r'''Récapitulatif des articles du projet'''

        dico = {'mm': Outils.format_2_dec(sco['somme_j_mm']), 'mr': Outils.format_2_dec(sco['somme_j_mr']),
                'maij': Outils.format_2_dec(sco['somme_j_mai']), 'mj': Outils.format_2_dec(sco['mj']),
                'nmij': Outils.format_2_dec((sco['somme_j_mai'] - sco['somme_j_mr'])),
                'moij': Outils.format_2_dec(sco['somme_j_moi']),
                'int_proc': Latex.echappe_caracteres(generaux.articles[2].intitule_long)}

        contenu = r'''
            \cline{2-4}
            \multicolumn{1}{r|}{} & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
            & \multicolumn{1}{c|}{Net} \\
            \hline
            %(int_proc)s & %(mm)s & %(mr)s & %(mj)s \\
            \hline
            \hspace{5mm} \textit{Machine} & \textit{%(maij)s} \hspace{5mm} & \textit{%(mr)s} \hspace{5mm}
            & \textit{%(nmij)s} \hspace{5mm} \\
            \hline
            \hspace{5mm} \textit{Main d'oeuvre opérateur} & \textit{%(moij)s} \hspace{5mm} &
            & \textit{%(moij)s} \hspace{5mm} \\
            \hline
            ''' % dico

        total = sco['mj']
        for article in generaux.articles_d3:
            total += sco['tot_cat'][article.code_d]
            dico = {'intitule': Latex.echappe_caracteres(article.intitule_long),
                    'cmj': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                    'crj': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                    'cj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
            contenu += r'''
            %(intitule)s & %(cmj)s & %(crj)s & %(cj)s \\
            \hline
            ''' % dico

        contenu += r'''\multicolumn{3}{|r|}{Total} & ''' + Outils.format_2_dec(total) + r'''\\
        \hline
        '''

        return Latex.tableau(contenu, structure, legende)

    @staticmethod
    def table_prix_jdmu(code_client, id_compte, intitule_compte, sco, sommes_acces, machines, users):
        """
        Prix JD/M/U - Table Compte Déductions HC (Rabais) par Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """

        if sco['somme_j_dhi'] > 0 and code_client in sommes_acces and id_compte in sommes_acces[code_client]['comptes']:
            structure = r'''{|l|c|r|r|}'''
            legende = r'''Rabais d’utilisation de machines en heures creuses'''
            contenu = r'''
                \hline
                \multicolumn{2}{|l|}{\textbf{''' + intitule_compte + r'''}} & \multicolumn{1}{c|}{Temps Mach.}
                 & \multicolumn{1}{c|}{Rabais (CHF)} \\
                \hline
                '''

            somme = sommes_acces[code_client]['comptes'][id_compte]
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    if somme[id_machine]['dhi'] > 0:
                        dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                        'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                        'dhi': Outils.format_2_dec(somme[id_machine]['dhi'])}
                        contenu += r'''
                            \hspace{2mm} %(machine)s & HC & %(hc)s & %(dhi)s \\
                            \hline
                            ''' % dico_machine

                        utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    smu = somme[id_machine]['users'][id_user]
                                    if smu['duree_hc'] > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hc': Outils.format_heure(smu['duree_hc'])}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HC & %(hc)s \hspace{5mm} & \\
                                            \hline
                                        ''' % dico_user

            dico = {'rabais_d': Outils.format_2_dec(sco['somme_j_dhi_d']),
                    'rabais': Outils.format_2_dec(sco['somme_j_dhi'])}

            contenu += r'''
                \multicolumn{3}{|r|}{Arrondi} & %(rabais_d)s \\
                \hline
                \multicolumn{3}{|r|}{Total} & %(rabais)s \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_points_xbmu(code_client, scl, sommes_acces, machines, users):
        """
        Points XB/M/U - Table Client Récap Bonus/MAchine/User
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """
        if scl['somme_t_mb'] > 0:
            structure = r'''{|l|c|r|r|}'''
            legende = r'''Récapitulatif des bonus d’utilisation en heures creuses'''

            contenu = r'''
                \cline{3-4}
                \multicolumn{2}{l|}{} & \multicolumn{1}{c|}{Temps Mach.} & \multicolumn{1}{c|}{Points Bonus} \\
                \hline
                '''

            somme = sommes_acces[code_client]['machines']
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    if somme[id_machine]['dhm'] > 0:
                        dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                        'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                        'dhm': somme[id_machine]['dhm']}
                        contenu += r'''
                            \hspace{2mm} %(machine)s & HC & %(hc)s & %(dhm)s \\
                            \hline
                            ''' % dico_machine

                        utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    smu = somme[id_machine]['users'][id_user]
                                    if smu['duree_hc'] > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hc': Outils.format_heure(smu['duree_hc'])}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HC & %(hc)s \hspace{5mm} & \\
                                            \hline
                                        ''' % dico_user

            dico = {'bht': scl['somme_t_mb']}
            contenu += r'''
                \multicolumn{3}{|r|}{\textbf{Total points de bonus}} & %(bht)s \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_xrmu(code_client, scl, sommes_reservations, machines, users):
        """
        Prix XR/M/U - Table Client Récap Pénalités Réservations/Machine/user
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_reservations: sommes des réservations importées
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """
        if scl['rm'] > 0:
            structure = r'''{|l|c|c|r|r|}'''
            legende = r'''Récapitulatif des pénalités de réservation'''

            contenu = r'''
                \cline{3-5}
                \multicolumn{2}{l|}{} & \multicolumn{1}{c|}{Pénalités} & \multicolumn{1}{c|}{PU} 
                & \multicolumn{1}{c|}{Montant} \\
                \cline{3-5}
                \multicolumn{2}{l|}{} & \multicolumn{1}{c|}{Durée} & \multicolumn{1}{c|}{CHF/h} 
                & \multicolumn{1}{c|}{CHF} \\
                \hline
                '''

            somme = sommes_reservations[code_client]

            machines_reservees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_reservees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    scm = scl['res'][id_machine]
                    contenu_hp = ""
                    contenu_hc = ""
                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'duree_hp': Outils.format_heure(scm['tot_hp']),
                                    'pu_hp': Outils.format_2_dec(somme[id_machine]['pu_hp']),
                                    'montant_hp': Outils.format_2_dec(scm['mont_hp']),
                                    'duree_hc': Outils.format_heure(scm['tot_hc']),
                                    'pu_hc': Outils.format_2_dec(somme[id_machine]['pu_hc']),
                                    'montant_hc': Outils.format_2_dec(scm['mont_hc'])}
                    if scm['mont_hp'] > 0:
                        contenu_hp += r'''
                                %(machine)s & HP & %(duree_hp)s & %(pu_hp)s  & %(montant_hp)s \\
                                \hline
                                ''' % dico_machine

                    if scm['mont_hc'] > 0:
                        contenu_hc += r'''
                                %(machine)s & HC & %(duree_hc)s & %(pu_hc)s  & %(montant_hc)s \\
                                \hline
                                ''' % dico_machine

                    utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                smu = scm['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'duree_hp': Outils.format_heure(smu['tot_hp']),
                                             'duree_hc': Outils.format_heure(smu['tot_hc'])}
                                if scm['mont_hp'] > 0 and smu['tot_hp'] > 0:
                                    contenu_hp += r'''
                                            \hspace{5mm} %(user)s & HP & %(duree_hp)s \hspace{5mm} & & \\
                                            \hline
                                            ''' % dico_user

                                if scm['mont_hc'] > 0 and smu['tot_hc'] > 0:
                                    contenu_hc += r'''
                                            \hspace{5mm} %(user)s & HC & %(duree_hc)s \hspace{5mm} & & \\
                                            \hline
                                            ''' % dico_user
                    contenu += contenu_hp
                    contenu += contenu_hc

            dico = {'penalite_d': Outils.format_2_dec(scl['rm_d']),
                    'penalite': Outils.format_2_dec(scl['rm']),
                    'rabais': Outils.format_2_dec(scl['rr']),
                    'total': Outils.format_2_dec(scl['r'])}

            contenu += r'''
                \multicolumn{4}{|r|}{Arrondi} & %(penalite_d)s \\
                \hline
                \multicolumn{4}{|r|}{Total} & %(penalite)s \\
                \hline
                \multicolumn{4}{|r|}{Rabais} & %(rabais)s \\
                \hline
                \multicolumn{4}{|r|}{\textbf{Total à payer}} & %(total)s \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""
