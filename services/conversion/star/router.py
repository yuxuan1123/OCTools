"""
OCTools/services/conversion/star/router.py
───────────────────────────────────────────────
星型自动寻路（保底转换的「大脑」）—— 业务逻辑层

思想：
  1. 建图：节点 = 全部格式；边 = 直达转换边（registry）∪ 星型枢纽边（hubs）
  2. 寻路：BFS 求 (源 → 目标) 的最短路径 —— 自动为「所有格式」找路，
     不需要为每一对 (源, 目标) 手写一条桥接规则
  3. 兜底：直达边没有时，只要图中存在路径（含经枢纽中转）就能转换

例：html → docx
  直达边没有 (html, docx)，但图里有 html→md（直达）与 md→docx（直达），
  BFS 找到路径 [html, md, docx]。

"""

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set

from core import formats as FMT
from services.conversion.registry import Registry
from services.conversion.star.hubs import hub_star_edges


class StarRouter:
    """基于直达边 + 星型枢纽边的自动寻路器"""

    def __init__(self, registry: Registry):
        self._registry = registry
        self._graph: Dict[str, Set[str]] = self._build_graph()

    # ── 建图 ──

    def _build_graph(self) -> Dict[str, Set[str]]:
        graph: Dict[str, Set[str]] = defaultdict(set)
        # 1) 直达转换边（真实可执行的转换函数）
        #    排除「输出是文件夹」的边（文档→按页图片）与
        #    「非中转」边（音频→txt 语音识别），避免星型中转断链 / 导出跨类路径
        for (src, dst) in self._registry.edges():
            spec = self._registry.get(src, dst)
            if spec is not None and (spec.output_is_folder or not spec.transitive):
                continue
            graph[src].add(dst)
        # 2) 星型枢纽边：族内 成员 ⇄ 枢纽 —— 仅当该方向确实有直达转换时保留，
        #    保证「枢纽边 = 可执行」；族内已全互联时与直达边重合，起到兜底保证
        for (m, h) in hub_star_edges():
            if self._registry.has(m, h):
                graph[m].add(h)
            if self._registry.has(h, m):
                graph[h].add(m)
        return {k: v for k, v in graph.items()}

    # ── 查询 ──

    def find_path(self, src: str, dst: str) -> Optional[List[str]]:
        """BFS 最短路径；返回 [src, fmt2, ..., dst]，找不到返回 None"""
        src, dst = FMT.resolve(src), FMT.resolve(dst)
        if src == dst:
            return [src]
        if src not in self._graph or dst not in self._graph:
            return None
        prev: Dict[str, str] = {src: ""}
        queue = deque([src])
        while queue:
            cur = queue.popleft()
            if cur == dst:
                break
            for nxt in sorted(self._graph.get(cur, ())):
                if nxt not in prev:
                    prev[nxt] = cur
                    queue.append(nxt)
        if dst not in prev:
            return None
        # 回溯路径
        path = [dst]
        while path[-1] != src:
            path.append(prev[path[-1]])
        path.reverse()
        return path

    def is_reachable(self, src: str, dst: str) -> bool:
        return self.find_path(src, dst) is not None

    def reachable_from(self, src: str) -> Set[str]:
        """从 src 出发可到达的全部格式（含经星型枢纽中转）"""
        src = FMT.resolve(src)
        seen: Set[str] = set()
        queue = deque([src])
        while queue:
            cur = queue.popleft()
            for nxt in self._graph.get(cur, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        seen.discard(src)
        return seen

    def path_hint(self, src: str, dst: str) -> str:
        """人类可读的路径描述，如 'html → md → docx'"""
        path = self.find_path(src, dst)
        return " → ".join(path) if path else ""


# ── 默认单例（基于默认注册表）──
def _default_router() -> StarRouter:
    from services.conversion.registry import REGISTRY
    return StarRouter(REGISTRY)


router = _default_router()
