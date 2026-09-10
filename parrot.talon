# Outside parrot mode. Through the channel rather than straight to an action,
# so tut can carry a combo. The map is input_map_global in parrot_rig_actions.
parrot(pop): user.input_map_channel_handle("parrot_rig_global", "pop")
parrot(cluck): user.input_map_channel_handle("parrot_rig_global", "cluck")
parrot(palate_click): user.input_map_channel_handle("parrot_rig_global", "palate")
parrot(tut): user.input_map_channel_handle("parrot_rig_global", "tut")

parrot [rig] help: user.parrot_rig_show_help()

# If you are updating inputs/actions, it may be necessary to reload/reset parrot rig
parrot [rig] (reload | reset): user.parrot_rig_reload()