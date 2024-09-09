from cell_classifier_psl.psl_utils import *
from cell_classifier_psl.features import Cell2Feat
from config_psl import config, get_full_path

class PSLWeightLearning:
    
    def __init__(self):
        
        self.psl_pred_file = get_full_path(config['cell_classifier']['predicate_file'])
        
        self.psl_rule_file = get_full_path(config['cell_classifier']['rule_file'])
        
        self.psl_learned_rule_file = get_full_path(config['cell_classifier']['learned_rule_file'])
        
        self.psl_learn_data_path = get_full_path(config['cell_classifier']['learn_path'])
        
        if not os.path.exists(self.psl_learn_data_path):
            os.makedirs(self.psl_learn_data_path, exist_ok=True)
          
        self.model = Model(config['cell_classifier']['cell_classifier_name'])
    
    def learn_weights(self, sheets, annotated):
        
        Cell2Feat().write_feats(sheets, annotated, self.psl_pred_file, self.psl_learn_data_path)
        
        get_predicates(self.model, self.psl_pred_file)
        
        add_data(self.model, self.psl_learn_data_path)
        
        get_rules(self.model, self.psl_rule_file)
        
        self.model.learn()
        
        write_rules(self.model, self.psl_learned_rule_file)
