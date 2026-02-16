from talon import actions
import os

class Utils:
    def update_time_of_file(self, filepath, filename):
        try:
            os.utime(filepath, None)
        except Exception as e:
            print(f"Error updating {filename}: {e}")

    def reload_files(self):
        actions.user.parrot_rig_disable()

        src_dir = os.path.dirname(__file__)
        main_dir = os.path.dirname(os.path.join("..", __file__))

        touched_count = 0

        for filename in os.listdir(src_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(src_dir, filename)
                self.update_time_of_file(filepath, filename)
                touched_count += 1

        for filename in os.listdir(main_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(main_dir, filename)
                self.update_time_of_file(filepath, filename)
                touched_count += 1

        print(f"Parrot mode reset and {touched_count} files touched for reload")

utils = Utils()
