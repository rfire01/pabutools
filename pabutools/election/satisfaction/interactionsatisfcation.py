"""
Additive satisfaction measures.
"""
from __future__ import annotations

from collections.abc import Callable, Collection

from pabutools.election import AbstractProfile
from pabutools.election.ballot.interactionballot import AbstractInteractionBallot
from pabutools.election.profile.interactionprofile import AbstractInteractionProfile
from pabutools.utils import Numeric

from pabutools.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pabutools.election.ballot import (
    AbstractBallot,
)
from pabutools.election.instance import (
    Instance,
    Project,
)


class InteractionSatisfaction(SatisfactionMeasure):
    """
    Class representing interaction satisfaction measures, that is, satisfaction functions for which the
    satisfaction of a project depend on the other chosen projects.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        func : Callable[[:py:class:`~pabutools.election.instance.Instance`, :py:class:`~pabutools.election.profile.profile.AbstractProfile`,  :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`, :py:class:`~pabutools.election.instance.Project`, dict[str, str]], Numeric]
            A function taking as input an instance, a profile, a ballot, a project and dictionary of precomputed values
            and returning the score of the project as a fraction.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractInteractionProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractInteractionBallot`
            The ballot.
        func : Callable[[:py:class:`~pabutools.election.instance.Instance`, :py:class:`~pabutools.election.profile.profile.AbstractProfile`,  :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`, :py:class:`~pabutools.election.instance.Project`, dict[str, str]], Numeric]
            A function taking as input an instance, a profile, a ballot, a project and dictionary of precomputed values
            and returning the score of the project as a fraction.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values. Initialised via the `preprocessing` method.
    """

    def __init__(
            self,
            instance: Instance,
            profile: AbstractInteractionProfile,
            ballot: AbstractInteractionBallot,
            project_func: Callable[
                [Instance, AbstractInteractionProfile, AbstractInteractionBallot, Project, Collection[Project]], Numeric
            ],
            bundle_func: Callable[
                [Instance, AbstractInteractionProfile, AbstractInteractionBallot, Collection[Project]], Numeric
            ]
    ) -> None:
        SatisfactionMeasure.__init__(self, instance, profile, ballot)
        self.project_func = project_func
        self.bundle_func = bundle_func

    def get_project_sat(self, project: Project, bundle: Collection[Project] = tuple()) -> Numeric:
        """
        Given a project, computes the corresponding satisfaction. Stores the score after computation to avoid
        re-computing it.

        Parameters
        ----------
            project : :py:class:`~pabutools.election.instance.Project`
                The instance.
            bundle : Collection
                The funded projects.

        Returns
        -------
            Numeric
                The satisfaction of the project.

        """
        score = self.project_func(
            self.instance,
            self.profile,
            self.ballot,
            project,
            bundle,
        )
        return score

    def sat(self, bundle: Collection[Project]) -> Numeric:
        score = self.bundle_func(
            self.instance,
            self.profile,
            self.ballot,
            bundle,
        )
        return score

    def sat_project(self, project: Project, bundle: Collection[Project] = tuple()) -> Numeric:
        return self.get_project_sat(project, bundle)


def project_interaction_cardinality(
        instance: Instance,
        profile: AbstractInteractionProfile,
        ballot: AbstractInteractionBallot,
        project: Project,
        bundle: Collection[Project],
) -> Numeric:
    """
    Computes the single project cardinality satisfaction for ballots. It is equal to the
    assigned marginal utility, which depends on how many projects were selected from the same group.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractInteractionProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractInteractionBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        bundle : Collection
            The funded projects.

    Returns
    -------
        int
            The cardinality satisfaction.
    """
    if project in ballot:
        project_group, group_util = ballot[project]
        chosen_in_group = project_group & set(bundle)
        project_marginal_utility = group_util[len(chosen_in_group)]

        return project_marginal_utility

    return 0


def outcome_interaction_cardinality(
        instance: Instance,
        profile: AbstractInteractionProfile,
        ballot: AbstractInteractionBallot,
        bundle: Collection[Project],
) -> Numeric:
    """
    Computes the total cardinality satisfaction for ballots. It is equal to the assigned marginal utility,
    which depends on how many projects were selected from the same group.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractInteractionProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractInteractionBallot`
            The ballot.
        bundle : Collection
            The funded projects.

    Returns
    -------
        int
            The cardinality satisfaction.
    """
    counts = {}
    group_to_util = {}
    for project in bundle:
        if project not in ballot:
            continue

        project_group, group_util = ballot[project]
        counts[project_group] = counts.get(project_group, 0) + 1
        group_to_util[project_group] = group_util

    sat = 0
    for project_group, group_count in counts.items():
        sat += sum(group_to_util[project_group][:group_count])

    return sat


class Cardinality_Sat_With_Interaction(InteractionSatisfaction):
    """
    The cardinality satisfaction for ballots. It is equal to the assigned marginal utility,
    which depends on how many projects were selected from the same group.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractInteractionProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractInteractionBallot`
            The ballot.
    """

    def __init__(
            self, instance: Instance, profile: AbstractInteractionProfile, ballot: AbstractInteractionBallot
    ):
        InteractionSatisfaction.__init__(
            self, instance, profile, ballot, project_interaction_cardinality, outcome_interaction_cardinality
        )


def project_additive_cardinality(
        instance: Instance,
        profile: AbstractInteractionProfile,
        ballot: AbstractInteractionBallot,
        project: Project,
        bundle: Collection[Project],
) -> Numeric:
    """
    Computes the single project cardinality satisfaction for ballots. It is equal to the assigned initial
    marginal utility, ignoring which other projects were selected.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractInteractionProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractInteractionBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        bundle : Collection
            The funded projects.

    Returns
    -------
        int
            The cardinality satisfaction.
    """
    if project in ballot:
        _, group_util = ballot[project]
        project_marginal_utility = group_util[0]

        return project_marginal_utility

    return 0


def outcome_additive_cardinality(
        instance: Instance,
        profile: AbstractInteractionProfile,
        ballot: AbstractInteractionBallot,
        bundle: Collection[Project],
) -> Numeric:
    """
    Computes the total cardinality satisfaction for ballots. It is equal to the assigned initial
    marginal utility, ignoring which other projects were selected.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractInteractionProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractInteractionBallot`
            The ballot.
        bundle : Collection
            The funded projects.

    Returns
    -------
        int
            The cardinality satisfaction.
    """
    return sum(project_additive_cardinality(instance, profile, ballot, p, bundle) for p in bundle)


class Cardinality_Sat_Ignoring_Interaction(InteractionSatisfaction):
    """
    The cardinality satisfaction for ballots. It is equal to the assigned initial marginal utility,
    ignoring which other projects were selected.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractInteractionProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractInteractionBallot`
            The ballot.
    """

    def __init__(
            self, instance: Instance, profile: AbstractInteractionProfile, ballot: AbstractInteractionBallot
    ):
        InteractionSatisfaction.__init__(
            self, instance, profile, ballot, project_additive_cardinality, outcome_additive_cardinality
        )