from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction

from disturbance.components.proposals.models import SpatialQueryQuestion
import pandas as pd

import logging
logger = logging.getLogger(__name__)


NL = '\n'

#    'Question ID[1]':                   'question_id',
#    'Answer ID[2]':                     'answer_mlq_id',
COLUMN_MAPPING = {
    'Component Type[0]':                'component_type',
    'Question ID[1]':                   'question',
    'Answer ID[2]':                     'answer_mlq',
    'Layer Name[3]':                    'layer_name',
    'Layer URL (GeoJSON)':              'layer_url',
    'Expiry (months)[4]':               'expiry',
    'Visible to proponent[5]':          'visible_to_proponent',
    'Buffer to apply[6]':               'buffer',
    'Intersection operator[7]':         'operator',
    'Attribute table[8]':               'attribute_table',
    'Unnamed: 10':                      'unnamed_10',
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
    CDDPLayerReader('disturbance/utils/csv/CDDP_Layers_v1.xlsx')
    '''
    def __init__(self, filename):
        self.errors = []
        self.df = self.read_file(filename)

    def read_file(self, filename):
        df = pd.read_excel(filename)

        # Rename the cols from Spreadsheet headers to Model fields names
        df = df.rename(columns=COLUMN_MAPPING)
        df = df.drop(columns=['component_type'])
        df = df.drop(columns=['attribute_table'])
        df = df.drop(columns=['unnamed_10'])

        # cast date str to datetime object
        df['expiry'] = pd.to_datetime(df['expiry'], format='%d-%m-%Y')
        df['visible_to_proponent'] = df['visible_to_proponent'].map(dict(Yes=True, yes=True, No=False, no=False))
        df.fillna('', inplace=True)
        #import ipdb; ipdb.set_trace()

        # drop the blank columns from the excel spreadsheet (those mapped to 'N/A')
        #df.drop('N/A', axis=1, inplace=True)  
        return df

    def run_migration(self):
        # Iterate through the dataframe and insert into each row into model
        for index, row in self.df.iterrows():
            try:
                m = SpatialQueryQuestion(**row.to_dict())
                m.save()
            except Exception as e:
                import ipdb; ipdb.set_trace()
                self.errors.append(f'{row.to_dict()} {NL} {e} {NL}{NL}')
 
        print(f'Errors: {self.errors}')





