from __future__ import annotations

from abc import ABC
from collections.abc import Collection, Iterable

from pabutools.election.ballot.cardinalballot import AbstractCardinalBallot
from pabutools.election.ballot.interactionballot import InteractionBallot
from pabutools.utils import Numeric

from pabutools.election.ballot import (
    Ballot,
    FrozenBallot,
)
from pabutools.election.profile.profile import Profile, MultiProfile, AbstractProfile
from pabutools.election.instance import Instance, Project

class AbstractInteractionProfile(AbstractProfile, ABC, Iterable[AbstractCardinalBallot]):
    """
    Abstract class for interaction profiles. Stores the metadata and the methods specific to interaction profiles.

    Parameters
    ----------
        legal_min_length : int, optional
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_min_score : Numeric, optional
            The minimum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_max_score : Numeric, optional
            The maximum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.

    Attributes
    ----------
        legal_min_length : int
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
        legal_max_length : int
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
        legal_min_score : Numeric
            The minimum score a project can be assigned by a voter per the rules of the election.
        legal_max_score : Numeric
            The maximum score a project can be assigned by a voter per the rules of the election.
    """

    def __init__(
            self,
            legal_min_length: int | None = None,
            legal_max_length: int | None = None,
            legal_min_score: Numeric | None = None,
            legal_max_score: Numeric | None = None,
    ):
        AbstractProfile.__init__(self)
        ABC.__init__(self)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score

    def total_score(self, project: Project, bundle: Collection[Project]) -> Numeric:
        """
        Returns the total score of a project, that is, the sum of scores received from all voters.

        Parameters
        ----------
            project : :py:class:`~pabutools.election.instance.Project`
                The project.
            bundle : Collection
                The funded projects.

        Returns
        -------
            Numeric
                The total score assigned to the project.
        """
        score = 0
        for ballot in self:
            if project in ballot:
                project_group, group_util = ballot[project]
                chosen_in_group = project_group & set(bundle)
                project_marginal_utility = group_util[len(chosen_in_group)]
                score += project_marginal_utility

        return score


class InteractionProfile(Profile, AbstractInteractionProfile):
    """
    A profile of interaction ballots, that is, a list of interaction ballots per voters. See the class
    :py:class:`~pabutools.election.ballot.interactionballot.InteractionBallot` for more details on interaction ballots.
    This class inherits from the Python `list` class and can thus be used as one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.ballot.interactionballot.CardinalBallot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.interactionballot.CardinalBallot` that is used an
            initializer for the list. If activated, the types of the ballots are validated. In case an
            :py:class:`~pabutools.election.profile.profile.AbstractProfile` object is passed, the
            additional attributes are also copied (except if the corresponding keyword arguments have been given).
        instance : :py:class:`~pabutools.election.instance.Instance`, optional
            The instance related to the profile.
            Defaults to `Instance()`.
        ballot_validation : bool, optional
            Boolean indicating whether ballots should be validated before being added to the profile.
            Defaults to `True`.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`], optional
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
            Defaults to `CardinalBallot`.
        legal_min_length : int, optional
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_min_score : Numeric, optional
            The minimum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_max_score : Numeric, optional
            The maximum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance related to the profile.
        ballot_validation : bool
            Boolean indicating whether ballots should be validated before being added to the profile.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`]
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
        legal_min_length : int
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
        legal_max_length : int
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
        legal_min_score : Numeric
            The minimum score a project can be assigned by a voter per the rules of the election.
        legal_max_score : Numeric
            The maximum score a project can be assigned by a voter per the rules of the election.
    """

    def __init__(
            self,
            init: Iterable[InteractionBallot] = (),
            instance: Instance | None = None,
            ballot_validation: bool | None = None,
            ballot_type: type[Ballot] | None = None,
            legal_min_length: int | None = None,
            legal_max_length: int | None = None,
            legal_min_score: Numeric | None = None,
            legal_max_score: Numeric | None = None,
    ) -> None:
        if legal_min_length is None and isinstance(init, AbstractInteractionProfile):
            legal_min_length = init.legal_min_length
        if legal_max_length is None and isinstance(init, AbstractInteractionProfile):
            legal_max_length = init.legal_max_length
        if legal_min_score is None and isinstance(init, AbstractInteractionProfile):
            legal_min_score = init.legal_min_score
        if legal_max_score is None and isinstance(init, AbstractInteractionProfile):
            legal_max_score = init.legal_max_score
        AbstractInteractionProfile.__init__(
            self,
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
            legal_min_score=legal_min_score,
            legal_max_score=legal_max_score,
        )
        if ballot_validation is None:
            if isinstance(init, AbstractProfile):
                ballot_validation = init.ballot_validation
            else:
                ballot_validation = True

        if ballot_type is None:
            if isinstance(init, AbstractProfile):
                ballot_type = init.ballot_type
            else:
                ballot_type = InteractionBallot

        if instance is None and isinstance(init, AbstractInteractionProfile):
            instance = init.instance

        Profile.__init__(
            self,
            init=init,
            instance=instance,
            ballot_validation=ballot_validation,
            ballot_type=ballot_type,
        )

    def complete(self, projects: Collection[Project], default_score: Numeric) -> None:
        """
        Completes all the ballots such that for all ballots, if a project from `projects` has not been assigned a score,
        then it is assigned `default_score`.

        Parameters
        ----------
            projects : Iterable[:py:class:`~pabutools.election.instance.Project`]
                The set of all the projects to consider. This is typically the instance.
            default_score : Numeric
                The default score that will be assigned.
        """
        for ballot in self:
            ballot.complete(projects, default_score)

    def sort(self, *, key=None, reverse=None):
        raise NotImplementedError(
            "Cardinal profiles cannot be sorted as cardinal ballots do not support '<'"
        )

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, list) and not isinstance(result, cls):
                    result = cls(
                        result,
                        instance=self.instance,
                        ballot_validation=self.ballot_validation,
                        ballot_type=self.ballot_type,
                        legal_min_length=self.legal_min_length,
                        legal_max_length=self.legal_max_length,
                        legal_min_score=self.legal_min_score,
                        legal_max_score=self.legal_max_score,
                    )
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


InteractionProfile._wrap_methods(
    [
        "__add__",
        "__iadd__",
        "__imul__",
        "__mul__",
        "__reversed__",
        "__rmul__",
        "copy",
        "reverse",
        "__getitem__",
    ]
)