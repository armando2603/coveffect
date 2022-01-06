import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import Predictor


app = Flask(__name__)
CORS(app)
pred = Predictor()

def gradientParser(
    output_ids_list,
    output_attributes,
    confidences,
    input_ids,
    grad_explains
):
    output_split = []
    for i, attribute in enumerate(output_attributes):
        value = pred.tokenizer.decode(output_ids_list[i][:-1])
        output_split.append([attribute, value])

    outputs = [dict(
        attribute=elem[0],
        value=elem[1].strip(),
        fixed=False,
        confidence=np.round(np.float64(confidences[i]), 2)
        ) for i, elem in enumerate(output_split)]
    # gradient saliency

    input_tokens = pred.tokenizer.convert_ids_to_tokens(input_ids)
    input_tokens = list(
        map(
            pred.tokenizer.convert_tokens_to_string,
            input_tokens
        )
    )
    gradient_inputs = []
    for grad_explain in grad_explains:
        scores = grad_explain[:-1, :]
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
        gradient_inputs.append(gradient_input)
    return outputs, gradient_inputs


@app.route('/extract_attributes', methods=['POST'])
def CallModel():
    data = request.get_json()
    input_text = data['input']
    output_attributes = data['output_attributes']
    pred.attributes = output_attributes

    output_ids_list, confidences, grad_explains = pred.predict(
        [input_text], output_attributes
    )

    input_ids = np.array(pred.tokenizer.encode(input_text))

    outputs, gradient_inputs = gradientParser(
        output_ids_list,
        output_attributes,
        confidences,
        input_ids,
        grad_explains
    )

    response = {
        'outputs': outputs,
        'saliency_map': gradient_inputs

    }
    return jsonify(response)

@app.route('/generateTable', methods=['POST'])
def generateTable():
    data = request.get_json()
    inputs = data['inputs']
    attributes = data['output_attributes']
    outputs = pred.generateTable(inputs, attributes)
    return jsonify(outputs)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--colab",
        action="store_true",
        help="colab mode"
    )
    args = parser.parse_args()
    if args.colab:
        from flask_ngrok import run_with_ngrok
        run_with_ngrok(app)
    app.run()
