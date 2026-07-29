# Mediary-Maps

Mediary 的公开远程映射库；插件只从 GitHub raw 下载到本地缓存，校验成功后原子替换并热加载，不需要重启 Emby。

- `genre_map.json`：题材（Genre）中文映射；`map` 为应建合集的题材，`skip` 为画质、片商、发行、系列等非题材标签。
- `actor_map.json`：人工核验的“原始演员名 → 简体中文显示名”覆盖层。不会机翻。
- `actor_aliases.json`：去重后的无歧义别名 → 显示名。它是唯一的社区派生数据文件，内置固定来源 revision、许可证和生成器信息；运行时优先级低于 `actor_map.json`。
- `actor_image_map.json`：人工核验的“原始演员名 → 允许按需请求的 HTTPS 主图 URL”索引。只保存身份键与 URL，绝不镜像或提交第三方图片文件；当前没有通过来源/许可审核的条目，故为空。

## 来源、许可证与纠错

1. `actor_map.json` 与 `genre_map.json` 是人工核验层；只收录名称/题材映射，不收录演员简介、照片或第三方页面正文。
2. `actor_aliases.json` 由 `scripts/build_actor_aliases.py` 从 [`catcat0921/AV_Data_Capture`](https://github.com/catcat0921/AV_Data_Capture) 的固定 revision `19977d177ea86e979c2a03212f7dde583dfebd83` 生成；源文件为 GPL-3.0-only，本文件及其派生内容同样以 GPL-3.0-only 分发。生成器只保留唯一归属的 alias；同一 alias 指向多个显示名时直接丢弃。
3. 2026-07-28 已重新从该固定 revision 生成并以 SHA-256 验证：`mapping_actor.xml` 为 `7fc846574c5b33dbbe8376c1fa121062273c99fb86af9802e00589a1cefb5052`，生成的 `actor_aliases.json` 与仓库版本逐字节一致（15,075 条）。
4. 更正或删除：请在本仓库 Issue 提交原始 alias、正确显示名和可公开核验的来源。维护者会先验证歧义和许可证，再修正/移除；不以批量抓取成人站点页面作为数据源。
5. 演员简介和主图不进入 Maps 仓：由用户自建 MetaTube 后端在实际遇到演员、且该站点条款/robots 允许时按需获取。Mediary 不镜像、提交或再分发第三方头像。

## 导入边界

- GitHub 上近期维护但未声明许可证的映射仓，不导入或再分发其数据；可仅作为人工核验线索。
- 已检查的站点 robots：JavBus 禁止所有爬虫；JavDB 禁止搜索且标明 `Crawl-delay: 20`。因此不对它们进行自动搜索、批量页面抓取或图片下载。
- `map` 与 `skip` 必须互斥；运行时若意外冲突，以明确 `map` 为准。
