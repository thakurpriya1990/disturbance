from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction

from disturbance.components.proposals.models import SpatialQueryQuestion
import pandas as pd

import logging
logger = logging.getLogger(__name__)


NL = '\n'

COLUMN_MAPPING = {
    'Question ID[1]':                   'question_id',
    'Answer ID[2]':                     'answer_mlq_id',
    'Layer Name[3]':                    'layer_name',
    'Layer URL (GeoJSON)':              'layer_url',
    'Expiry (months)[4]':               'expiry',
    'Visible to proponent[5]':          'visible_to_proponent',
    'Buffer to apply[6]':               'buffer',
    'Intersection operator[7]':         'operator',
    'Attribute table[8]':               'N/A',
    'Unnamed: 9':                       'N/A',
    'Column Name':                      'column_name',
    'Operator[12]':                     'operator',
    'Value[13]':                        'value',
    'Answer[14]':                       'answer',
    'PrefixAnswer[15]':                 'prefix_answer',
    'NoPolygonsToProcessProponent[16]': 'no_polygons_proponent',
    'Info for Assessor[17]':            'assessor_info',
    'PrefixInfo[18]':                   'prefix_info',
    'NoPolygonsToProcessAssessor[19]':  'no_polygons_assessor',
    'Regions[9]':                       'regions',
}


class CDDPLayerReader():
    '''
    from disturbance.utils.migration_cddp import CDDPLayerReader
    CDDPLayerReader('/home/jawaidm/Downloads/CDDP_Layers_v1.xltx')
    '''
    def __init__(self, filename):
        self.errors = []
        self.run_migration(filename)

    def run_migration(self, filename):
        df = pd.read_excel(filename)


        # Rename the cols from Spreadsheet headers to Model fields names
        df = df.rename(columns=COLUMN_MAPPING)

        # drop the blank columns from the excel spreadsheet (those mapped to 'N/A')
        df.drop('N/A', axis=1, inplace=True)  

        # Iterate through the dataframe and insert into each row into model
        for index, row in df.iterrows():
            try:
                m = SpatialQueryQuestion(**row.to_dict())
                m.save()
            except Exception as e:
                self.errors.append(f'{row.to_dict()} {NL} {e} {NL}{NL}')
 
        print(f'Errors: {self.errors}')





