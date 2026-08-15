parrot(pop): user.parrot_rig_simple_click()
parrot(cluck): user.parrot_rig_enable()
parrot(palate_click): user.parrot_rig_repeat_phrase()
parrot(tut): user.parrot_rig_reverse_command()

parrot [rig] help: user.parrot_rig_show_help()

parrot [rig] profile save <user.text>: user.parrot_rig_profile_save(text)
parrot [rig] profile load <user.text>: user.parrot_rig_profile_load(text)
parrot [rig] profile delete <user.text>: user.parrot_rig_profile_delete(text)
parrot [rig] profile list: user.parrot_rig_profile_list()

# If you are updating inputs/actions, it may be necessary to reload/reset parrot rig(
parrot [rig] (reload | reset): user.parrot_rig_reload()