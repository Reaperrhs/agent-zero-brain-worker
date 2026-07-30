from helpers.extension import Extension

PLUGIN_NAME = "brain_worker"


def _is_enabled(agent) -> bool:
    from helpers import plugins
    enabled = plugins.get_enabled_plugins(agent)
    return PLUGIN_NAME in enabled


def _build_utility_model(agent):
    """Build a utility model for worker subordinates."""
    import models
    from helpers import plugins as plg

    cfg = plg.get_plugin_config(PLUGIN_NAME, agent=agent) or {}
    util_cfg = cfg.get("worker_utility_model", {})
    if not util_cfg.get("name"):
        return None

    mc = models.ModelConfig(
        type=models.ModelType.CHAT,
        provider=util_cfg.get("provider", "other"),
        name=util_cfg.get("name", "free-stack-Utility"),
        api_key=util_cfg.get("api_key", ""),
        api_base=util_cfg.get("api_base", "https://omniroute.onekindpromo.com"),
        ctx_length=int(util_cfg.get("ctx_length", 128000)),
        vision=False,
        limit_requests=int(util_cfg.get("rl_requests", 0)),
        limit_input=int(util_cfg.get("rl_input", 0)),
        limit_output=int(util_cfg.get("rl_output", 0)),
        kwargs={},
    )
    return models.get_chat_model(mc.provider, mc.name, model_config=mc, **mc.build_kwargs())


class SwapWorkerUtility(Extension):
    def execute(self, data: dict = {}, **kwargs):
        if not self.agent:
            return
        if self.agent.number == 0:
            return
        if not _is_enabled(self.agent):
            return
        util_model = _build_utility_model(self.agent)
        if util_model:
            data["result"] = util_model
