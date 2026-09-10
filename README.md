
## 数据来源与再生成

- `actor_map.json` / `actor_aliases.json`: 人工验证条目优先，缺额由 [li-peifeng/Jav-Actors-Mapping](https://github.com/li-peifeng/Jav-Actors-Mapping) `actor-mapping.xml` 补齐（歧义别名丢弃）。
- `actor_avatars.json`: [li-peifeng/gfriends](https://github.com/li-peifeng/gfriends) `Filetree.json` 紧凑索引（名 → 图源相对路径，不重分发图片字节）。
- `actor_photoalbums.json`: [li-peifeng/Jalbum](https://github.com/li-peifeng/Jalbum) `Filetree.json` 紧凑索引（名 → folder + 文件列表）。

重新生成：`python3 scripts/build_from_upstream.py --repo .`（现有人工条目永不被上游覆盖）。
