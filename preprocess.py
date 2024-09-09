from cell_classifier.cell_classifier import CellClassifier
import pickle
import numpy as np
from type.cell.function_cell_type import FunctionCellType
from type.cell.cell_type_pmf import CellTypePMF
from reader.sheet import Sheet
from typing import List
from tabular_cell_type_classification.src.models import ClassificationModel, CEModel, FeatEnc
from tabular_cell_type_classification.src.excel_toolkit import get_sheet_names, get_sheet_tarr, get_feature_array
from tabular_cell_type_classification.src.helpers import Preprocess, SentEnc, label2ind, get_cevectarr, get_fevectarr

import sys
import torch
import numpy as np


class PreprocessCE:
    def __init__(self, args):
        self.config = args
        ce_model_path = args['ce_model']
        fe_model_path = args['fe_model']
        self.w2v_path = args['w2v']
        self.vocab_size = args['vocab_size']
        self.infersent_model = args['infersent_model']

        self.mode = 'ce+f'
        self.device = 'cpu'
        ce_dim = 512
        senc_dim = 4096
        window = 2
        f_dim = 43
        fenc_dim = 40
        n_classes = 4
        if self.device != 'cpu': torch.cuda.set_device(self.device)

        self.ce_model = CEModel(senc_dim, ce_dim // 2, window * 4)
        self.ce_model = self.ce_model.to(self.device)
        self.fe_model = FeatEnc(f_dim, fenc_dim)
        self.fe_model = self.fe_model.to(self.device)

        self.ce_model.load_state_dict(torch.load(ce_model_path, map_location=self.device))
        self.fe_model.load_state_dict(torch.load(fe_model_path, map_location=self.device))

        self.label2ind = ["attributes", "data", "header", "metadata"]

    def generate_sent(self, tarr):
        sentences = set()
        for row in tarr:
            for c in row:
                sentences.add(c)
        return sentences

    def _get_embedding(self, t, ce_model, fe_model, senc, mode='ce+f', device='cpu'):
        if 'ce' in mode: ce_dim = ce_model.encdim * 2
        if 'f' in mode: fenc_dim = fe_model.encdim
        if mode == 'ce+f':
            cl_input_dim = ce_dim + fenc_dim
            runce = runfe = True
        elif mode == 'ce':
            cl_input_dim = ce_dim
            runfe = False
            runce = True
        elif mode == 'fe':
            cl_input_dim = fenc_dim
            runfe = True
            runce = False
        with torch.no_grad():
            tarr = np.array(t['table_array'])
            feature_array = np.array(t['feature_array'])
            n, m = tarr.shape

            if runfe: fevtarr = get_fevectarr(feature_array, n, m, fe_model, device)
            if runce: cevtarr = get_cevectarr(tarr, ce_model, senc, device, ce_model.num_context // 4, senc_dim=4096)
            if runfe: fevtarr = torch.from_numpy(fevtarr).float()
            if runce: cevtarr = torch.from_numpy(cevtarr).float()
            if mode == 'ce+f':
                features = torch.cat([cevtarr, fevtarr], dim=-1).to(device)
            elif mode == 'ce':
                features = cevtarr.to(device)
            elif mode == 'fe':
                features = fevtarr.to(device)
        return features

    def get_embeddings(self, fname, sname):

        senc = SentEnc(self.infersent_model, self.w2v_path,
                       self.vocab_size, device=self.device, hp=False)
        prep = Preprocess()

        tarr, n, m = get_sheet_tarr(fname, sname, file_type='xlsx')

        ftarr = get_feature_array(fname, sname, file_type='xlsx')

        table = dict(table_array=tarr, feature_array=ftarr)

        sentences = self.generate_sent(tarr)

        senc.cache_sentences(list(sentences))

        return tarr, ftarr, self._get_embedding(table, self.ce_model, self.fe_model,
                                                senc, self.mode, self.device)

    def process_tables(self, fname):
        file_type = fname.split(".")[-1]

        if file_type == "csv":
            with open(fname) as f:
                reader = csv.reader(f, delimiter=',')
                values = [["" if ((cell is None) or (cell == "None")) else cell for cell in row] for row in reader]
                pyx.save_as(array=values, dest_file_name=fname + ".xls")

                fname = fname + ".xls"
                file_type = "xls"

        sheet_list = []
        for sid, sname in enumerate(get_sheet_names(fname, file_type=file_type)):
            tarr, ftarr, temp = self.get_embeddings(fname, sname)

            embs = [[_.cpu().detach().numpy().tolist() for _ in item] for item in temp]

            sheet = Sheet(tarr,
                          {"farr": ftarr,
                           "name": sname,
                           "embeddings": embs
                           })

            sheet_list.append(sheet)

        return sheet_list
