import json
from os import environ

# hack to override sqlite database filename
# see: https://help.morph.io/t/using-python-3-with-morph-scraperwiki-fork/148
environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'
import scraperwiki

import dac_crs

'''
Generates codelist files from CRS codelists.
'''

with open('crs_mappings.json') as f:
    crs_mappings = json.load(f)

crs_xls = dac_crs.fetch_xls()

for name, mapping in crs_mappings.items():
    print('Extracting {} from spreadsheet ...'.format(name))
    codelist = dac_crs.get_crs_codelist(crs_xls, mapping)
    scraperwiki.sqlite.save(['code'], codelist, name)
    fieldnames = [x[1] for x in mapping['cols']]
    print('Saving {}.csv'.format(name))
    dac_crs.save_csv(name, codelist, fieldnames)

print('Combining sector_en and sector_fr ...')
sectors_en = scraperwiki.sqlite.select('* from sector_en')
for sector in sectors_en:
    fr_data = scraperwiki.sqlite.select('`name_fr`, `description_fr` from sector_fr where `code` = "{}"'.format(sector['code']))
    if len(fr_data) == 0:
        sector.update(fr_data[0])
fieldnames = [x[1] for x in crs_mappings['sector_en']['cols']] + ['name_fr', 'description_fr']
print('Saving sectors.csv')
dac_crs.save_csv('sectors', sectors_en, fieldnames)
scraperwiki.sqlite.save(['code'], sectors_en, 'sector')
