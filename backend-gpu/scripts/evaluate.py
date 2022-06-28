import pandas as pd
import numpy as np
import torch
from transformers import GPT2Config, GPT2LMHeadModel, AutoTokenizer
from collections import OrderedDict
from tqdm import tqdm
import torch.nn.functional as F
from pathlib import Path
import json

def evaluate (
    model_name_input="mrm8488/GPT-2-finetuned-CORD19",
    checkpoint_name_input=None
):
    model_name = model_name_input
    checkpoint_name = checkpoint_name_input

    def generate(input_ids):
        generated_sequence = []
        distributions = []
        comma_id = tokenizer.encode(',')[0]
        eos_id = tokenizer.eos_token_id
        sep_id = tokenizer.sep_token_id
        sepo_id = tokenizer(' | ')['input_ids'][0]
        output_indexes = [0]
        current_index = 0
        # past = None
        ended_with_eos = False
        while(len(generated_sequence) < 100):

            if current_index > 0:
                if (predicted_token_tensor == comma_id):
                    output_indexes.append(current_index)

            outputs = model(
                input_ids,
                # past_key_values=past,
                # use_cache=True,
                return_dict=True
            )
            # past = outputs.past_key_values
            next_token_logits = outputs.logits[:, -1, :]
            predicted_token_tensor = torch.argmax(next_token_logits)

            if (predicted_token_tensor == eos_id) or (predicted_token_tensor == sepo_id) or (predicted_token_tensor == sep_id) :
                ended_with_eos = True
                break

            distributions.append(
                F.softmax(next_token_logits[0], 0).detach()
            )
            
            input_ids = torch.cat(
                (input_ids, predicted_token_tensor.view(1, 1)),
                dim=-1
            ).detach()
            generated_sequence.append(predicted_token_tensor.detach())
            current_index += 1
        return generated_sequence, output_indexes, distributions, ended_with_eos

    def generateTable(inputs, output_attributes):
        table_outputs = []
        fields = output_attributes
        with torch.no_grad():
            for it, (input_text, doi) in enumerate(tqdm(inputs)):
                # print(input_text)
                prefix_input_ids = tokenizer.encode(
                    input_text,
                    return_tensors='pt',
                    truncation=True,
                    max_length=hparam['max_len'] -100
                )
                generated_outputs = [[]]
                for field in fields:
                    tmp_generated_outputs = []
                    for istance_index, instance in enumerate(generated_outputs):
                        confidences = []
                        past_conditional = ''
                        if len(instance) > 0:
                            for output in instance:
                                past_conditional += output['attribute'] + ': ' + output['value'] + ' | '
                        tmp_field = field['value']
                        conditional_text = past_conditional + tmp_field + '_list:' if field['multiple'] else past_conditional + tmp_field + ':',
                        # print('conditional text:', conditional_text[0])
                        conditional_ids = tokenizer.encode(
                            conditional_text[0],
                            return_tensors='pt',
                            truncation=True,
                            max_length=100
                        )


                        input_ids = torch.cat(
                            (
                                torch.tensor([[tokenizer.bos_token_id]]),
                                prefix_input_ids,
                                torch.tensor([[tokenizer.sep_token_id]]),
                                conditional_ids
                            ),
                            dim=-1
                        ).to(device)

                        generated_sequence, output_indexes, distributions, ended_with_eos\
                            = generate(input_ids)

                        distributions = [
                            distribution.cpu().numpy() for distribution in distributions
                        ]
                        # print(tokenizer.decode(generated_sequence))
                        outputs_text = tokenizer.decode(generated_sequence).split(',')

                        if not ended_with_eos:
                            outputs_text = outputs_text[:-1]
                            output_indexes = output_indexes[:-1]
                        # print('Abstract number:', it)
                        # print('generated sequence:', tokenizer.decode(generated_sequence))
                        if (len(generated_sequence)) == 0 and field['value'] == 'mutation_name' and field['multiple'] :
                            tmp_generated_outputs = []
                            break


                        outputs_text_filtered = []
                        for i, output_index in enumerate(output_indexes):
                            # confidence 1st token
                            if outputs_text[i] not in outputs_text[:i]:
                                outputs_text_filtered.append(outputs_text[i])
                                out_prob = distributions[output_index]
                                confidences.append(np.max(out_prob))

                                start_index = output_index
                                end_index = output_indexes[i + 1] - 1 if i < (len(outputs_text)-1) else len(generated_sequence)

                        assert len(outputs_text_filtered) == len(confidences), \
                            f'n of outputs not correspond n of confidences: {outputs_text} {confidences}\n'\
                            +f'Len Input: {prefix_input_ids.shape}, Len Cond: {conditional_ids.shape}'
                        
                        
                        for output_index, output in enumerate(outputs_text_filtered):
                            if output not in outputs_text[:output_index]:
                                tmp_generated_outputs.append(
                                    instance + [
                                        dict(
                                            attribute=field['value'],
                                            value=output.strip(),
                                            confidence=np.round(np.float64(confidences[output_index]), 2),
                                        )
                                    ]
                                )
                    
                    generated_outputs = tmp_generated_outputs
                
                table_outputs.append(dict(doi=doi, outputs=generated_outputs))
            return table_outputs

    def compute_scores(predictions, targets, confusion_only=False):
        tp = 0
        fp = 0
        fn = 0
        targets = targets.copy()
        for prediction in predictions:
            if prediction in targets:
                tp += 1
                targets.remove(prediction)
            else:
                fp += 1
        fn += len(targets)
        
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
        if confusion_only:
            return tp, fp, fn
        else:
            return precision, recall, f1

    def compute_corpus_scores(predictions_targets_list):
        general_scores = pd.DataFrame()
        general_scores[['precision', 'recall', 'f1', 'predictions', 'targets', 'doi']] = predictions_targets_list.apply(
            lambda row: compute_scores(
                row['prediction_values'], row['target_values']
                ) + (row['prediction_values'], row['target_values'], row['doi'])
            ,
            axis=1
        ).to_list()
        scores_by_doi = general_scores[['precision', 'recall', 'f1',  'doi']].groupby('doi').mean().reset_index()
        len_by_doi = general_scores[['doi', 'targets']].groupby('doi').agg({'targets': len}).reset_index().rename(columns = {'targets': 'targets_len'})
        scores_by_doi = pd.merge(
            scores_by_doi,
            len_by_doi,
            on='doi'
        )

        # Compute macro scores
        macro_scores = scores_by_doi[['precision', 'recall', 'f1']].mean().to_list()
        macro_scores_dict = dict(precision=round(macro_scores[0], 3), recall=round(macro_scores[1], 3), f1=round(macro_scores[2], 3))

        # Compute average macro scores
        total_n_entities = scores_by_doi['targets_len'].sum()
        scores_by_doi['weighted_precision'] = scores_by_doi.apply(lambda row: row['precision']*row['targets_len']/total_n_entities, axis=1)
        scores_by_doi['weighted_recall'] = scores_by_doi.apply(lambda row: row['recall']*row['targets_len']/total_n_entities, axis=1)
        scores_by_doi['weighted_f1'] = scores_by_doi.apply(lambda row: row['f1']*row['targets_len']/total_n_entities, axis=1)
        macro_weighted_scores_dict = dict(
            precision=round(scores_by_doi['weighted_precision'].sum(), 3),
            recall=round(scores_by_doi['weighted_recall'].sum(), 3),
            f1=round(scores_by_doi['weighted_f1'].sum(), 3)
        )

        # Compute micro scores
        confusion_values = pd.DataFrame()
        confusion_values[['tp', 'fp', 'fn']] = predictions_targets_list.apply(
            lambda row: compute_scores(
                row['prediction_values'], row['target_values'],
                confusion_only=True
                ),
            axis=1
        ).to_list()
        tp_sum, fp_sum, fn_sum = confusion_values.sum().to_list()
        micro_precision = tp_sum / (tp_sum + fp_sum)
        micro_recall = tp_sum / (tp_sum + fn_sum)
        micro_f1 = 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall)
        micro_scores_dict = dict(precision=round(micro_precision, 3), recall=round(micro_recall, 3), f1=round(micro_f1, 3))

        general_scores['predictions'] = general_scores.apply( lambda row: ', '.join(row['predictions']), axis=1)
        general_scores['targets'] = general_scores.apply( lambda row: ', '.join(row['targets']), axis=1)
        return {
            'scores': { 'macro': macro_scores_dict, 'micro': micro_scores_dict, 'weighted_macro': macro_weighted_scores_dict},
            'df_general_scores': json.loads(general_scores.to_json(orient='records')),
            'df_scores_by_doi': json.loads(scores_by_doi.to_json(orient='records'))
        }

    my_file = Path('api/test_results/' + checkpoint_name[:-5] + '.tsv')
    # print(my_file.is_file())
    if not my_file.is_file():

        device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        print('GPU available:', torch.cuda.is_available())
        hparam = {
            'max_len': 900,
        }

        # Load pre-trained model (weights)
        model_name = "mrm8488/GPT-2-finetuned-CORD19"
        config = GPT2Config()
        model = GPT2LMHeadModel(config)
        model.eval()
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.add_special_tokens({
            'pad_token': '<PAD>',
            'bos_token': '<BOS>',
            'eos_token': '<EOS>',
            'sep_token': '<SEP>',
            'additional_special_tokens': ['<SEPO>']
        })
        model.resize_token_embeddings(len(tokenizer))

        # checkpoint_name = 'multiple-instances-cord19-epoch=06.ckpt'
        checkpoint = torch.load('api/Checkpoints/' + checkpoint_name, map_location='cpu')
        if 'state_dict' in checkpoint.keys():
            state_dict = checkpoint['state_dict']
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                if k[:6] == 'model.':
                    name = k[6:]
                else:
                    name = k
                new_state_dict[name] = v
            model.load_state_dict(new_state_dict)
            print(checkpoint_name, 'new state dict load')
            torch.save(model.state_dict(), '/api/Checkpoints/' + checkpoint_name)
        else:
            model.load_state_dict(checkpoint)
            print(checkpoint_name, 'checkpoint loaded')
            del checkpoint

        model.to(device)

        df_test = pd.read_csv('api/local_data/test_set.csv', sep='\t', index_col=[0])
        prediction_attributes = [
            { 'value': 'mutation_name', 'multiple': True},
            { 'value': 'effect', 'multiple': True},
            { 'value': 'level', 'multiple': False}
        ]
        dois = df_test['doi'].unique()
        abstract_doi_list = [[df_test.loc[df_test['doi'] == doi, 'abstract'].to_list()[0], doi ]for doi in dois]

        prediction_results = generateTable(abstract_doi_list, prediction_attributes)

        prediction_list = []
        for prediction in prediction_results:
            if len(prediction['outputs']) > 0:
                for instance in prediction['outputs']:
                    output = {}
                    for element in instance:
                        output['doi'] = prediction['doi']
                        output[element['attribute']] = element['value']
                    prediction_list.append(output)
            else:
                prediction_list.append({
                    'doi': prediction['doi'],
                    'mutation_name': '',
                    'effect': '', 
                    'level': ''
                })

        pd.DataFrame(
            {
                'doi': [prediction['doi'] for prediction in prediction_list],
                'entity': [prediction['mutation_name'] for prediction in prediction_list],
                'effect': [prediction['effect'] for prediction in prediction_list],
                'level': [prediction['level'] for prediction in prediction_list]
            }
        ).to_csv('api/test_results/' + checkpoint_name[:-5] + '.tsv', sep='\t')

    df_predictions = pd.read_csv('api/test_results/' + checkpoint_name[:-5] + '.tsv', sep='\t', index_col=[0])
    df_predictions = df_predictions.fillna('')
    df_predictions['entity'] = df_predictions['entity'].astype(str).str.upper()
    df_test = pd.read_csv('api/local_data/test_set.csv', sep='\t', index_col=[0])
    df_test = df_test.fillna('')
    df_test['entity'] = df_test['entity'].astype(str).str.upper()

    # create entity targets and predictions
    entity_targets_list =  df_test.groupby('doi')['entity'].apply(lambda x: list(x)).reset_index()
    entity_targets_list.rename(columns={'entity': 'target_values'}, inplace=True)

    entity_predictions_list = df_predictions.groupby('doi')['entity'].apply(lambda x: list(x)).reset_index()
    entity_predictions_list.rename(columns={'entity': 'prediction_values'}, inplace=True)

    entity_predictions_targets_list = pd.merge(
        entity_predictions_list,
        entity_targets_list,
        on='doi'
    )

    # Create effect predictions and targets
    df_entity_matches = pd.merge(
        entity_targets_list,
        entity_predictions_list,
        on="doi",
    )
    df_entity_matches['entity_matches'] = df_entity_matches.apply(lambda row: list(set(row['prediction_values']) & set(row['target_values'])) , axis=1)
    dois_entity_matches = zip(df_entity_matches['doi'].to_list(), df_entity_matches['entity_matches'].to_list())
    effect_predictions_list = pd.DataFrame()
    effect_targets_list = pd.DataFrame()
    for (doi, matches) in dois_entity_matches:
        for match in matches:
            prediction_effects = []
            target_effects = []
            prediction_effects += df_predictions.loc[
                (df_predictions['doi'] == doi) & (df_predictions['entity'] == match), 'effect'
            ].to_list()
            target_effects += df_test.loc[
                (df_test['doi'] == doi) & (df_test['entity'] == match), 'effect'
            ].to_list()

            effect_predictions_list = pd.concat(
                [effect_predictions_list, pd.DataFrame({'doi': [doi], 'entity': [match], 'prediction_values': [prediction_effects]})]
            ).reset_index(drop=True)
            effect_targets_list = pd.concat(
                [effect_targets_list, pd.DataFrame({'doi': [doi], 'entity': [match], 'target_values': [target_effects]})]
            ).reset_index(drop=True)

    effect_predictions_targets_list = pd.merge(
        effect_predictions_list,
        effect_targets_list,
        on=['doi', 'entity']
    )

    # Create level predictions and targets
    df_effect_matches = pd.merge(
        effect_targets_list.rename(columns={'values': 'target_values'}),
        effect_predictions_list.rename(columns={'values': 'prediction_values'}),
        on=['doi', 'entity'],
    )
    df_effect_matches['effect_matches'] = df_effect_matches.apply(lambda row: list(set(row['prediction_values']) & set(row['target_values'])) , axis=1)
    # dois_entity_effect_matches = pd.merge(
    #     df_effect_matches[['doi', 'effect_matches']],
    #     df_entity_matches[['doi', 'entity_matches']],
    #     on='doi'
    # )
    dois_effect_matches_list = zip(
        df_effect_matches['doi'].to_list(),
        df_effect_matches['entity'].to_list(),
        df_effect_matches['effect_matches'].to_list()
    )
    level_predictions_list = pd.DataFrame()
    level_targets_list = pd.DataFrame()
    for (doi, entity, effect_matches) in dois_effect_matches_list:
        # if doi =='10.1016/j.ygeno.2021.05.006':
            # print('entity matches', entity)
            # print('effect matches', effect_matches)
        for effect_match in effect_matches:
            prediction_levels = []
            target_levels = []
            prediction_levels += df_predictions.loc[
                (df_predictions['doi'] == doi)\
                & (df_predictions['entity'] == entity)\
                & (df_predictions['effect'] == effect_match),
                'level'
            ].to_list()
            target_levels += df_test.loc[
                (df_test['doi'] == doi)\
                & (df_test['entity'] == entity)\
                & (df_test['effect'] == effect_match),
                'level'
            ].to_list()

            level_predictions_list = pd.concat(
                [level_predictions_list, pd.DataFrame({
                    'doi': [doi],
                    'entity': [entity],
                    'effect': [effect_match],
                    'prediction_values': [prediction_levels]
                })]
            ).reset_index(drop=True)
            level_targets_list = pd.concat(
                [level_targets_list, pd.DataFrame({
                    'doi': [doi],
                    'entity': [entity],
                    'effect': [effect_match],
                    'target_values': [target_levels]
                })]
            ).reset_index(drop=True)
    level_predictions_targets_list = pd.merge(
        level_predictions_list,
        level_targets_list,
        on=['doi', 'entity', 'effect']
    )

    entity_scores_dict = compute_corpus_scores(entity_predictions_targets_list)
    effect_scores_dict = compute_corpus_scores(effect_predictions_targets_list)
    level_scores_dict = compute_corpus_scores(level_predictions_targets_list)

    return {
        'entity_scores_dict': entity_scores_dict,
        'effect_scores_dict': effect_scores_dict,
        'level_scores_dict': level_scores_dict
    }

