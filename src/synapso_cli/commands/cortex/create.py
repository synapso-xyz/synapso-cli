from synapso_core.cortex_manager import CortexManager


def cmd_create_cortex(folder_location: str, cortex_name: str):
    cortex_manager = CortexManager()
    return cortex_manager.create_cortex(cortex_name, folder_location)
