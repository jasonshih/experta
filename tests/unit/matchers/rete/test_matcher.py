import pytest

from experta import abstract


def test_retematcher_exists():
    try:
        from experta.matchers.rete import ReteMatcher
    except ImportError as exc:
        assert False, exc


def test_retematcher_is_matcher():
    from experta.matchers.rete import ReteMatcher

    assert issubclass(ReteMatcher, abstract.Matcher)


def test_retematcher_is_not_abstract():
    from experta.matchers.rete import ReteMatcher
    from experta.engine import KnowledgeEngine

    # MUST NOT RAISE
    ReteMatcher(KnowledgeEngine())


def test_retematcher_has_root_node():
    from experta.matchers.rete import ReteMatcher
    from experta.engine import KnowledgeEngine
    from experta.matchers.rete.nodes import BusNode

    matcher = ReteMatcher(KnowledgeEngine())
    assert hasattr(matcher, 'root_node')
    assert isinstance(matcher.root_node, BusNode)


def test_retematcher_changes_are_propagated(TestNode):
    from experta.engine import KnowledgeEngine
    from experta.fact import Fact
    from experta.matchers.rete import ReteMatcher
    from experta.matchers.rete.token import Token

    matcher = ReteMatcher(KnowledgeEngine())
    tn1 = TestNode()
    tn2 = TestNode()

    matcher.root_node.add_child(tn1, tn1.activate)
    matcher.root_node.add_child(tn2, tn2.activate)

    f1 = Fact(__factid__=1)
    f2 = Fact(__factid__=2)
    f3 = Fact(__factid__=3)
    f4 = Fact(__factid__=4)

    matcher.changes(adding=[f1, f2],
                    deleting=[f3, f4])

    assert Token.valid(f1) in tn1.added
    assert Token.valid(f1) in tn2.added
    assert Token.valid(f2) in tn1.added
    assert Token.valid(f2) in tn2.added
    assert Token.invalid(f3) in tn1.added
    assert Token.invalid(f3) in tn2.added
    assert Token.invalid(f4) in tn1.added
    assert Token.invalid(f4) in tn2.added


def test_retematcher_changes_return_activations_if_csn():
    from experta.engine import KnowledgeEngine
    from experta.fact import Fact
    from experta.rule import Rule
    from experta.activation import Activation
    from experta.matchers.rete.nodes import ConflictSetNode
    from experta.matchers.rete import ReteMatcher

    matcher = ReteMatcher(KnowledgeEngine())
    rule = Rule()
    csn = ConflictSetNode(rule)
    matcher.root_node.add_child(csn, csn.activate)

    added, removed = matcher.changes(adding=[Fact(__factid__=1),
                                             Fact(__factid__=2)])

    assert len(added) == 2
    assert all(isinstance(a, Activation) for a in added)
