from talon import actions
import os
import time

def show_reloading_notification():
    """Show brief 'Reloading...' notification before files are touched"""
    try:
        def reloading_ui():
            screen, div, text = actions.user.ui_elements(["screen", "div", "text"])
            return screen(align_items="flex_end", justify_content="flex_end")[
                div(
                    padding=15,
                    margin=50,
                    background_color="#0088ffdd",
                    border_radius=10,
                )[
                    text("Reloading parrot rig...", font_size=20, color="white", font_weight="bold")
                ]
            ]

        actions.user.ui_elements_show(reloading_ui, duration="1s", min_version="0.10.0")
    except (AttributeError, ImportError):
        pass

def reload_files():
    actions.user.parrot_rig_disable()
    actions.user.input_map_channel_unregister("parrot_rig")

    show_reloading_notification()
    time.sleep(0.1)

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
