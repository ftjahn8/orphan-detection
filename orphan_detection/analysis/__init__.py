
from orphan_detection import util

#candidates = util.read_lines_from_file("..\\Data\\Results\\hm.edu\\hm.edu_potential_orphans.txt")
#shuffled = util.shuffle_candidates_list(candidates)
#util.write_lines_to_file("..\\Data\\Results\\hm.edu\\hm.edu_potential_orphans_2.txt", shuffled[:100])

import requests

with open('test.txt', 'w') as outfile:
    outfile.write(requests.get("https://w3me-n.hm.edu/fakultaet/grusswort/index.de.html").text)
