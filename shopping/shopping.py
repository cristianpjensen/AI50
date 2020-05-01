import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    # Read in the data from the file into two lists: evidence and labels.
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            evidence.append(row[:-1])
            labels.append(row[-1])

    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "June", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    for data in evidence:
        # Turn Administrative, Informational, ProductRelated into an integer.
        for i in range(len(data))[:5:2]:
            data[i] = int(data[i])

        # Turn OperatingSystem, Browser, Region, TrafficType into an integer.
        for i in range(len(data))[11:15]:
            data[i] = int(data[i])

        # Turn Month into an integer corresponding to the month.
        for month in months:
            if data[10] == month:
                data[10] = months.index(month)

        # Turn VisitorType into an integer depening on the type of visitor.
        if data[15] == 'Returning_Visitor':
            data[15] = 1
        else:
            data[15] = 0

        # Turn Weekend into an integer depending on if it is weekend or not.
        if data[16] == 'TRUE':
            data[16] = 1
        else:
            data[16] = 0

        # Turn Administrative_Duration, Informational_Duration, ProductRelated
        # _Duration into a float.
        for i in range(len(data))[1:4:2]:
            data[i] = float(data[i])
        # Turn BounceRates, ExitRates, PageValues, and SpecialDay into a float
        for i in range(len(data))[5:10]:
            data[i] = float(data[i])

    # Turn all labels into either 1, or 0, dependent on TRUE or FALSE.
    for i in range(len(labels)):
        if labels[i] == "TRUE":
            labels[i] = 1
        else:
            labels[i] = 0

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sens_count = 0
    pos_count = 0

    spec_count = 0
    neg_count = 0

    # Add 1 to pos_ and neg_count, for every label.
    # Add 1 to sens_ and spec_count, for every correct prediction.
    for i in range(len(labels)):
        if labels[i] == 1:
            pos_count += 1
            if predictions[i] == 1:
                sens_count += 1

        if labels[i] == 0:
            neg_count += 1
            if predictions[i] == 0:
                spec_count += 1

    # Compute the proportions.
    sensitivity = sens_count / pos_count
    specificity = spec_count / neg_count

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
