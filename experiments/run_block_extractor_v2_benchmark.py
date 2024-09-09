from benchmarks.block_extractor_benchmark import BlockExtractorBenchmark
from data_loader.load_synthetic_data import LoadSyntheticData
from cell_classifier.crf_cell_classifier import CRFCellClassifier
from block_extractor.block_extractor_v2 import BlockExtractorV2


def run_block_extractor_v2_benchmark(test_full_pipeline=False):
    lst = LoadSyntheticData()
    sheets, cell_tags, blocks, layout = lst.load_files()
    crf_classifier = CRFCellClassifier()
    block_extractor = BlockExtractorV2()

    total_matching_blocks = 0
    total_type_mismatched_blocks = 0
    total_blocks_detected = 0
    total_blocks_expected = 0

    for sheet, cell_tag, gold_block in zip(sheets, cell_tags, blocks):
        if test_full_pipeline:
            cell_tag = crf_classifier.classify_cells(sheet)
        beb = BlockExtractorBenchmark(sheet, cell_tag, block_extractor, gold_block)
        matching_blocks, type_mismatch, blocks_detected, blocks_expected = beb.get_matching_blocks()

        total_matching_blocks += matching_blocks
        total_type_mismatched_blocks += type_mismatch
        total_blocks_detected += blocks_detected
        total_blocks_expected += blocks_expected

    print(total_matching_blocks, total_type_mismatched_blocks, total_blocks_detected, total_blocks_expected)

if __name__ == "__main__":
    run_block_extractor_v2_benchmark(test_full_pipeline=False)

