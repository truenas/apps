class Storage:
    def __init__(self, render_instance, name, config):
        self.render_instance = render_instance
        self.name = name
        # FIXME: do something with config

    def volume(self):
        return {}

    def volume_mount(self):
        return {}

    def render(self):
        return {}
