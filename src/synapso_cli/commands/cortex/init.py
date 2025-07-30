from synapso_core.cortex_manager import CortexManager


def cmd_initialize_cortex(cortex_id: str, index_now: bool = True):
    cortex_manager = CortexManager()
    return cortex_manager.initialize_cortex(cortex_id, index_now)
