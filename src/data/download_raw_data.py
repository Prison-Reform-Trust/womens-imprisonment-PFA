"""
This script downloads the data needed for analysis from the Ministry of Justice Criminal Justice Statistics
December 2022. 

Published at https://www.gov.uk/government/statistics/criminal-justice-system-statistics-quarterly-december-2022
"""

import os
import utilities as utils

config = utils.read_config()
print(config['data']['downloadPaths'][0])

# for key, value in config['data']['downloadPaths'].keys():
#      print(value)

# data_endpoint = "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/"
# for key, value, in config['data']['downloadPaths']:
#      url = (data_endpoint +value)
#      print(url)




    
    # output_dir = os.path.join(
    #             config['data']['rawFilePath'], key+'_data.txt')
    #         with open(output_dir, 'w') as outfile:
    #             json.dump(data, outfile)
