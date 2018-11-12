from outils import Outils
from latex import Latex
from .tables_annexes import TablesAnnexes
import os


class Annexes(object):
    """
    Classe pour la création des annexes
    """
    @staticmethod
    def annexes(sommes, clients, edition, livraisons, acces, machines, reservations, comptes, paramannexe, generaux,
                users, couts, docpdf):
        """
        création des annexes
        :param sommes: sommes calculées
        :param clients: clients importés
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param acces: accès importés
        :param machines: machines importées
        :param reservations: réservations importées
        :param comptes: comptes importés
        :param paramannexe: paramètres d'annexe
        :param generaux: paramètres généraux
        :param users: users importés
        :param couts: catégories coûts importées
        :param docpdf: paramètres d'ajout de document pdf
        """

        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer les annexes"
            Outils.affiche_message(info)
            return

        for code_client, scl in sommes.sommes_clients.items():
            code_client = Latex.echappe_caracteres(code_client)
            client = clients.donnees[code_client]
            nature = Latex.echappe_caracteres(generaux.code_ref_par_code_n(client['nature']))
            av_hc = Latex.echappe_caracteres(generaux.avantage_hc_par_code_n(client['nature']))
            an_couts = Latex.echappe_caracteres(generaux.annexe_cout_par_code_n(client['nature']))
            reference = nature + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
            if edition.version > 0:
                reference += "-" + str(edition.version)

            filtre = generaux.filtrer_article_nul_par_code_n(client['nature'])

            contenu_prix_bonus_xj = ""
            contenu_prix_cae_xj = ""
            contenu_prix_xaj = ""
            contenu_prix_xf = ""
            inc_fact = 1

            contenu_prix_lvr_xdj_tab = {}
            for article in generaux.articles_d3:
                contenu_prix_lvr_xdj_tab[article.code_d] = ""

            contenu_projets = ""
            contenu_details = ""
            contenu_interne = ""

            if code_client in sommes.sommes_comptes:
                comptes_utilises = Outils.comptes_in_somme(sommes.sommes_comptes[code_client], comptes)

                for num_compte, id_compte in sorted(comptes_utilises.items()):
                    id_compte = Latex.echappe_caracteres(id_compte)

                    # ## COMPTE

                    sco = sommes.sommes_comptes[code_client][id_compte]
                    compte = comptes.donnees[id_compte]
                    intitule_compte = Latex.echappe_caracteres(compte['numero'] + " - " + compte['intitule'])

                    # ## ligne Prix XF - Table Client Récap Postes de la facture

                    if sco['c1'] > 0 and not (filtre == "OUI" and sco['c2'] == 0):
                        poste = inc_fact * 10
                        intitule = Latex.echappe_caracteres(intitule_compte + " - " +
                                                            generaux.articles[2].intitule_long)

                        if sco['somme_j_mm'] > 0 and not (filtre == "OUI" and sco['mj'] == 0):
                            dico_prix_xf = {'intitule': intitule, 'poste': str(poste),
                                            'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                            'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                            'mj': Outils.format_2_dec(sco['mj'])}
                            contenu_prix_xf += r'''
                                %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                                \hline
                                ''' % dico_prix_xf
                            poste += 1

                        for article in generaux.articles_d3:
                            categorie = article.code_d
                            if sco['sommes_cat_m'][categorie] > 0 and not (filtre == "OUI"
                                                                           and sco['tot_cat'][article.code_d] == 0):
                                intitule = Latex.echappe_caracteres(intitule_compte + " - " + article.intitule_long)
                                dico_prix_xf = {'intitule': intitule, 'poste': str(poste),
                                                'mm': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                                'mr': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                                'mj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                                contenu_prix_xf += r'''
                                    %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                                    \hline
                                    ''' % dico_prix_xf
                                poste += 1

                        inc_fact += 1

                    # ## ligne Prix XA/J - Table Client Récap Articles/Compte

                    total = sco['mj']
                    dico_prix_xaj = {'compte': intitule_compte,
                                     'type': Latex.echappe_caracteres(compte['type_subside']),
                                     'procede': Outils.format_2_dec(sco['mj'])}

                    ligne = r'''%(compte)s & %(type)s & %(procede)s ''' % dico_prix_xaj

                    for categorie in generaux.codes_d3():
                        total += sco['tot_cat'][categorie]
                        ligne += r''' & ''' + Outils.format_2_dec(sco['tot_cat'][categorie])

                    if total > 0:
                        dico_prix_xaj['total'] = Outils.format_2_dec(total)
                        ligne += r'''& %(total)s \\
                            \hline
                            ''' % dico_prix_xaj
                        contenu_prix_xaj += ligne

                    # ## ligne Prix CAE X/J - Table Client Récap Procédés/Compte

                    rhj = client['rh'] * sco['somme_j_dhi']
                    dico_prix_cae_xj = {'intitule': intitule_compte,
                                        'type': Latex.echappe_caracteres(compte['type_subside']),
                                        'maij': Outils.format_2_dec(sco['somme_j_mai']),
                                        'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                        'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                        'rhj': Outils.format_2_dec(rhj),
                                        'moij': Outils.format_2_dec(sco['somme_j_moi']),
                                        'mj': Outils.format_2_dec(sco['mj'])}
                    contenu_prix_cae_xj += r'''
                        %(intitule)s & %(type)s & %(maij)s & %(moij)s & %(rhj)s & %(mm)s & %(mr)s & %(mj)s \\
                        \hline
                        ''' % dico_prix_cae_xj

                    # ## ligne Prix LVR X/D/J - Table Client Récap Prestations livr./code D/Compte

                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        for article in generaux.articles_d3:
                            if article.code_d in livraisons.sommes[code_client][id_compte]:
                                if contenu_prix_lvr_xdj_tab[article.code_d] == "":
                                    contenu_prix_lvr_xdj_tab[article.code_d] = r'''
                                        \cline{2-4}
                                        \multicolumn{1}{c}{} & \multicolumn{3}{|c|}{
                                        ''' + Latex.echappe_caracteres(article.intitule_long) + r'''} \\
                                        \hline
                                        Compte & Montant & Rabais & Montant net \\
                                        \hline
                                        '''
                                dico_prest_client = {'intitule': intitule_compte,
                                                     'cmj': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                                     'crj': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                                     'cj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                                contenu_prix_lvr_xdj_tab[article.code_d] += r'''
                                %(intitule)s & %(cmj)s & %(crj)s & %(cj)s \\
                                \hline
                                ''' % dico_prest_client

                    # ## ligne Prix Bonus X/J - Table Client Récap Bonus/Compte

                    if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:
                        bhj = client['bh'] * sco['somme_j_dhi']
                        dico_prix_bonus_xj = {'compte': intitule_compte, 'bhj': Outils.format_2_dec(bhj)}
                        contenu_prix_bonus_xj += r'''
                            %(compte)s & %(bhj)s \\
                            \hline
                            ''' % dico_prix_bonus_xj

                    # ##

                    ann_pro_titre = "Récapitulatif du projet : " + intitule_compte
                    contenu_projets += Annexes.titre_annexe(client, edition, generaux, reference, ann_pro_titre,
                                                            "Annexe facture")
                    contenu_projets += Annexes.section(client, generaux, reference, ann_pro_titre)

                    contenu_projets += TablesAnnexes.table_prix_ja(sco, generaux)
                    contenu_projets += TablesAnnexes.table_prix_cae_jk(code_client, id_compte, intitule_compte, sco,
                                                                       acces.sommes, couts)
                    contenu_projets += TablesAnnexes.table_prix_lvr_jd(code_client, id_compte, intitule_compte, sco,
                                                                       livraisons.sommes, generaux)
                    if av_hc == "RABAIS":
                        contenu_projets += TablesAnnexes.table_prix_jdmu(code_client, id_compte, intitule_compte, sco,
                                                                         acces.sommes, machines, users)
                    contenu_projets += r'''\clearpage'''

                    ann_det_titre = "Annexe détaillée du projet : " + intitule_compte
                    contenu_details += Annexes.titre_annexe(client, edition, generaux, reference, ann_det_titre,
                                                            "Annexe facture")
                    contenu_details += Annexes.section(client, generaux, reference, ann_det_titre)
                    contenu_details += TablesAnnexes.table_tps_cae_jkmu(code_client, id_compte, intitule_compte, users,
                                                                        machines, couts, acces)
                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        contenu_details += TablesAnnexes.table_qte_lvr_jdu(code_client, id_compte, intitule_compte,
                                                                           generaux, livraisons, users)
                    contenu_details += r'''\clearpage'''

                    if an_couts == "OUI":
                        contenu_interne += TablesAnnexes.table_cout_cae_jk(code_client, id_compte, intitule_compte, sco,
                                                                           acces.sommes, couts)
                        contenu_interne += TablesAnnexes.table_cout_ja(code_client, id_compte, generaux, sco,
                                                                       livraisons.sommes)
                        contenu_interne += TablesAnnexes.table_cout_cae_jkm(code_client, id_compte, intitule_compte,
                                                                            couts, machines, acces.sommes)
                        contenu_interne += TablesAnnexes.table_cout_lvr_jd(code_client, id_compte, intitule_compte, sco,
                                                                           generaux, livraisons.sommes)
                        contenu_interne += r'''\clearpage'''

                    # ## compte

            contenu_cae_xmu = TablesAnnexes.contenu_tps_m_cae_xmu(code_client, scl, acces.sommes, machines, users,
                                                                  comptes)

            suffixe = "_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_"
            suffixe += str(edition.version) + "_" + code_client

            # ## Début des tableaux

            pdfs_annexes = {}

            if scl['somme_t'] > 0:

                contenu_annexe_client = Annexes.entete(edition)
                contenu_annexe_client += Annexes.titre_annexe(client, edition, generaux, reference,
                                                              "Récapitulatif pour le client", "Annexe facture")
                contenu_annexe_client += Annexes.section(client, generaux, reference, "Récapitulatif pour le client")

                contenu_annexe_client += TablesAnnexes.table_prix_xf(scl, generaux, filtre, contenu_prix_xf)
                contenu_annexe_client += TablesAnnexes.table_prix_xaj(scl, generaux, contenu_prix_xaj)
                if av_hc == "BONUS":
                    contenu_annexe_client += TablesAnnexes.table_points_xbmu(code_client, scl, acces.sommes, machines,
                                                                             users)
                contenu_annexe_client += TablesAnnexes.table_prix_xrmu(code_client, scl, reservations.sommes, machines,
                                                                       users)
                contenu_annexe_client += r'''\end{document}'''
                Latex.creer_latex_pdf('Annexe-client' + suffixe, contenu_annexe_client)
                pdfs_annexes['Annexe-client'] = ['Annexe-client' + suffixe + ".pdf"]

                if not contenu_projets == "":
                    contenu_annexe_projets = Annexes.entete(edition)
                    contenu_annexe_projets += contenu_projets
                    contenu_annexe_projets += r'''\end{document}'''
                    Latex.creer_latex_pdf('Annexe-projets' + suffixe, contenu_annexe_projets)
                    pdfs_annexes['Annexe-projets'] = ['Annexe-projets' + suffixe + ".pdf"]

                contenu_details_2 = ""
                if code_client in reservations.sommes or contenu_cae_xmu != "":
                    contenu_details_2 += Annexes.titre_annexe(client, edition, generaux, reference,
                                                              "Annexe détaillée des pénalités de réservation",
                                                              "Annexe facture")
                    contenu_details_2 += Annexes.section(client, generaux, reference,
                                                         "Annexe détaillée des pénalités de réservation")
                    contenu_details_2 += TablesAnnexes.table_tps_penares_xmu(code_client, scl, acces.sommes,
                                                                             reservations.sommes, machines, users)
                    contenu_details_2 += TablesAnnexes.table_tps_m_cae_xmu(code_client, acces, contenu_cae_xmu)
                    contenu_details_2 += TablesAnnexes.table_tps_res_xmu(code_client, reservations, machines, users)
                if not contenu_details == "" or not contenu_details_2 == "":
                    contenu_annexe_details = Annexes.entete(edition)
                    contenu_annexe_details += contenu_details
                    contenu_annexe_details += contenu_details_2
                    contenu_annexe_details += r'''\end{document}'''
                    Latex.creer_latex_pdf('Annexe-détails' + suffixe, contenu_annexe_details)
                    pdfs_annexes['Annexe-détails'] = ['Annexe-détails' + suffixe + ".pdf"]

                if docpdf is not None:
                    pdfs = docpdf.pdfs_pour_client(client, 'Annexe-pièces')
                    if pdfs is not None and len(pdfs) > 0:
                        nom_pdf = 'Annexe-pièces' + suffixe
                        pieces = [nom_pdf + '.pdf']
                        texte = ""
                        for pos, docs in sorted(pdfs.items()):
                            for doc in docs:
                                texte += str(pos) + r''' \hspace*{5cm} 
                                    ''' + Latex.echappe_caracteres(doc['nom']) + r'''
                                     \\ 
                                    '''
                                pieces.append(doc['chemin'])
                        contenu_annexe_pieces = Annexes.entete(edition)
                        contenu_annexe_pieces += Annexes.titre_annexe(client, edition, generaux, reference,
                                                                      "Documents contractuels et informatifs",
                                                                      "Annexe facture")
                        contenu_annexe_pieces += Annexes.section(client, generaux, reference,
                                                                 "Documents contractuels et informatifs")
                        contenu_annexe_pieces += texte
                        contenu_annexe_pieces += r'''\end{document}'''
                        Latex.creer_latex_pdf(nom_pdf, contenu_annexe_pieces)
                        pdfs_annexes['Annexe-pièces'] = pieces

            if docpdf is not None:
                pdfs = docpdf.pdfs_pour_client(client, 'Annexe-interne')
                if pdfs is not None and len(pdfs) > 0:
                    nom_pdf = 'Annexe-interne-anntemp'
                    pieces = [nom_pdf + '.pdf']
                    texte = ""
                    for pos, docs in sorted(pdfs.items()):
                        for doc in docs:
                            texte += str(pos) + r''' \hspace*{5cm} 
                                ''' + Latex.echappe_caracteres(doc['nom']) + r'''
                                 \\ 
                                '''
                            pieces.append(doc['chemin'])
                    contenu_annexe_interne_a = Annexes.entete(edition)
                    contenu_annexe_interne_a += Annexes.titre_annexe(client, edition, generaux, reference,
                                                                     "Documents contractuels et informatifs",
                                                                     "Annexe interne")
                    contenu_annexe_interne_a += Annexes.section(
                        client, generaux, reference, "Annexe interne / Documents contractuels et informatifs"
                    )
                    contenu_annexe_interne_a += texte
                    contenu_annexe_interne_a += r'''\end{document}'''
                    Latex.creer_latex_pdf(nom_pdf, contenu_annexe_interne_a)
                    pdfs_annexes['Annexe-interne'] = pieces

            contenu_interne_b = ""
            if an_couts == "OUI":
                contenu_interne_b += Annexes.titre_annexe(client, edition, generaux, reference, "Coûts d'utilisation",
                                                          "Annexe interne")
                contenu_interne_b += Annexes.section(client, generaux, reference,
                                                     "Annexe interne / Coûts d’utilisation")
                contenu_interne_b += contenu_interne

            contenu_interne_b += Annexes.titre_annexe(client, edition, generaux, reference, "Tableaux supplémentaires",
                                                      "Annexe interne")
            contenu_interne_b += Annexes.section(client, generaux, reference,
                                                 "Annexe interne / Tableaux supplémentaires")
            contenu_interne_b += TablesAnnexes.table_prix_xa(scl, generaux)
            contenu_interne_b += TablesAnnexes.table_prix_xe(scl, client)
            contenu_interne_b += TablesAnnexes.table_prix_cae_xj(code_client, scl, acces.sommes, client,
                                                                 contenu_prix_cae_xj)
            if not contenu_interne_b == "":
                contenu_annexe_interne_b = Annexes.entete(edition)
                contenu_annexe_interne_b += contenu_interne_b
                contenu_annexe_interne_b += r'''\end{document}'''
                nom_pdf = 'Annexe-interne' + suffixe
                Latex.creer_latex_pdf(nom_pdf, contenu_annexe_interne_b)
                if 'Annexe-interne' in pdfs_annexes:
                    pdfs_annexes['Annexe-interne'].append(nom_pdf + ".pdf")
                else:
                    pdfs_annexes['Annexe-interne'] = [nom_pdf + ".pdf"]

            for donnee in paramannexe.donnees:
                if donnee['nom'] in pdfs_annexes:
                    if len(pdfs_annexes[donnee['nom']]) > 1:
                        Latex.concatenation_pdfs(donnee['nom'] + suffixe, pdfs_annexes[donnee['nom']])
                    Latex.finaliser_pdf(donnee['nom'] + suffixe, donnee['chemin'])
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in files:
                if f.endswith('anntemp.pdf'):
                    os.unlink(f)

    @staticmethod
    def titre_annexe(client, edition, generaux, reference, titre, annexe):
        """
        création d'un titre d'annexe
        :param client: données du client concerné
        :param edition: paramètres d'édition
        :param generaux: paramètres généraux
        :param reference: référence de la facture
        :param titre: titre de l'annexe
        :param annexe: nom de l'annexe
        :return: page de titre latex de l'annexe
        """
        dic_titre = {'code_sap': Latex.echappe_caracteres(client['code_sap']), 'ref': reference, 'titre': titre,
                     'nom': Latex.echappe_caracteres(client['abrev_labo']), 'annexe': annexe,
                     'date': edition.mois_txt + " " + str(edition.annee),
                     'centre': Latex.echappe_caracteres(generaux.centre)}

        contenu = r'''
            \thispagestyle{empty}
            \begin{adjustwidth}{0cm}{}
            %(centre)s \hspace*{\fill} \thepage \\
            %(ref)s \\
            \hspace*{\fill} %(nom)s \\
            \hspace*{\fill} %(code_sap)s \\
            \end{adjustwidth}
            \begin{center}
            \Large\textsc{%(annexe)s %(date)s} \\
            \Large\textsc{%(titre)s}
            \end{center}
            \rule{\linewidth}{1pt}
             \vspace*{5mm}
            ''' % dic_titre

        return contenu

    @staticmethod
    def section(client, generaux, reference, titre):
        """
        création d'un début de section non-visible
        :param client: données du client concerné
        :param generaux: paramètres généraux
        :param reference: référence de la facture
        :param titre: titre de la section
        :return: section latex
        """
        dic_section = {'code_sap': Latex.echappe_caracteres(client['code_sap']),
                       'nom': Latex.echappe_caracteres(client['abrev_labo']), 'ref': reference, 'titre': titre,
                       'centre': Latex.echappe_caracteres(generaux.centre)}

        section = r'''
            \fakesection{%(centre)s \\ %(ref)s \\ %(titre)s}
            {%(code_sap)s - %(nom)s \\}
            ''' % dic_section

        return section

    @staticmethod
    def entete(edition):
        """
        création de l'entête latex
        :param edition: paramètres d'édition
        :return: entête latex
        """

        entete = Latex.entete()
        entete += r'''
            \usepackage[margin=12mm, includehead, includefoot]{geometry}
            \usepackage{multirow}
            \usepackage{graphicx}
            \usepackage{longtable}
            \usepackage{dcolumn}
            \usepackage{changepage}
            \usepackage[scriptsize]{caption}
            \captionsetup[table]{position=bottom}
            \usepackage{fancyhdr}\usepackage{float}
            \restylefloat{table}

            '''

        if edition.filigrane != "":
            entete += r'''
                \usepackage{draftwatermark}
                \SetWatermarkLightness{0.8}
                \SetWatermarkAngle{45}
                \SetWatermarkScale{2}
                \SetWatermarkFontSize{2cm}
                \SetWatermarkText{''' + edition.filigrane[:15] + r'''}
                '''

        entete += r'''
            \pagestyle{fancy}

            \fancyhead{}
            \fancyfoot{}

            \renewcommand{\headrulewidth}{0pt}
            \renewcommand{\footrulewidth}{0pt}
            \renewcommand{\arraystretch}{1.5}

            \fancyhead[L]{\leftmark}
            \fancyhead[R]{\thepage \\ \rightmark}

            \newcommand{\fakesection}[2]{
                \markboth{#1}{#2}
            }

            \begin{document}
            '''

        return entete
