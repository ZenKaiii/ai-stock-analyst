from ai_stock_analyst.notification.dingtalk import DingTalkNotifier


def test_dingtalk_downgrades_unstable_markdown():
    notifier = DingTalkNotifier()
    raw = "## 标题\n\n- **交易信号**: `HOLD`"
    out = notifier._format_markdown_for_dingtalk("测试标题", raw)  # noqa: SLF001
    assert "**" not in out
    assert "`" not in out
    assert "交易信号" in out


def test_dingtalk_avoids_duplicate_heading():
    notifier = DingTalkNotifier()
    raw = "## 已有标题\n\n内容"
    out = notifier._format_markdown_for_dingtalk("另一个标题", raw)  # noqa: SLF001
    assert out.startswith("## 已有标题")
    assert "## 另一个标题" not in out


def test_dingtalk_strips_stray_asterisk_markers():
    notifier = DingTalkNotifier()
    raw = "## 热门股票发现\n\n- **结论*: BUY\n- *推荐原因*: 证据一般\n- **交易信号**: `HOLD`"
    out = notifier._format_markdown_for_dingtalk("热门股票发现", raw)  # noqa: SLF001
    assert "*" not in out
    assert "`" not in out
    assert "结论: BUY" in out
    assert "推荐原因: 证据一般" in out
