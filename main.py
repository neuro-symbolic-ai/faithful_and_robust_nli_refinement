from refinement.refinement_model import RefinementModel
from generation.gpt import GPT
from critique.isabelle import IsabelleCritique
import yaml
import argparse
import json


def main(args):

    # premise and explanation are default to None
    # explanation sentences need to be seperate by '\n'
    with open(f'data/{args.data_name}.json', 'r') as file:
        data = json.load(file)

    for item in data:
        q_id = item['id']
        premise = item['premise']
        hypothesis = item['hypothesis']
        explanation = item['explanation']
        data_name = f'{args.data_name}_{q_id}'
        if premise == 'none':
            premise = None
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            api_key = config.get(args.llm, {}).get('api_key')
        llm = GPT(args.llm, api_key)

        isabelle_solver = IsabelleCritique(
            generative_model=llm,
            isabelle_session='HOL',
            theory_name=data_name
        )
        prompt_dict = {
            'generate explanation': 'get_explanation_prompt.txt',
            'refine no premise': 'refine_hard_no_premise_prompt.txt',
            'refine with premise': 'refine_hard_with_premise_prompt.txt'
        }

        refinement_model = RefinementModel(
            generative_model=llm,
            critique_model=isabelle_solver,
            prompt_dict=prompt_dict
        )

        # premise and explanation are optional
        # iterative refinement times are set to 10 by default
        results = refinement_model.refine(
            hypothesis=hypothesis,
            premise=premise,
            explanation=explanation,
            data_name=data_name,
        )
        item['results'] = results
        with open(f'{data_name}_results.json', 'w') as file:
            json.dump(item, file, indent=4)
        isabelle_solver.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--llm', '-l', type=str,
                        choices=['gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4o'],
                        default='gpt-4o')
    parser.add_argument('--data_name', '-d', type=str,
                        choices=['esnli', 'qasc', 'worldtree', 'example'],
                        default='example')
    args = parser.parse_args()
    main(args)