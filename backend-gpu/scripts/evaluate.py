import pandas as pd
import numpy as np
import torch
from transformers import GPT2Config, GPT2LMHeadModel, AutoTokenizer
from collections import OrderedDict
from tqdm.notebook import tqdm
import torch.nn.functional as F


def evaluate (
    model_name_input="mrm8488/GPT-2-finetuned-CORD19",
    checkpoint_name_input='multiple-instances-cord19-epoch=06.ckpt'
):
    model_name = model_name_input
    checkpoint_name = checkpoint_name_input

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

    checkpoint_name = 'multiple-instances-cord19-epoch=06.ckpt'
    checkpoint = torch.load('../api/Checkpoints/' + checkpoint_name, map_location='cpu')
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
        print('new state dict load')
        torch.save(model.state_dict(), '../api/Checkpoints/' + checkpoint_name)
    else:
        model.load_state_dict(checkpoint)
        print('checkpoint loaded')
        del checkpoint

    model.to(device)

    def generate(input_ids):
        generated_sequence = []
        distributions = []
        comma_id = tokenizer.encode(',')[0]
        eos_id = tokenizer.eos_token_id
        sep_id = tokenizer.sep_token_id
        sepo_id = tokenizer('<SEPO>')['input_ids'][0]
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
                                past_conditional += output['attribute'] + ': ' + output['value'] + '<SEPO>'
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
                        print('generated sequence:', tokenizer.decode(generated_sequence))
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

    df_test = pd.read_csv('../api/local_data/test_set.csv', sep='\t', index_col=[0])

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

    df_predictions = pd.DataFrame(
        {
            'doi': [prediction['doi'] for prediction in prediction_list],
            'entity': [prediction['mutation_name'] for prediction in prediction_list],
            'effect': [prediction['effect'] for prediction in prediction_list],
            'level': [prediction['level'] for prediction in prediction_list]
        }
    ).to_csv('.../api/test_results/' + checkpoint_name[:-5] + '.tsv', sep='\t')

