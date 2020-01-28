import re


countries = {'UK':'United Kingdom'}
def get_country(country:str):
	country = country.strip()
	country = re.sub(r"[^\w ]|\d","",country).strip()
	return countries.get(country, country)