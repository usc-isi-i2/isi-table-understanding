from pydoc import locate


class Configurator(object):
    def __init__(self, args):
        self.args = args
        self.augmenter_preload_resources = None

    def set_augmenter_preload_resources(self, res):
        self.augmenter_preload_resources = res

    def get_class_instance(self, module_path):
        my_class = locate(module_path)
        return my_class

    def get_instance(self, component_key):
        if component_key in self.args and self.args[component_key]['class']:
            argument_value = self.args[component_key]['class']
            provider = self.get_class_instance(argument_value)
            kwargs = {}

            for keyword in self.args[component_key]:
                if keyword != "class":
                    kwargs[keyword] = self.args[component_key][keyword]

            return provider(**kwargs)

    def get_component(self, component_key):
        return self.get_instance(component_key)