class Evaluator:
    def __init__(self) -> None:
        self.model = None
        self.device = None
        self.status = 0
    
        self.hparam = {
            'max_len': 900,
        }
        self.model_name = None
        self.model = None
        self.tokenizer = None


    def evaluate(
        self,
        model_name_input="mrm8488/GPT-2-finetuned-CORD19",
        checkpoint_name_input=None
    ):
        model_name = model_name_input
        checkpoint_name = checkpoint_name_input

        my_file = Path('api/test_results/' + checkpoint_name[:-5] + '.tsv')
        # print(my_file.is_file())
        if not my_file.is_file():

            self.device = torch.device(
                "cuda:0" if torch.cuda.is_available() else "cpu"
            )
            print('GPU available:', torch.cuda.is_available())
            self.hparam = {
                'max_len': 900,
            }

            # Load pre-trained model (weights)
            # self.model_name = "mrm8488/GPT-2-finetuned-CORD19"
            config = GPT2Config()
            self.model = GPT2LMHeadModel(config)
            self.model.eval()
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.tokenizer.add_special_tokens({
                'pad_token': '<PAD>',
                'bos_token': '<BOS>',
                'eos_token': '<EOS>',
                'sep_token': '<SEP>',
                'additional_special_tokens': ['<SEPO>']
            })
            self.model.resize_token_embeddings(len(self.tokenizer))

            # checkpoint_name = 'multiple-instances-cord19-epoch=06.ckpt'
            checkpoint = torch.load('api/Checkpoints/' + checkpoint_name, map_location='cpu')
            if 'state_dict' in checkpoint.keys():
                state_dict = checkpoint['state_dict']
                new_state_dict = OrderedDict()
                for k, v in state_dict.items():
                    if k[:6] == 'model.':
                        name = k[6:]
                    else:
                        name = k
                    new_state_dict[name] = v
                self.model.load_state_dict(new_state_dict)
                print(checkpoint_name, 'new state dict load')
                torch.save(self.model.state_dict(), '/api/Checkpoints/' + checkpoint_name)
            else:
                self.model.load_state_dict(checkpoint)
                print(checkpoint_name, 'checkpoint loaded')
                del checkpoint

            self.model.to(self.device)

            df_test = pd.read_csv('api/local_data/test_set.csv', sep='\t', index_col=[0])
            prediction_attributes = [
                { 'value': 'mutation_name', 'multiple': True},
                { 'value': 'effect', 'multiple': True},
                { 'value': 'level', 'multiple': False}
            ]
            dois = df_test['doi'].unique()
            abstract_doi_list = [[df_test.loc[df_test['doi'] == doi, 'abstract'].to_list()[0], doi ]for doi in dois]

            prediction_results = self.generateTable(abstract_doi_list, prediction_attributes)

            prediction_list = []
            for prediction in prediction_results:
                if len(prediction['outputs']) > 0:
                    for instance in prediction['outputs']:
                        output = {}
                        for element in instance:
                            output['doi'] = prediction['doi']
                            output[element['attribute']] = element['value']
                        prediction_list.append(output)
                else:
                    prediction_list.append({
                        'doi': prediction['doi'],
                        'mutation_name': '',
                        'effect': '', 
                        'level': ''
                    })

            pd.DataFrame(
                {
                    'doi': [prediction['doi'] for prediction in prediction_list],
                    'entity': [prediction['mutation_name'] for prediction in prediction_list],
                    'effect': [prediction['effect'] for prediction in prediction_list],
                    'level': [prediction['level'] for prediction in prediction_list]
                }
            ).to_csv('api/test_results/' + checkpoint_name[:-5] + '.tsv', sep='\t')

        df_predictions = pd.read_csv('api/test_results/' + checkpoint_name[:-5] + '.tsv', sep='\t', index_col=[0])
        df_predictions = df_predictions.fillna('')
        df_predictions['entity'] = df_predictions['entity'].astype(str).str.upper()
        df_test = pd.read_csv('api/local_data/test_set.csv', sep='\t', index_col=[0])
        df_test = df_test.fillna('')
        df_test['entity'] = df_test['entity'].astype(str).str.upper()

        # create entity targets and predictions
        entity_targets_list =  df_test.groupby('doi')['entity'].apply(lambda x: list(x)).reset_index()
        entity_targets_list.rename(columns={'entity': 'target_values'}, inplace=True)

        entity_predictions_list = df_predictions.groupby('doi')['entity'].apply(lambda x: list(x)).reset_index()
        entity_predictions_list.rename(columns={'entity': 'prediction_values'}, inplace=True)

        entity_predictions_targets_list = pd.merge(
            entity_predictions_list,
            entity_targets_list,
            on='doi'
        )

        # Create effect predictions and targets
        df_entity_matches = pd.merge(
            entity_targets_list,
            entity_predictions_list,
            on="doi",
        )
        df_entity_matches['entity_matches'] = df_entity_matches.apply(lambda row: list(set(row['prediction_values']) & set(row['target_values'])) , axis=1)
        dois_entity_matches = zip(df_entity_matches['doi'].to_list(), df_entity_matches['entity_matches'].to_list())
        effect_predictions_list = pd.DataFrame()
        effect_targets_list = pd.DataFrame()
        for (doi, matches) in dois_entity_matches:
            for match in matches:
                prediction_effects = []
                target_effects = []
                prediction_effects += df_predictions.loc[
                    (df_predictions['doi'] == doi) & (df_predictions['entity'] == match), 'effect'
                ].to_list()
                target_effects += df_test.loc[
                    (df_test['doi'] == doi) & (df_test['entity'] == match), 'effect'
                ].to_list()

                effect_predictions_list = pd.concat(
                    [effect_predictions_list, pd.DataFrame({'doi': [doi], 'entity': [match], 'prediction_values': [prediction_effects]})]
                ).reset_index(drop=True)
                effect_targets_list = pd.concat(
                    [effect_targets_list, pd.DataFrame({'doi': [doi], 'entity': [match], 'target_values': [target_effects]})]
                ).reset_index(drop=True)

        effect_predictions_targets_list = pd.merge(
            effect_predictions_list,
            effect_targets_list,
            on=['doi', 'entity']
        )

        # Create level predictions and targets
        df_effect_matches = pd.merge(
            effect_targets_list.rename(columns={'values': 'target_values'}),
            effect_predictions_list.rename(columns={'values': 'prediction_values'}),
            on=['doi', 'entity'],
        )
        df_effect_matches['effect_matches'] = df_effect_matches.apply(lambda row: list(set(row['prediction_values']) & set(row['target_values'])) , axis=1)
        # dois_entity_effect_matches = pd.merge(
        #     df_effect_matches[['doi', 'effect_matches']],
        #     df_entity_matches[['doi', 'entity_matches']],
        #     on='doi'
        # )
        dois_effect_matches_list = zip(
            df_effect_matches['doi'].to_list(),
            df_effect_matches['entity'].to_list(),
            df_effect_matches['effect_matches'].to_list()
        )
        level_predictions_list = pd.DataFrame()
        level_targets_list = pd.DataFrame()
        for (doi, entity, effect_matches) in dois_effect_matches_list:
            # if doi =='10.1016/j.ygeno.2021.05.006':
                # print('entity matches', entity)
                # print('effect matches', effect_matches)
            for effect_match in effect_matches:
                prediction_levels = []
                target_levels = []
                prediction_levels += df_predictions.loc[
                    (df_predictions['doi'] == doi)\
                    & (df_predictions['entity'] == entity)\
                    & (df_predictions['effect'] == effect_match),
                    'level'
                ].to_list()
                target_levels += df_test.loc[
                    (df_test['doi'] == doi)\
                    & (df_test['entity'] == entity)\
                    & (df_test['effect'] == effect_match),
                    'level'
                ].to_list()

                level_predictions_list = pd.concat(
                    [level_predictions_list, pd.DataFrame({
                        'doi': [doi],
                        'entity': [entity],
                        'effect': [effect_match],
                        'prediction_values': [prediction_levels]
                    })]
                ).reset_index(drop=True)
                level_targets_list = pd.concat(
                    [level_targets_list, pd.DataFrame({
                        'doi': [doi],
                        'entity': [entity],
                        'effect': [effect_match],
                        'target_values': [target_levels]
                    })]
                ).reset_index(drop=True)
        level_predictions_targets_list = pd.merge(
            level_predictions_list,
            level_targets_list,
            on=['doi', 'entity', 'effect']
        )

        entity_scores_dict = self.compute_corpus_scores(entity_predictions_targets_list)
        effect_scores_dict = self.compute_corpus_scores(effect_predictions_targets_list)
        level_scores_dict = self.compute_corpus_scores(level_predictions_targets_list)

        return {
            'entity_scores_dict': entity_scores_dict,
            'effect_scores_dict': effect_scores_dict,
            'level_scores_dict': level_scores_dict
        }

    

    def generate(self, input_ids):
        generated_sequence = []
        distributions = []
        comma_id = self.tokenizer.encode(',')[0]
        eos_id = self.tokenizer.eos_token_id
        sep_id = self.tokenizer.sep_token_id
        sepo_id = self.tokenizer(' | ')['input_ids'][0]
        output_indexes = [0]
        current_index = 0
        # past = None
        ended_with_eos = False
        while(len(generated_sequence) < 100):

            if current_index > 0:
                if (predicted_token_tensor == comma_id):
                    output_indexes.append(current_index)

            outputs = self.model(
                input_ids,
                # past_key_values=past,
                # use_cache=True,
                return_dict=True
            )
            # past = outputs.past_key_values
            next_token_logits = outputs.logits[:, -1, :]
            predicted_token_tensor = torch.argmax(next_token_logits)

            if (predicted_token_tensor == eos_id) or (predicted_token_tensor == sepo_id) or (predicted_token_tensor == sep_id) :
                ended_with_eos = True
                break

            distributions.append(
                F.softmax(next_token_logits[0], 0).detach()
            )
            
            input_ids = torch.cat(
                (input_ids, predicted_token_tensor.view(1, 1)),
                dim=-1
            ).detach()
            generated_sequence.append(predicted_token_tensor.detach())
            current_index += 1
        return generated_sequence, output_indexes, distributions, ended_with_eos
    

    def generateTable(self, inputs, output_attributes):
        self.status = 0
        table_outputs = []
        fields = output_attributes
        with torch.no_grad():
            for it, (input_text, doi) in enumerate(tqdm(inputs)):
                # print(input_text)
                self.status = round((it + 1)/len(inputs), 2) * 100

                prefix_input_ids = self.tokenizer.encode(
                    input_text,
                    return_tensors='pt',
                    truncation=True,
                    max_length=self.hparam['max_len'] -100
                )
                generated_outputs = [[]]
                for field in fields:
                    tmp_generated_outputs = []
                    for istance_index, instance in enumerate(generated_outputs):
                        confidences = []
                        past_conditional = ''
                        if len(instance) > 0:
                            for output in instance:
                                past_conditional += output['attribute'] + ': ' + output['value'] + ' | '
                        tmp_field = field['value']
                        conditional_text = past_conditional + tmp_field + '_list:' if field['multiple'] else past_conditional + tmp_field + ':',
                        # print('conditional text:', conditional_text[0])
                        conditional_ids = self.tokenizer.encode(
                            conditional_text[0],
                            return_tensors='pt',
                            truncation=True,
                            max_length=100
                        )


                        input_ids = torch.cat(
                            (
                                torch.tensor([[self.tokenizer.bos_token_id]]),
                                prefix_input_ids,
                                torch.tensor([[self.tokenizer.sep_token_id]]),
                                conditional_ids
                            ),
                            dim=-1
                        ).to(self.device)

                        generated_sequence, output_indexes, distributions, ended_with_eos\
                            = self.generate(input_ids)

                        distributions = [
                            distribution.cpu().numpy() for distribution in distributions
                        ]
                        # print(self.tokenizer.decode(generated_sequence))
                        outputs_text = self.tokenizer.decode(generated_sequence).split(',')

                        if not ended_with_eos:
                            outputs_text = outputs_text[:-1]
                            output_indexes = output_indexes[:-1]
                        # print('Abstract number:', it)
                        # print('generated sequence:', self.tokenizer.decode(generated_sequence))
                        if (len(generated_sequence)) == 0 and field['value'] == 'mutation_name' and field['multiple'] :
                            tmp_generated_outputs = []
                            break


                        outputs_text_filtered = []
                        for i, output_index in enumerate(output_indexes):
                            # confidence 1st token
                            if outputs_text[i] not in outputs_text[:i]:
                                outputs_text_filtered.append(outputs_text[i])
                                out_prob = distributions[output_index]
                                confidences.append(np.max(out_prob))

                                # start_index = output_index
                                # end_index = output_indexes[i + 1] - 1 if i < (len(outputs_text)-1) else len(generated_sequence)

                        assert len(outputs_text_filtered) == len(confidences), \
                            f'n of outputs not correspond n of confidences: {outputs_text} {confidences}\n'\
                            +f'Len Input: {prefix_input_ids.shape}, Len Cond: {conditional_ids.shape}'
                        
                        
                        for output_index, output in enumerate(outputs_text_filtered):
                            if output not in outputs_text[:output_index]:
                                tmp_generated_outputs.append(
                                    instance + [
                                        dict(
                                            attribute=field['value'],
                                            value=output.strip(),
                                            confidence=np.round(np.float64(confidences[output_index]), 2),
                                        )
                                    ]
                                )
                    
                    generated_outputs = tmp_generated_outputs
                
                table_outputs.append(dict(doi=doi, outputs=generated_outputs))
            return table_outputs

    def compute_scores(self, predictions, targets, confusion_only=False):
        tp = 0
        fp = 0
        fn = 0
        targets = targets.copy()
        for prediction in predictions:
            if prediction in targets:
                tp += 1
                targets.remove(prediction)
            else:
                fp += 1
        fn += len(targets)
        
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
        if confusion_only:
            return tp, fp, fn
        else:
            return precision, recall, f1

    def compute_corpus_scores(self, predictions_targets_list):
        general_scores = pd.DataFrame()
        general_scores[['precision', 'recall', 'f1', 'predictions', 'targets', 'doi']] = predictions_targets_list.apply(
            lambda row: self.compute_scores(
                row['prediction_values'], row['target_values']
                ) + (row['prediction_values'], row['target_values'], row['doi'])
            ,
            axis=1
        ).to_list()
        scores_by_doi = general_scores[['precision', 'recall', 'f1',  'doi']].groupby('doi').mean().reset_index()
        len_by_doi = general_scores[['doi', 'targets']].groupby('doi').agg({'targets': len}).reset_index().rename(columns = {'targets': 'targets_len'})
        scores_by_doi = pd.merge(
            scores_by_doi,
            len_by_doi,
            on='doi'
        )

        # Compute macro scores
        macro_scores = scores_by_doi[['precision', 'recall', 'f1']].mean().to_list()
        macro_scores_dict = dict(precision=round(macro_scores[0], 3), recall=round(macro_scores[1], 3), f1=round(macro_scores[2], 3))

        # Compute average macro scores
        total_n_entities = scores_by_doi['targets_len'].sum()
        scores_by_doi['weighted_precision'] = scores_by_doi.apply(lambda row: row['precision']*row['targets_len']/total_n_entities, axis=1)
        scores_by_doi['weighted_recall'] = scores_by_doi.apply(lambda row: row['recall']*row['targets_len']/total_n_entities, axis=1)
        scores_by_doi['weighted_f1'] = scores_by_doi.apply(lambda row: row['f1']*row['targets_len']/total_n_entities, axis=1)
        macro_weighted_scores_dict = dict(
            precision=round(scores_by_doi['weighted_precision'].sum(), 3),
            recall=round(scores_by_doi['weighted_recall'].sum(), 3),
            f1=round(scores_by_doi['weighted_f1'].sum(), 3)
        )

        # Compute micro scores
        confusion_values = pd.DataFrame()
        confusion_values[['tp', 'fp', 'fn']] = predictions_targets_list.apply(
            lambda row: self.compute_scores(
                row['prediction_values'], row['target_values'],
                confusion_only=True
                ),
            axis=1
        ).to_list()
        tp_sum, fp_sum, fn_sum = confusion_values.sum().to_list()
        micro_precision = tp_sum / (tp_sum + fp_sum)
        micro_recall = tp_sum / (tp_sum + fn_sum)
        micro_f1 = 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall)
        micro_scores_dict = dict(precision=round(micro_precision, 3), recall=round(micro_recall, 3), f1=round(micro_f1, 3))

        general_scores['predictions'] = general_scores.apply( lambda row: ', '.join(row['predictions']), axis=1)
        general_scores['targets'] = general_scores.apply( lambda row: ', '.join(row['targets']), axis=1)
        return {
            'scores': { 'macro': macro_scores_dict, 'micro': micro_scores_dict, 'weighted_macro': macro_weighted_scores_dict},
            'df_general_scores': json.loads(general_scores.to_json(orient='records')),
            'df_scores_by_doi': json.loads(scores_by_doi.to_json(orient='records'))
        }



