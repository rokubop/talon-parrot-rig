from talon import actions
import os

def reload_files():
    actions.user.parrot_rig_disable()

    src_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(src_dir)
    ui_dir = os.path.join(root_dir, "ui")

    touched_count = 0

    for directory in [root_dir, src_dir, ui_dir]:
        if not os.path.isdir(directory):
            continue
        for filename in os.listdir(directory):
            if filename.endswith('.py'):
                filepath = os.path.join(directory, filename)
                try:
                    os.utime(filepath, None)
                    touched_count += 1
                except Exception as e:
                    print(f"Error updating {filename}: {e}")

    print(f"Parrot rig reset and {touched_count} files touched for reload")
