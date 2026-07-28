# StrmAssistant-Maps

Strm Assistant 插件的远程映射库（公开仓库，无需 token）。

- `genre_map.json`：AV 题材(Genre) 中文映射。`map`=题材→中文名；`skip`=非题材类（画质/片商/发行/系列/英文电影类型/演员误标），插件不建合集。
- `actor_map.json`：演员原名→中文真名映射。无中文官方译名的演员不在此列，插件改用库内已本地化的 Person 名兜底。

人工维护，非机翻。插件运行时从 raw.githubusercontent.com 拉取，24h 缓存。
