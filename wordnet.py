import re
from difflib import SequenceMatcher as diff
from termcolor import colored

synonyms_gls = "roget.txt"
translation_gls = "salaty.txt"


def lookup(gls,word):
	word=word.lower()
	with open(gls, "r") as file:
		for line in file:
			if word in line.split('\t',1)[0].lower().split('|'):
				return line
	return None

def info_extractor(gls,word):
	line=lookup(gls,lookup_word)
	if line:
		splited_line=line.split('\t',1)
		info={'entry':splited_line[0],'poss':[]}
		poss=re.finditer(r'(\w+) ((?:.(?!pos:))+)',splited_line[1]) # step 2
		for pos_index,pos_entry in enumerate(poss):
			info['poss'].append({'pos':pos_entry.group(1),'meanings':[]})
			meanings=re.finditer(r' ([^:]+): ((?:.(?!\d\.))+) ',pos_entry.group(2)) # step 3
			for meaning_index,meaning in enumerate(meanings):
				info['poss'][pos_index]['meanings'].append({'descr':meaning.group(1),'synonyms':[]})
				synonyms=meaning.group(2).split('.',1)[0] # step 4
				synonyms=re.findall(r'(?: |)([^,\.]+)',synonyms) # step 5
				for synonym in synonyms:
					info['poss'][pos_index]['meanings'][meaning_index]['synonyms'].append(synonym)
		return info
	return None

lookup_word=True
while lookup_word:
	lookup_word=input(colored("\nPlease enter your word (enter for previous): ",'grey'))
	if not lookup_word:
		lookup_word=last_lookup_word
		print('\n'+lookup_word)
	last_lookup_word=lookup_word
	info=info_extractor(synonyms_gls,lookup_word)
	if info:
		# print(info)
		chosen_pos_index=0
		if len(info['poss'])>1:
			print()
			for pos_index,pos_entry in enumerate(info['poss']):	
				print(str(pos_index + 1) + ". " + pos_entry['pos'])
			print()
			chosen_pos_index=int(input(colored('Please choose one of the above POSs: ','grey'))) - 1
		meanings=info['poss'][chosen_pos_index]['meanings']
		chosen_meaning_index = [0]
		if len(meanings)>1:
			print()
			for meaning_index,meaning in enumerate(meanings):
				print(str(meaning_index + 1) + '. ' + meaning['descr'])
			print()
			chosen_meaning_index=input(colored("Please choose one (or 'all' or multiple comma seperated numbers) of the above meanings: ",'grey'))
			if chosen_meaning_index=='all':
				chosen_meaning_index=range(len(meanings))
			else:
				chosen_meaning_index=[int(i)-1 for i in chosen_meaning_index.split(',')]
		main_translation=lookup(translation_gls,lookup_word)
		if main_translation:
			main_translation_text=main_translation.split('\t',1)[1]
		else:
			main_translation_text='Not Found'
		translation_texts=[[]]*len(meanings)
		similiarities=[[]]*len(meanings)
		for i in chosen_meaning_index:
			for synonym in meanings[i]['synonyms']:
				line = lookup(translation_gls,synonym)
				if line:
					splited_line=line.split('\t',1)[1]
					translation_texts[i].append(splited_line)
					similiarities[i].append(diff(None,main_translation_text,splited_line).ratio())
				else:
					translation_texts[i].append('Not Found\n')
					similiarities[i].append(0)
			translation_texts[i]=[x for _,x in sorted(zip(similiarities[i],translation_texts[i]),reverse=True)]
			meanings[i]['synonyms']=[x for _,x in sorted(zip(similiarities[i],meanings[i]['synonyms']),reverse=True)]
			similiarities[i]=sorted(similiarities[i],reverse=True)
		print('\n' + (colored('100%','red') + '\t')*bool(main_translation) + colored(lookup_word + ': ','blue') + colored(main_translation_text,'green'))
		for i in chosen_meaning_index:
			print(str(i + 1) + '. ' + meanings[i]['descr'] + ':')
			for synonym_index,synonym in enumerate(meanings[i]['synonyms']):
				if similiarities[i][synonym_index]!=0 or not main_translation:
					print(colored('{:.1f}'.format(similiarities[i][synonym_index]*100) + '%'+ '\t','red')*bool(main_translation) + colored(synonym + ': ','blue') + colored(translation_texts[i][synonym_index],'green'),end='')
			print()
	else:
		print('\n404')
