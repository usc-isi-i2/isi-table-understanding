from cell_classifier_psl.psl_utils import *
from layout_detector_psl.featurizer import Featurize
from config_psl import config, get_full_path

class PSLWeightLearningLD:
    
    def __init__(self):
        
        self.psl_pred_file = get_full_path(config['layout_detector']['predicate_file'])
        
        self.psl_rule_file = get_full_path(config['layout_detector']['rule_file'])
        
        self.psl_learned_rule_file = get_full_path(config['layout_detector']['learned_rule_file'])
        
        self.psl_learn_data_path = get_full_path(config['layout_detector']['learn_path'])
        
        if not os.path.exists(self.psl_learn_data_path):
            os.makedirs(self.psl_learn_data_path, exist_ok=True)
          
        self.model = Model(config['layout_detector']['layout_detector_name'])
    
    def learn_weights(self, block_annotated, layouttypes):
        
        Featurize().featurize(block_annotated, layouttypes, self.psl_pred_file, self.psl_learn_data_path)
        
        get_predicates(self.model, self.psl_pred_file)
        
        add_data(self.model, self.psl_learn_data_path)
        
        get_rules(self.model, self.psl_rule_file)

        self.model.learn()
        
        write_rules(self.model, self.psl_learned_rule_file)
