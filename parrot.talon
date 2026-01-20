parrot(pop): user.on_pop()
parrot(cluck): user.parrot_rig_enable()
parrot(palate_click): user.parrot_rig_repeater()
parrot(tut): user.parrot_rig_reverser()

parrot mode help: user.parrot_rig_show_help()

# If you are updating inputs/actions, it may be necessary to reload/reset parrot mode
parrot mode [reload | reset]: user.parrot_rig_reload()