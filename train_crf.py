from layout_detector.crf.estimator import CRFLayoutEstimator
from data_loader.load_training_data import LoadTrainingData
from data_loader.load_synthetic_data import LoadSyntheticData
import pickle


def main():
    data_loader = LoadTrainingData()

    reg_params = [0.003, 0.01, 0.03, 0.1, 0.3, 1]
    block_list, layout_list = data_loader.load_annotation_files()

    crf_estimator = CRFLayoutEstimator(C_range=reg_params)
    crf_estimator.set_input([None] * len(block_list), [None] * len(block_list), block_list, layout_list)
    crf_model = crf_estimator.fit_crf()
    print("_________________")


def find_hyper_parameters():
    lsd = LoadSyntheticData()

    reg_params = [0.01, 0.03, 0.1]
    sheet_list, tags_list, block_list, layout_list = lsd.load_files()

    crf_estimator = CRFLayoutEstimator(C_range=reg_params, eval_against_test=False)
    crf_estimator.set_input(sheet_list, tags_list, block_list, layout_list)
    crf_estimator.fit_crf()
    print("_________________")


def evaluate_on_test_set():
    lsd = LoadSyntheticData()

    reg_params = [0.03]
    sheet_list, tags_list, block_list, layout_list = lsd.load_files()

    crf_estimator = CRFLayoutEstimator(C_range=reg_params, eval_against_test=True)
    crf_estimator.set_input(sheet_list, tags_list, block_list, layout_list)
    crf_model = crf_estimator.fit_crf()
    print("_________________")

    # Test on real data
    data_loader = LoadTrainingData()
    t_block_list, t_layout_list = data_loader.load_annotation_files()
    crf_estimator.evaluate_test_set([None] * len(t_block_list), [None] * len(t_block_list), t_block_list, t_layout_list)


"""
Training with all available data
"""
def write_layout_detector_to_file():
    data_loader_1 = LoadTrainingData()
    block_list_1, layout_list_1 = data_loader_1.load_annotation_files()

    data_loader_2 = LoadSyntheticData()
    sheet_list_2, tags_list_2, block_list_2, layout_list_2 = data_loader_2.load_files()

    print(len(block_list_1), len(layout_list_1))
    print(len(sheet_list_2), len(tags_list_2), len(block_list_2), len(layout_list_2))

    N = len(block_list_1) + len(block_list_2)

    crf_estimator = CRFLayoutEstimator(C_range=[0.03], eval_against_test=False)
    block_list_1.extend(block_list_2)
    layout_list_1.extend(layout_list_2)
    crf_estimator.set_input([None] * N, [None] * N, block_list_1, layout_list_1)
    crf_model = crf_estimator.fit_crf()

    print("Writing model to file.")
    with open("layout_detector/crf/model.pkl", "wb") as model_file:
        pickle.dump(crf_model, model_file)


if __name__ == "__main__":
    # main()
    # find_hyper_parameters()
    # evaluate_on_test_set()

    write_layout_detector_to_file()

