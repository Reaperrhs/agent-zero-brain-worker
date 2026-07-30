from helpers.extension import Extension

PLUGIN_NAME = "brain_worker"


def _is_enabled(agent) -> bool:
    from helpers import plugins
    enabled = plugins.get_enabled_plugins(agent)
    return PLUGIN_NAME in enabled


def _build_glm_model(agent):
    """Build a GLM 5.2 chat model for worker subordinates."""
    import models
    from helpers import plugins as plg

    cfg = plg.get_plugin_config(PLUGIN_NAME, agent=agent) or {}
    chat_cfg = cfg.get("worker_chat_model", {})
    if not chat_cfg.get("name"):
        return None

    mc = models.ModelConfig(
        type=models.ModelType.CHAT,
        provider=chat_cfg.get("provider", "zai_coding"),
        name=chat_cfg.get("name", "glm-5.2"),
        api_key=chat_cfg.get("api_key", ""),
        api_base=chat_cfg.get("api_base", "https://api.z.ai/api/coding/paas/v4"),
        ctx_length=int(chat_cfg.get("ctx_length", 1000000)),
        vision=bool(chat_cfg.get("vision", False)),
        limit_requests=int(chat_cfg.get("rl_requests", 0)),
        limit_input=int(chat_cfg.get("rl_input", 0)),
        limit_output=int(chat_cfg.get("rl_output", 0)),
        kwargs={},
    )
    return models.get_chat_model(mc.provider, mc.name, model_config=mc, **mc.build_kwargs())


class SwapToWorkerModel(Extension):
    def execute(self, data: dict = {}, **kwargs):
        if not self.agent:
            return
        # Only override for subordinates (agent number > 0)
        if self.agent.number == 0:
            return
        if not _is_enabled(self.agent):
            return
        worker_model = _build_glm_model(self.agent)
        if worker_model:
            data["result"] = worker_model
