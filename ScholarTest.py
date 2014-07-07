import os
os.chdir("e:\\mcc\\cmu\\devel\\papergraph")

import Scholar as sch

querier = sch.ScholarQuerier()
settings = sch.ScholarSettings()

querier.apply_settings(settings)

query = sch.SearchScholarQuery()
query.set_num_page_results(1)
query.set_phrase('MoSIFT: Recognizing Human Actions in Surveillance Videos')

querier.send_query(query)

sch.txt(querier)