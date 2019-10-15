""" Auxiliary utilities """
from .datasets import BagsWithVocab
from .condition import ConditionList
from sklearn.metrics import mutual_info_score


def compute_mutual_info(bags, conditions=None, include_labels=True):
    """
    Arguments
    =========

    :bags: BagsWithVocab instance
    :conditions: ConditionList instance
    :include_labels: if True, include labels in input

    """
    assert isinstance(bags, BagsWithVocab), "Expecting BagsWithVocab instance, apply vocab before"
    assert conditions or include_labels, "If no conditions are give, include_labels should be True"
    print("[MI]", "Put labels into csr format...")
    Y = bags.tocsr()
    print("[MI]", "Y shape (labels):", Y.shape)

    if conditions:
        assert isinstance(conditions, ConditionList), "Expecting ConditionList instance"
        print("[MI]", "Preprocessing condition data...")
        condition_data = bags.get_attributes(conditions.keys())
        condition_data = conditions.fit_transform(condition_data)
        if include_labels:
            # Impose condition on (input) labels
            print("[MI]", "Imposing conditions on labels")
            X = conditions.encode_impose(Y, condition_data)
        else:
            print("[MI]", "Computing condition data")
            # Use *only* condition data to compute MI
            encoded_cdata = conditions.encode(condition_data)
            remaining_conditions = list(conditions.values())[1:]
            X = encoded_cdata[0]
            if remaining_conditions:
                for cond, cdata in zip(remaining_conditions, encoded_cdata[1:]):
                    # Impose all remaining conditions
                    X = cond.impose(X, cdata)
    else:
        X = Y
    print("[MI]", "X shape (features):", X.shape)

    print("[MI]", "Computing contingency table...")
    contingency = X.T @ Y

    print("[MI]", "Computing mutual information...")
    mi = mutual_info_score(None, None, contingency=contingency)
    print("[MI]", "Mutual information (base e):", mi)
    return mi
