from disturbance.components.proposals.models import (
    SpatialQueryQuestion,
    SpatialQueryLayer,
    MasterlistQuestion,
    QuestionOption,
    CddpQuestionGroup,
    DASMapLayer,
)

import pandas as pd
import ast
from datetime import datetime, date

COLUMNS = [
    'question_id',
    'question',
    'group',
    'other_data',
    'question_option_label',
    'question_option_value',
    'layer_name',
    'display_name',
    'layer_url',
    'expiry',
    'visible_to_proponent',
    'buffer',
    'how',
    'column_name',
    'operator',
    'value',
    'prefix_answer',
    'answer',
    'prefix_info',
    'assessor_info',
    'proponent_items',
    'assessor_items',
]

def export_sqq(filename='/tmp/export_sqq.csv'):
    ''' from disturbance.utils.migrations_cddp2 import export_sqq
        export_sqq(filename='/tmp/export2.csv')
    '''

    df = pd.DataFrame(columns=COLUMNS)
    #for idx, sql in enumerate(SpatialQueryLayer.objects.filter(spatial_query_question__id__in=[267,268,270]).order_by('id')):
    for idx, sql in enumerate(SpatialQueryLayer.objects.filter().order_by('id')):
        sqq = sql.spatial_query_question
        qo_label = sqq.answer_mlq.label if sqq.answer_mlq else None 
        qo_value = sqq.answer_mlq.value if sqq.answer_mlq else None
             
        l = sql.layer
        df.loc[idx] = [
            sqq.id,
            sqq.question.question,
            sqq.group,
            sqq.other_data,
            qo_label,
            qo_value,
            l.layer_name,
            l.display_name,
            l.layer_url,
            sql.expiry,
            sql.visible_to_proponent,
            sql.buffer,
            sql.how,
            sql.column_name,
            sql.operator,
            sql.value,
            sql.prefix_answer,
            sql.answer,
            sql.prefix_info,
            sql.assessor_info,
            sql.proponent_items,
            sql.assessor_items
        ]

    df.to_csv(filename, sep='|', index=False)
    return df


def import_sqq(filename):
    ''' from disturbance.utils.migrations_cddp2 import import_sqq
        import_sqq(filename='/tmp/export2.csv')
    '''
    sql_created = []
    errors = []
    df = pd.read_csv(filename, sep='|')
    df.fillna('', inplace=True)
    for idx, row in df.iterrows():
        try: 
            group, created = CddpQuestionGroup.objects.get_or_create(name=row.group)

            qo = None
            if row.question_option_label:
                qo, created = QuestionOption.objects.get_or_create(label=row.question_option_label, value=row.question_option_value) 

            sqq, created = SpatialQueryQuestion.objects.get_or_create(
                question__question=row.question,
                answer_mlq=qo,
                defaults={
                    'group': group,
                    'other_data': row.other_data,
                    #'answer_mlq': qo,
                },
            )

            layer, created = DASMapLayer.objects.get_or_create(
                layer_name=row.layer_name,
                defaults={
                    'layer_url': row.layer_url,
                    'display_name': row.display_name,
                },
            )

            sql = SpatialQueryLayer.objects.create(
                spatial_query_question_id=sqq.id,
                layer_id=layer.id,
                #expiry=row.expiry if row.expiry else None,
                expiry=datetime.strptime(row.expiry, '%Y-%m-%d') if row.expiry else None,
                visible_to_proponent=row.visible_to_proponent,
                buffer=row.buffer,
                how=row.how,
                column_name=row.column_name,
                operator=row.operator,
                value=row.value if row.value else '',
                prefix_answer=row.prefix_answer if row.prefix_answer else '',
                answer=row.answer if row.answer else '',
                prefix_info=row.prefix_info if row.prefix_info else '',
                assessor_info=row.assessor_info if row.assessor_info else '',
                proponent_items=ast.literal_eval(row.proponent_items) if row.proponent_items else [{}],
                assessor_items=ast.literal_eval(row.assessor_items) if row.assessor_items else [{}],
            )
            sql_created.append((sqq.id, sql.id))
    
        except Exception as e: 
            errors.append(f'{idx} - {e}')
            pass

    print(f'SQL Create: {len(sql_created)}')
    print(f'Errors:     {errors}')

