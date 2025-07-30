from synapso_core.cortex_manager import CortexManager


def cmd_index_cortex(cortex_id: str):
    cortex_manager = CortexManager()
    return cortex_manager.index_cortex(cortex_id)
