from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import IntegrityError, transaction

from disturbance.components.proposals.models import SpatialQueryQuestion, CddpQuestionGroup, MasterlistQuestion, QuestionOption
from disturbance.components.main.models import DASMapLayer
from ledger.accounts.models import EmailUser
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
    'Expiry (months)[4]':               'expiry',
    'Visible to proponent[5]':          'visible_to_proponent',
    'Buffer to apply[6]':               'buffer',
    'Intersection operator[7]':         'how',
    'Attribute table[8]':               'attribute_table',
    'Unnamed: 9':                       'unnamed_9',
    'Column Name[10]':                  'column_name',
    'Operator[11]':                     'operator',
    'Value[12]':                        'value',
    'Answer[13]':                       'answer',
    'PrefixAnswer[14]':                 'prefix_answer',
    'Info for Assessor[15]':            'assessor_info',
    'PrefixInfo[16]':                   'prefix_info',
    'Unnamed: 17':                      'unnamed_17',
    'CDDP_group[18]':                   'cddp_group',
    'Group_members[19]':                'group_members',
}


class CDDPLayerReader():
    '''
    from disturbance.utils.migration_cddp import CDDPLayerReader
    CDDPLayerReader('disturbance/utils/csv/CDDP_Layers_v4.xlsx')
    r.add_users()
    r.run_migration()

    from disturbance.utils.migration_cddp import CDDPLayerReader
    r = CDDPLayerReader('/app/shared/CDDP_Layers_v4.xlsx')
    r.add_users()
    r.run_migration()
    '''
    def __init__(self, filename):
        self.df = self.read_file(filename)

    def read_file(self, filename):
        df = pd.read_excel(filename)

        # Rename the cols from Spreadsheet headers to Model fields names
        df = df.rename(columns=COLUMN_MAPPING)
        #df = df.drop(columns=['component_type'])
        df = df.drop(columns=['attribute_table'])
        df = df.drop(columns=['unnamed_9', 'unnamed_17'])

        #import ipdb; ipdb.set_trace()
        # cast date str to datetime object
        df['expiry'] = pd.to_datetime(df['expiry'], format='%d-%m-%Y')
        df["expiry"] = df['expiry'].astype(str).where(df['expiry'].notnull(),'')
        df['visible_to_proponent'] = df['visible_to_proponent'].map(dict(Yes=True, yes=True, No=False, no=False))
        df.fillna('', inplace=True)
        #import ipdb; ipdb.set_trace()

        # drop the blank columns from the excel spreadsheet (those mapped to 'N/A')
        #df.drop('N/A', axis=1, inplace=True)  
        return df

    def add_users(self):
        # Iterate through the dataframe and insert into each row into model
        user_errors = []
        for index, row in self.df.iterrows():
            #import ipdb; ipdb.set_trace()
            try:
                group_name = row.cddp_group
                users = row.group_members.split(',')

                group, created = CddpQuestionGroup.objects.get_or_create(name=group_name)
                for user in users:
                    qs = EmailUser.objects.filter(email=user)
                    if qs.exists():
                        user = qs[0]
                        group.members.add(user)

            except Exception as e:
                import ipdb; ipdb.set_trace()
                user_errors.append(f'{row.to_dict()} {NL} {e} {NL}{NL}')
 
        print(f'Errors: {user_errors}')



    def run_migration(self):
        # Iterate through the dataframe and insert into each row into model
        errors = []
        for index, row in self.df.iterrows():
            try:
                if row.component_type:
                    #m = SpatialQueryQuestion(**row.to_dict())
                    #m.save()
                    try:
                        l = DASMapLayer.objects.get(layer_name=row.layer_name)
                    except ObjectDoesNotExist as oe:
                        #l = DASMapLayer.objects.create(display_name=row.layer_name, layer_name=row.layer_name, layer_url=row.layer_url)
                        l = DASMapLayer.objects.create(display_name=row.layer_name, layer_name=row.layer_name)

                    g = CddpQuestionGroup.objects.get(name=row.cddp_group)

                    question = MasterlistQuestion.objects.get(question=row.question)

                    answer_mlq = None
                    for option in question.get_options():
                        if row.answer_mlq and row.answer_mlq == option.label:
                            #answer_mlq = option
                            answer_mlq = QuestionOption.objects.get(label=option.label)

#                    if '2.0 What' in question.question:
#                        import ipdb; ipdb.set_trace()

                    if answer_mlq:
                        m = SpatialQueryQuestion(
                            #question=row.question,
                            #answer_mlq=row.answer_mlq,
                            question=question,
                            answer_mlq=answer_mlq,
                            layer_id=l.id,
                            group_id=g.id,
                            expiry=row.expiry if row.expiry else None,
                            visible_to_proponent=row.visible_to_proponent,
                            buffer=row.buffer,
                            how=row.how,
                            column_name=row.column_name,
                            operator=row.operator,
                            value=row.value,
                            answer=row.answer,
                            prefix_answer=row.prefix_answer,
                            no_polygons_proponent=-1, #row.no_polygons_proponent,
                            assessor_info=row.assessor_info,
                            prefix_info=row.prefix_info,
                            no_polygons_assessor=-1, #row.no_polygons_assessor,
                            regions='All', #row.regions
                        )
                        m.save()

            except Exception as e:
                #import ipdb; ipdb.set_trace()
                logger.error(e)
                errors.append(f'{row.to_dict()} {NL} {e} {NL}{NL}')
 
        print(f'Errors: {errors}')





