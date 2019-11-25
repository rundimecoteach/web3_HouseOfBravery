import os
import signal

import requests
from bs4 import BeautifulSoup

import json

lodge_dir = './TP2/data/html/'
victim_dir = './TP2/data/json/'
lodges = range(30000,30500)

def main():
    killer = Jason()
    summer_camp = []
    place = 0

    blood = ''
    while not killer.mom_call and place < len(lodges):
        lodge = lodges[place]
        place += 1

        victim = {}
        lastname = 'http://echecs.asso.fr/FicheTournoi.aspx?Ref='+str(lodge)
        firstname = (lastname).replace(':','_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')
            
        if os.path.exists(victim_dir+firstname):
            with open(victim_dir+firstname, 'r') as f:
                try:
                    victim = json.loads(f.read())
                except:
                    pass
        else:
            blood = getFromUrl(lastname, firstname)
            instinct = BeautifulSoup(blood, 'html.parser')
            carpet = instinct.find_all('tr')
            for path in carpet:
                td = path.find_all('td')
                if len(td) == 2:
                    if td[0].string is not None and td[1].string is not None:
                        if len(td[0].string)>0 and len(td[1].string)>0:
                            victim[td[0].string.replace(':', '').strip().lower()] = td[1].string.strip()

            lastname = 'http://echecs.asso.fr/Resultats.aspx?URL=Tournois/Id/'+str(lodge)+'/'+str(lodge)+'&Action=Stats'
            firstname = (lastname).replace(':','_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')
            
            victim['stats'] = {}
            blood = getFromUrl(lastname, firstname)
            instinct = BeautifulSoup(blood, 'html.parser')
            carpet = instinct.find_all('tr')
            for path in carpet:
                actualClass = None
                if'class' in path:
                    lastClass = path['class']
                    if 'papi_liste_t' in path['class']:
                        if lastClass != path['class']:
                            actualClass = path.find('td').string.strip().lower()
                            victim['stats'][actualClass] = {}
                    elif 'papi_liste_c' in path['class']:
                        td = path.find_all('td')
                        if len(td) == 2:
                            if td[0].string is not None and td[1].string is not None:
                                if len(td[0].string)>0 and len(td[1].string)>0:
                                    victim['stats'][actualClass][td[0].string.replace(':', '').strip().lower()] = td[1].string.replace(':').strip()

            lastname = 'http://echecs.asso.fr/Resultats.aspx?URL=Tournois/Id/'+str(lodge)+'/'+str(lodge)+'&Action=Ls'
            firstname = (lastname).replace(':','_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')
        
            victim['liste_participant'] = {}
            blood = getFromUrl(lastname, firstname)
            instinct = BeautifulSoup(blood, 'html.parser')
            carpet = instinct.find_all('tr')
            for path in carpet:
                if 'class' in path:
                    lastClass = path['class']
                    header = []
                    if 'papi_liste_t' in path['class']:
                        if lastClass != path['class']:
                            for td in path.find_all('td'):
                                header.append(td.string.strip().lower())
                    elif 'papi_liste_c' in path['class'] or 'papi_liste_c' in path['class']:
                        td = path.find_all('td')
                        i = 0
                        for td in path.find_all('td'):
                            if td.string is not None:
                                if len(td.string)>0:
                                    victim['liste_participant'][header[i]] = td.string.replace(':').strip()

            lastname = 'http://echecs.asso.fr/Resultats.aspx?URL=Tournois/Id/'+str(lodge)+'/'+str(lodge)+'&Action=Ga'
            firstname = (lastname).replace(':','_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')
        
            victim['grille_resultats'] = {}
            blood = getFromUrl(lastname, firstname)
            instinct = BeautifulSoup(blood, 'html.parser')
            carpet = instinct.find('.texte_courant')
            if carpet is not None and carpet.string != "Désolé, le fichier n'existe pas...":
                carpet = instinct.find_all('tr')
                for path in carpet:
                    if 'class' in path:
                        lastClass = path['class']
                        header = []
                        if 'papi_small_t' in path['class']:
                            if lastClass != path['class']:
                                for td in path.find_all('td'):
                                    header.append(td.string.strip().lower())
                        elif 'papi_small_f' in path['class'] or 'papi_small_c' in path['class']:
                            td = path.find_all('td')
                            i = 0
                            for td in path.find_all('td'):
                                if td.string is not None:
                                    if len(td.string)>0:
                                        victim['grille_resultats'][header[i]] = td.string.replace(':').strip()

        summer_camp.append(victim)
        victim = json.dumps(victim, ensure_ascii=alse, encoding='utf-8', sort_keys=True, indent=4, separators=(',', ': '))
        
        with open(victim_dir+firstname, 'w+') as f:
            try:
                f.write(victim)
            except:
                pass

    
    with open('TP2/data/result.json', 'w+') as f:
        try:
            f.write(json.dumps(summer_camp, sort_keys=True, indent=4, separators=(',', ': ')))
        except:
            pass

def getFromUrl(url, path):
    if not os.path.exists(lodge_dir+path):
        with requests.get(url) as r:
            with open(lodge_dir+path, 'w+') as f:
                try:
                    f.write(r.text)
                    blood = r.text
                except:
                    pass
    else:
        with open(lodge_dir+path, 'r') as f:
            try:
                blood = f.read()
            except:
                pass
    return blood

class Jason:
  mom_call = False
  jason_is_here = False
  def __init__(self):
    if self.jason_is_here:
        print('Escape, Jason is already here. Leave Crystal-Lake ! LEAVE NOW !!')
    else:
        self.jason_is_here = True
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.mom_call = True

if __name__ == '__main__':
    main()
