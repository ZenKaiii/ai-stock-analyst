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
