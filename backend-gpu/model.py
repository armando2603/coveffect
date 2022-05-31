from collections import OrderedDict
from typing import Sequence
import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
import torch.nn.functional as F
from tqdm import tqdm
from os import path

def gradient_x_inputs_attribution(prediction_logit, inputs_embeds):

    inputs_embeds.retain_grad()
    # back-prop gradient
    prediction_logit.backward(retain_graph=True)
    grad = inputs_embeds.grad
    # This should be equivalent to
    # grad = torch.autograd.grad(prediction_logit, inputs_embeds)[0]

    # Grad X Input
    grad_x_input = grad * inputs_embeds

    # Turn into a scalar value for each input token by taking L2 norm
    feature_importance = torch.norm(grad_x_input, dim=1)

    # Normalize so we can show scores as percentages
    token_importance_normalized = feature_importance / torch.sum(
        feature_importance)

    # Zero the gradient for the tensor so next backward() calls don't have
    # gradients accumulating
    inputs_embeds.grad.data.zero_()
    return token_importance_normalized

class Predictor:
    def __init__(self):
        self.pretrained_model = ''
        self.fields = []
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        print(torch.cuda.is_available())
        self.generated_sequence = None
        self.MAX_LEN = 900
        self.model = None
        self.status = 0
        self.model_id = None
        # Load pre-trained model (weights)
        model_name = 'mrm8488/GPT-2-finetuned-CORD19'
        self.config = GPT2Config()
        self.model = GPT2LMHeadModel(self.config)
        self.model.eval()
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.add_special_tokens({
            'pad_token': '<PAD>',
            'bos_token': '<BOS>',
            'eos_token': '<EOS>',
            'sep_token': '<SEP>',
            'additional_special_tokens': ['<SEPO>']
        })
        self.base_model = GPT2LMHeadModel(self.config)
        self.base_model.resize_token_embeddings(len(self.tokenizer))
        self.base_model.eval()

        self.model.resize_token_embeddings(len(self.tokenizer))
        # self.name_model = 'checkpoint_4-epoch=14-val_loss=0.306.ckpt'
        self.name_model = 'multiple-instances-cord19-epoch=07.ckpt'
        checkpoint = torch.load('api/Checkpoints/' + self.name_model, map_location='cpu')
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
            torch.save(self.model.state_dict(), 'api/Checkpoints/' + self.name_model)
        else:
            del checkpoint

    def predict_and_saliency(self, input_text, output_attributes):
        self.fields = output_attributes
        self.model = self.base_model.to(self.device) # TODO verify if .to() copy
        if path.isfile('api/Checkpoints/' + 'augmented_' + self.name_model):
            augmented = 'augmented_'
        else:
            augmented = ''
        self.model.load_state_dict(
            torch.load(
                'api/Checkpoints/' + augmented + self.name_model, map_location=self.device
            )
        )

        # print('Input Text: ', input_text)
        prefix_input_ids = self.tokenizer.encode(
            input_text,
            return_tensors='pt',
            truncation=True,
            max_length=self.MAX_LEN - 100 # 100 less because of the conditional input
        )
        print(f'abstract len: {prefix_input_ids.shape}')
        input_ids = np.array(self.tokenizer.encode(input_text))
        input_tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
        input_tokens = list(
            map(
                self.tokenizer.convert_tokens_to_string,
                input_tokens
            )
        )
        self.generated_outputs = [[]]
        for field in self.fields:
            self.grad_explains = []
            tmp_generated_outputs = []
            for istance_index, instance in enumerate(self.generated_outputs):
                self.confidences = []
                past_conditional = ''
                if len(instance) > 0:
                    for output in instance:
                        past_conditional += output['attribute'] + ': ' + output['value'] + '<SEPO>'
                
                tmp_field = field['value']
                conditional_text = past_conditional + tmp_field + '_list:' if field['multiple'] else past_conditional + tmp_field + ':',
                print('conditional text:', conditional_text[0])
                conditional_ids = self.tokenizer.encode(
                    conditional_text[0],
                    return_tensors='pt',
                    truncation=True,
                    max_length=100
                )

                generated_sequence, output_indexes, distributions, grad_explain, ended_with_eos\
                    = self.generate_with_saliency(prefix_input_ids, conditional_ids)
                grad_explain = [
                    explain.cpu().numpy() for explain in grad_explain
                ]
                distributions = [
                    distribution.cpu().numpy() for distribution in distributions
                    ]
                # self.grad_explains.append(np.array(grad_explain))
                # print(self.tokenizer.decode(generated_sequence))

                print('generated sequence:', self.tokenizer.decode(generated_sequence))
                if (len(generated_sequence)) == 0 and field['value'] == 'mutation_name' and field['multiple'] :
                    return []
                
                
                outputs_text = self.tokenizer.decode(generated_sequence).split(',')
                if not ended_with_eos:
                    outputs_text = outputs_text[:-1]
                    output_indexes = output_indexes[:-1]

                outputs_text_filtered = []                
                for i, output_index in enumerate(output_indexes):
                    if outputs_text[i] not in outputs_text[:i]:
                        outputs_text_filtered.append(outputs_text[i])
                        # confidence 1st token
                        out_prob = distributions[output_index]
                        self.confidences.append(np.max(out_prob))

                        start_index = output_index
                        end_index = output_indexes[i + 1] - 1 if i < (len(outputs_text)-1) else len(generated_sequence)
                        # print('start index:', start_index)
                        # print('end index:', end_index)
                        print('sequence_filtered',self.tokenizer.decode(generated_sequence[start_index:end_index]))
                        # print('grad_explains dimensions:', np.array(grad_explain).shape)
                        self.grad_explains.append(self.gradientParser(np.array(grad_explain)[start_index:end_index], input_tokens))

                assert len(outputs_text_filtered) == len(self.confidences), \
                    f'n of outputs not correspond n of confidences: {outputs_text} {self.confidences}\n'\
                    +f'Len Input: {prefix_input_ids.shape}, Len Cond: {conditional_ids.shape}'

                for output_index, output in enumerate(outputs_text_filtered):
                        tmp_generated_outputs.append(
                            instance + [
                                dict(
                                    attribute=field['value'],
                                    value=output.strip(),
                                    confidence=np.round(np.float64(self.confidences[output_index]), 2),
                                    saliency_map=self.grad_explains[output_index][0]
                                )
                            ]
                        )

                # confidence as mul of confidences
                #     out_prob = distributions[self.indexes[j]:-1]
                #     self.confidences.append(np.multiply.reduce(
                #         np.max(out_prob, 1),
                #         0
                #     ))
            self.generated_outputs = tmp_generated_outputs
        # self.model = self.model.to('cpu')
        # self.model = self.base_model
        if self.model_id == 1:
            del self.model
            with torch.cuda.device(self.device):
                torch.cuda.empty_cache()
        return self.generated_outputs
        # , self.grad_explains

    def generate_with_saliency(self, prefix_input_ids, conditional_ids):

        input_ids = torch.cat(
            (
                torch.tensor([[self.tokenizer.bos_token_id]]),
                prefix_input_ids,
                torch.tensor([[self.tokenizer.sep_token_id]]),
                conditional_ids
            ),
            dim=-1
        ).to(self.device)

        input_length = prefix_input_ids.shape[1]
        generated_sequence = []
        distributions = []
        comma_id = self.tokenizer.encode(',')[0]
        eos_id = self.tokenizer.eos_token_id
        sep_id = self.tokenizer.sep_token_id
        sepo_id = self.tokenizer('<SEPO>')['input_ids'][0]
        output_indexes = [0]
        current_index = 0
        grad_explain = []
        ended_with_eos = False
        # print(self.tokenizer.decode(input_ids[0]))
        while(len(generated_sequence) < 100):
            if current_index > 0:
                if (predicted_token_tensor == comma_id):
                    output_indexes.append(current_index)

            inputs_embeds, token_ids_tensor_one_hot = \
                self._get_embeddings(input_ids[0])
            inputs = inputs_embeds.unsqueeze(0)
            outputs = self.model(
                inputs_embeds=inputs,
                return_dict=True
            )
            next_token_logits = outputs.logits[:, -1, :]
            predicted_token_tensor = torch.argmax(next_token_logits)

            if (predicted_token_tensor == eos_id) or (predicted_token_tensor == sepo_id) or (predicted_token_tensor == sep_id) :
                ended_with_eos = True
                break

            distributions.append(
                F.softmax(next_token_logits[0], 0).detach()
            )
            prediction_logit = outputs.logits[
                0,
                -1,
                predicted_token_tensor
            ]
            grad_x_input = gradient_x_inputs_attribution(
                prediction_logit,
                inputs_embeds
            )
            grad_explain.append(
                grad_x_input[1:(input_length + 1)].detach()
            )
            input_ids = torch.cat(
                (input_ids, predicted_token_tensor.view(1, 1)),
                dim=-1
            ).detach()
            generated_sequence.append(predicted_token_tensor.detach())
            current_index += 1
        return generated_sequence, output_indexes, distributions, grad_explain, ended_with_eos

    def generateTable(self, inputs_text, output_attributes):
        self.status = 0
        table_outputs = []
        self.fields = output_attributes
        self.model = self.base_model.to(self.device) # TODO verify if .to() copy
        if path.isfile('api/Checkpoints/' + 'augmented_' + self.name_model):
            augmented = 'augmented_'
        else:
            augmented = ''
        self.model.load_state_dict(
            torch.load(
                'api/Checkpoints/' + augmented + self.name_model, map_location=self.device
            )
        )


        with torch.no_grad():
            for it, input_text in enumerate(tqdm(inputs_text)):

                self.status = round((it + 1)/len(inputs_text), 2) * 100


                print(input_text)
                prefix_input_ids = self.tokenizer.encode(
                    input_text,
                    return_tensors='pt',
                    truncation=True,
                    max_length=self.MAX_LEN -100
                )
                self.generated_outputs = [[]]
                for field in self.fields:
                    tmp_generated_outputs = []
                    for istance_index, instance in enumerate(self.generated_outputs):
                        self.confidences = []
                        past_conditional = ''
                        if len(instance) > 0:
                            for output in instance:
                                past_conditional += output['attribute'] + ': ' + output['value'] + '<SEPO>'
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
                        print('generated sequence:', self.tokenizer.decode(generated_sequence))
                        if (len(generated_sequence)) == 0 and field['value'] == 'mutation_name' and field['multiple'] :
                            tmp_generated_outputs = []
                            break


                        outputs_text_filtered = []
                        for i, output_index in enumerate(output_indexes):
                            # confidence 1st token
                            if outputs_text[i] not in outputs_text[:i]:
                                outputs_text_filtered.append(outputs_text[i])
                                out_prob = distributions[output_index]
                                self.confidences.append(np.max(out_prob))

                                start_index = output_index
                                end_index = output_indexes[i + 1] - 1 if i < (len(outputs_text)-1) else len(generated_sequence)

                        assert len(outputs_text_filtered) == len(self.confidences), \
                            f'n of outputs not correspond n of confidences: {outputs_text} {self.confidences}\n'\
                            +f'Len Input: {prefix_input_ids.shape}, Len Cond: {conditional_ids.shape}'
                        
                        
                        for output_index, output in enumerate(outputs_text_filtered):
                            if output not in outputs_text[:output_index]:
                                tmp_generated_outputs.append(
                                    instance + [
                                        dict(
                                            attribute=field['value'],
                                            value=output.strip(),
                                            confidence=np.round(np.float64(self.confidences[output_index]), 2),
                                        )
                                    ]
                                )
                    
                    self.generated_outputs = tmp_generated_outputs
                
                table_outputs.append(self.generated_outputs)
            if self.model_id == 1:
                del self.model
                with torch.cuda.device(self.device):
                    torch.cuda.empty_cache()
            return table_outputs

    def generate(self, input_ids):
        generated_sequence = []
        distributions = []
        comma_id = self.tokenizer.encode(',')[0]
        eos_id = self.tokenizer.eos_token_id
        sep_id = self.tokenizer.sep_token_id
        sepo_id = self.tokenizer('<SEPO>')['input_ids'][0]
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

    def onlineLearning(self, input_text, output_list):
        self.model = self.base_model.to(self.device)
        if path.isfile('api/Checkpoints/' + 'augmented_' + self.name_model):
            augmented = 'augmented_'
        else:
            augmented = ''
        self.model.load_state_dict(
            torch.load(
                'api/Checkpoints/' + augmented + self.name_model, map_location=self.device
            )
        )
        input_prefix = self.tokenizer.encode(
            input_text,
            return_tensors='pt',
            truncation=True,
            max_length=self.MAX_LEN
        ).to(self.device)
        for output_text in output_list:
            print(output_text)
            output_ids = self.tokenizer.encode(
                output_text,
                return_tensors='pt'
            ).to(self.device)
            inp_out_ids = torch.cat(
                (
                    torch.tensor([[self.tokenizer.bos_token_id]], device=self.device),
                    input_prefix,
                    torch.tensor([[self.tokenizer.sep_token_id]], device=self.device),
                    output_ids
                ),
                dim=-1
            )
            labels = inp_out_ids.clone().detach()
            labels[0, :-output_ids.shape[1]] = torch.ones(
                input_prefix.shape[1] + 2
            ) * -100

            optimizer = torch.optim.Adam(self.model.parameters(), lr=2e-5)
            new_output = torch.empty(output_ids.shape, device=self.device)
            not_match = True
            max_epochs = 10
            epoch = 0
            while (not_match and epoch < max_epochs):
                epoch += 1
                self.model.train()
                optimizer.zero_grad()
                output = self.model(inp_out_ids, labels=labels, return_dict=True)
                loss = output.loss
                print(loss)
                if (loss < 0.1):
                    not_match = False
                loss.backward()
                optimizer.step()
                # self.model.eval()
                # with torch.no_grad():
                #     past = None
                #     inp = torch.cat(
                #         (
                #             torch.tensor(
                #                 [[self.tokenizer.bos_token_id]],
                #                 device=self.device
                #             ),
                #             input_prefix,
                #             torch.tensor(
                #                 [[self.tokenizer.sep_token_id]],
                #                 device=self.device
                #             )
                #         ),
                #         dim=-1
                #     )
                #     generated_sequence = torch.zeros(
                #         (1, 0),
                #         device=self.device
                #     ).long()
                #     while(len(generated_sequence) < 300):
                #         out = self.model(
                #             inp,
                #             # attention_mask=attn_mask,
                #             past_key_values=past,
                #             use_cache=True,
                #             return_dict=True
                #         )
                #         past = out.past_key_values
                #         last_tensor = out.logits[0, -1, :]
                #         predicted_token_tensor = torch.argmax(last_tensor)
                #         inp = predicted_token_tensor.view(1, 1)
                #         generated_sequence = torch.cat(
                #             (generated_sequence, predicted_token_tensor.view(1,1)),
                #             dim=-1
                #         )
                #         if predicted_token_tensor == self.tokenizer.eos_token_id:
                #             break
                #     print(f'output generato : {self.tokenizer.decode(list(output_ids[0]))} e con generate sequence:', self.tokenizer.decode(list(generated_sequence[0])))
                #     new_output = generated_sequence
                #     if new_output.shape == output_ids.shape:
                #         if torch.all(new_output.eq(output_ids)):
                #             not_match = False

            # 1
        torch.save(
            self.model.state_dict(),
            'api/Checkpoints/' + 'augmented_' + self.name_model
        )
        del self.model
        with torch.cuda.device(self.device):
            torch.cuda.empty_cache()

    def _get_embeddings(self, input_ids):
            """
            Takes the token ids of a sequence, returnsa matrix of their embeddings.
            """
            embedding_matrix = self.model.transformer.wte.weight

            vocab_size = embedding_matrix.shape[0]

            one_hot_tensor = torch.zeros(
                len(input_ids), vocab_size
            ).to(self.device).scatter_(1, input_ids.unsqueeze(1), 1.)

            token_ids_tensor_one_hot = one_hot_tensor.clone().requires_grad_(True)
            # token_ids_tensor_one_hot.requires_grad_(True)

            inputs_embeds = torch.matmul(token_ids_tensor_one_hot, embedding_matrix)
            return inputs_embeds, token_ids_tensor_one_hot

    def gradientParser(self, grad_explain, input_tokens):
        scores = grad_explain[:, :]
        scores = np.mean(scores, axis=0)

        max_scores = np.max(scores)
        max_scores = 1 if max_scores == 0.0 else max_scores
        scores = scores / max_scores
        assert len(input_tokens) == len(scores), (
            f'Gradient: len input_tokens {len(input_tokens)}'
            + f' != len scores {len(scores)}'
        )

        input_list = list(zip(input_tokens, scores))
        word_list = []
        values_list = input_list
        new_values_list = []
        i = 1
        while i < len(values_list):
            end_word = False
            mean_scores = [values_list[i-1][1]]
            new_world = values_list[i-1][0]
            while end_word is False:
                next_word = values_list[i][0]
                next_score = values_list[i][1]
                if ((' ' or '_' or '-' or ':' or ';' or '(' or ')')
                        not in next_word[0]):
                    new_world += next_word
                    mean_scores.append(next_score)
                else:
                    end_word = True
                    new_values_list.append(
                        [new_world, np.mean(mean_scores)]
                    )
                i += 1
                if i == len(values_list):
                    if not end_word:
                        new_values_list.append(
                            [new_world, np.mean(mean_scores)]
                        )
                        end_word = True
                    else:
                        mean_scores = [values_list[i-1][1]]
                        new_world = values_list[i-1][0]
                        new_values_list.append(
                            [new_world, np.mean(mean_scores)]
                        )

        word_list.append(new_values_list)

        gradient_input = word_list
        for i, input_list in enumerate(gradient_input):
            for k, value in enumerate(input_list):
                opacity = np.int(np.ceil(value[1]*5))
                bg_colors = f'bg-blue-{opacity}' if (
                    opacity) > 1 else 'bg-white'
                gradient_input[i][k][1] = bg_colors
            gradient_input[i] = [
                dict(
                    text=elem[0], color=elem[1]
                    ) for elem in gradient_input[i]
            ]
        return gradient_input