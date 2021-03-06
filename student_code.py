import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here
        # if it is a fact
        if isinstance(fact_or_rule, Fact):
            if fact_or_rule not in self.facts:
                return
            f = self._get_fact(fact_or_rule)
            if f.supported_by == []:

                for sf in f.supports_facts:
                    # handle sf's supported_by
                    for pair in sf.supported_by:
                        if pair[0] == f:
                            sf.supported_by.remove(pair)
                    # retract sf
                    self.kb_retract(sf)
                for sr in f.supports_rules:
                    # handle sr's supported_by
                    for pair in sr.supported_by:
                        if pair[0] == f:
                            sr.supported_by.remove(pair)
                    # retract sf
                    self.kb_retract(sr)
                # remove f in kb
                self.facts.remove(f)
        # if it is a rule
        else:
            # if it is an inferred rule
            if fact_or_rule not in self.rules:
                return
            r = self._get_rule(fact_or_rule)
            if r.asserted is False:
                if r.supported_by == []:
                    for sf in r.supports_facts:
                        # handle sf's supported_by
                        for pair in sf.supported_by:
                            if pair[1] == r:
                                sf.supported_by.remove(pair)
                        # retract sf
                        self.kb_retract(sf)
                    for sr in r.supports_rules:
                        # handle sr's supported_by
                        for pair in sr.supported_by:
                            if pair[1] == r:
                                sr.supported_by.remove(pair)
                        # retract sr
                        self.kb_retract(sr)
                # remove f in kb
                self.rules.remove(r)

class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        # infer a fact/ a rule
        # bind LHS[0] and fact
        bindings = match(fact.statement, rule.lhs[0])
        rule_lhs = []
        for i, l in enumerate(rule.lhs):
            if i > 0:
                rule_lhs.append(l)
        # instantiate a new statement
        if bindings:
            if len(rule_lhs) is 0:
                support_by = [[fact, rule]]
                # use the first binding , create a new fact
                new_f = Fact(instantiate(rule.rhs, bindings), support_by)
                kb.kb_add(new_f)
                ind = kb.facts.index(new_f)
                fact.supports_facts.append(kb.facts[ind])
                rule.supports_facts.append(kb.facts[ind])
            else:
                rule_lhs_statement = []
                support_by = [[fact, rule]]
                # use the first binding , create a new list of lhs
                for rl in rule_lhs:
                    rule_lhs_statement.append(instantiate(rl, bindings))
                # create a new rhs
                new_rule_rhs = instantiate(rule.rhs, bindings)
                # create a new rule using lhs and rhs
                new_r = Rule([rule_lhs_statement, new_rule_rhs], support_by)
                kb.kb_add(new_r)
                ind = kb.rules.index(new_r)
                fact.supports_rules.append(kb.rules[ind])
                rule.supports_rules.append(kb.rules[ind])

