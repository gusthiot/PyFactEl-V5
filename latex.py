import re
import os
import shutil
import sys
import subprocess
from outils import Outils
from PyPDF2 import PdfFileMerger


class Latex(object):

    @classmethod
    def possibles(cls):
        return bool(shutil.which("pdflatex"))

    @staticmethod
    def echappe_caracteres(texte):
        """
        échappement des caractères qui peuvent poser problème dans les tableaux latex
        :param texte: texte à échapper
        :return: texte échappé
        """

        p = re.compile("[^ a-zA-Z0-9_'Éèéêëâàäïûùüçöô.:,;+\-%#&@\\\\$/|()\[\]\{\}]")
        texte = p.sub('', texte)

        texte = texte.replace('\\', '\\textbackslash')
        caracteres = ['%', '$', '_', '&', '#', '{', '}']
        latex_c = ['\%', '\$', '\_', '\&', '\#', '\{', '\}']
        for pos in range(0, len(caracteres)):
            texte = texte.replace(caracteres[pos], latex_c[pos])

        return texte

    @staticmethod
    def creer_latex_pdf(nom_fichier, contenu):
        """
        création d'un pdf à partir d'un contenu latex
        :param nom_fichier: nom du pdf final
        :param contenu: contenu latex
        """
        with open(nom_fichier + ".tex", 'w') as f:
            f.write(contenu)

        proc = subprocess.Popen(['pdflatex', nom_fichier + ".tex"])
        proc.communicate()

        # 2 fois pour que les longtable soient réguliers (courant de relancer latex)

        proc = subprocess.Popen(['pdflatex', nom_fichier + ".tex"])
        proc.communicate()

        try:
            os.unlink(nom_fichier + '.tex')
            os.unlink(nom_fichier + '.log')
            os.unlink(nom_fichier + '.aux')

        except OSError as err:
            Outils.affiche_message("OSError: {0}".format(err))
        except IOError as err:
            Outils.affiche_message("IOError: {0}".format(err))

    @staticmethod
    def finaliser_pdf(nom_fichier, chemin_dossier=""):
        """
        déplacer le pdf créé si nécessaire
        :param nom_fichier: nom du pdf
        :param chemin_dossier: chemin du dossier dans lequel enregistrer le pdf
        """
        fichier = nom_fichier + ".pdf"
        try:
            if chemin_dossier != '':
                shutil.copy(fichier, chemin_dossier)
                os.unlink(fichier)
        except OSError as err:
            Outils.affiche_message("OSError: {0}".format(err))
        except IOError as err:
            Outils.affiche_message("IOError: {0}".format(err))

    @staticmethod
    def concatenation_pdfs(nom_fichier, pdfs):
        """
        concatenation de pdfs
        :param nom_fichier: nom du pdf final
        :param pdfs: pages à concaténer
        """
        fichier = nom_fichier + ".pdf"
        try:
            if pdfs is not None and len(pdfs) > 1:
                merger = PdfFileMerger()
                fs = []
                for pdf in pdfs:
                    f = open(pdf, 'rb')
                    merger.append(f)
                    fs.append(f)
                merger.write('concatene.pdf')
                for f in fs:
                    f.close()
                shutil.copy('concatene.pdf', fichier)
                os.unlink('concatene.pdf')
        except OSError as err:
            Outils.affiche_message("OSError: {0}".format(err))
        except IOError as err:
            Outils.affiche_message("IOError: {0}".format(err))

    @staticmethod
    def long_tableau(contenu, structure, legende):
        """
        création d'un long tableau latex (peut s'étendre sur plusieurs pages)
        :param contenu: contenu du tableau
        :param structure: structure du tableau
        :param legende: légende du tabéeau
        :return: long tableau latex
        """
        return r'''
            {\tiny
            \begin{longtable}[c]
            ''' + structure + contenu + r'''
            \caption*{''' + legende + r'''}
            \end{longtable}}
            '''

    @staticmethod
    def tableau(contenu, structure, legende):
        """
        création d'un tableau latex
        :param contenu: contenu du tableau
        :param structure: structure du tableau
        :param legende: légende du tableau
        :return: tableau latex
        """
        return r'''
            \begin{table}[H]
            \tiny
            \centering
            \begin{tabular}''' + structure + contenu + r'''\end{tabular}
            \caption*{''' + legende + r'''}
            \end{table}
            '''

    @staticmethod
    def tableau_vide(legende):
        """
        création d'un tableau vide, juste pour avoir la légende formatée
        :param legende: légende du tableau vide
        :return: tableau avec juste la légende
        """
        return r'''
            \begin{table}[H]
            \tiny
            \centering
            \caption*{''' + legende + r'''}
            \end{table}
            '''

    @staticmethod
    def entete():
        """
        création de l'entête de fichier latex en fonction de l'OS
        :return: le contenu de l'entête
        """
        debut = r'''\documentclass[a4paper,10pt]{article}
            \usepackage[T1]{fontenc}
            \usepackage{lmodern}
            \usepackage[french]{babel}
            \usepackage{microtype}
            \DisableLigatures{encoding = *, family = * }
            '''
        if sys.platform == "win32":
            debut += r'''
                \usepackage[cp1252]{inputenc}
                '''
        elif sys.platform == "darwin":
            debut += r'''\usepackage[appelmac]{inputenc}'''
        else:
            debut += r'''\usepackage[utf8]{inputenc}'''
        return debut
