# PyFactEl-V4

- installer Python 3 (https://www.python.org/downloads/)
    si l'option "rajouter Python au PATH" se présente, la cocher
- installer TeX Live (https://www.tug.org/texlive/)
- dans une fenêtre de commande ou un terminal, taper<pre>
  pip install -r requirements.txt</pre>
- lancer main.py et choisir un dossier de travail qui contient des csv de données brutes

- si la fabrication de pdf avec tex live ne fonctionne pas, ouvrir une console de commande et taper 'fmtutil --sys --all'

Le dossier 'importes' contient les classes servant à l'importation des données contenues dans les csv et au traitement 
de base de ces données

Le dossier 'paramètres' contient les classes servant à l'importation des paramètres d'édition et des paramètres généraux

Le dossier 'traitement' contient les classes servant à la fabrication de la facture, du bilan et des annexes, ainsi que 
le fichier 'rabais.py' servant au calcul des rabais

Le dossier de travail doit contenir les fichiers suivants (noms modifiables dans le code au besoin) :

    - cae.csv 
    - client.csv
    - coeffmachine.csv
    - coeffprestation.csv
    - compte.csv
    - lvr.csv
    - machine.csv
    - paramedit.csv
    - paramgen.csv
    - prestation.csv
    - res.csv
