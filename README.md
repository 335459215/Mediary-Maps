# StrmAssistant-Maps

StrmAssistant 的公开远程映射库；插件只从 GitHub raw 下载到本地缓存，校验成功后原子替换并热加载，不需要重启 Emby。

- `genre_map.json`：题材（Genre）中文映射；`map` 为应建合集的题材，`skip` 为画质、片商、发行、系列等非题材标签。
- `actor_map.json`：人工核验的“原始演员名 → 简体中文显示名”覆盖层。不会机翻。
- `actor_aliases.json`：无歧义别名 → `actor_map.json` 中的标准原名。当前为空；只有人工复核后才可加入，避免同名演员错误合并。
- `actor_sources.json`：候选社区来源的固定 revision、字段与许可证记录；用于离线导入审计，不会把其数据随本仓库再分发。

## 导入规则

1. `actor_map.json` 是最高优先级的人工真名层。
2. 候选源中的重名或不完整别名必须丢弃，不能直接发布。
3. 远程演员资料和主图由用户自建 MetaTube 后端按需提供；本仓库不镜像或分发第三方头像。
4. `AV_Data_Capture` 的 `mapping_actor.xml` 为 GPL-3.0-only 社区数据：只允许插件在运行时作为候选来源拉取/转换；若未来发布其内容的派生数据包，必须先做许可证审查并保留完整来源归属。
