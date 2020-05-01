import numpy as np

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


people = {
  'Harry': {'name': 'Harry', 'mother': 'Lily', 'father': 'James', 'trait': None},
  'James': {'name': 'James', 'mother': None, 'father': None, 'trait': True},
  'Lily': {'name': 'Lily', 'mother': None, 'father': None, 'trait': False}
}


def main():
    prob = joint_probability(people, {"Harry"}, {"Lily"}, {"James", "Harry"})
    print(prob)


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probs = []
    
    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]
        mother_prob = parent_probability(mother, one_gene, two_genes)
        father_prob = parent_probability(father, one_gene, two_genes)
        
        # If the person does have one gene ... 
        if person in one_gene:
            trait_prob = trait_probability(1, person, have_trait)

            # ... and parentless.
            if mother == None and father == None:
                probs.append(parentless_probability(1, trait_prob))
            
            # ... and parents exist
            else:
                gene_prob = ((1 - mother_prob) * father_prob +
                             mother_prob * (1 - father_prob))
                joint_prob = gene_prob * trait_prob
                probs.append(joint_prob)

        # If the person has two genes ...
        elif person in two_genes:
            trait_prob = trait_probability(2, person, have_trait)

            # ... and parentless.
            if mother == None and father == None:
                probs.append(parentless_probability(2, trait_prob))
            
            # ... and parents exist.
            else:
                gene_prob = mother_prob * father_prob
                joint_prob = gene_prob * trait_prob
                probs.append(joint_prob)

        # If the person does not have the gene ...
        else:
            trait_prob = trait_probability(0, person, have_trait)

            # ... and parentless.
            if mother == None and father == None:
                probs.append(parentless_probability(0, trait_prob))

            # ... and parents exist.
            else:
                gene_prob = (1 - mother_prob) * (1 - father_prob)
                joint_prob = gene_prob * trait_prob
                probs.append(joint_prob)
    
    return np.product(probs)


def parent_probability(parent, one_gene, two_genes):
    if parent == None:
        return
    elif parent in two_genes:
        return 1.0 - PROBS["mutation"]
    elif parent in one_gene:
        return 0.5 - PROBS["mutation"]
    else:
        return PROBS["mutation"]


def trait_probability(num_genes, person, have_trait):
    if person in have_trait:
        return PROBS["trait"][num_genes][True]
    else:
        return PROBS["trait"][num_genes][False]


def parentless_probability(num_genes, trait_prob):
    gene_prob = PROBS["gene"][num_genes]
    return gene_prob * trait_prob


if __name__ == "__main__":
    main()