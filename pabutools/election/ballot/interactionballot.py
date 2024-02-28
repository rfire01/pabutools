"""
Interaction ballots, i.e., ballots with score dependencies between projects.
"""
from __future__ import annotations

from typing import List, Tuple, FrozenSet

from abc import ABC
from collections.abc import Collection, Mapping

from pabutools.election.ballot.ballot import FrozenBallot, Ballot, AbstractBallot
from pabutools.election.instance import Project

from pabutools.utils import Numeric


class AbstractInteractionBallot(AbstractBallot, ABC, Mapping[Project, Tuple[frozenset, List[float]]]):
    """
    Abstract class for interaction ballots. Essentially used for typing purposes.
    """


class FrozenInteractionBallot(
    dict[Project, Tuple[frozenset, List[float]]], FrozenBallot, AbstractInteractionBallot
):
    """
    Frozen interaction ballot, a ballot in which the voter split projects to groups and assign
    scores depend on how many are chosen.
    Since there is no frozen dictionary implemented in Python, this class simply inherits from the Python class `dict`,
    overriding the `set_item` method to ensure that it is non-mutable (raising an exception if the method is used).

    Parameters
    ----------
        init: dict[:py:class:`~pabutools.election.instance.Project`], optional
            Dictionary of :py:class:`~pabutools.election.instance.Project` used to initialise the ballot. In case an
            :py:class:`~pabutools.election.ballot.ballot.AbstractBallot` object is passed, the
            additional attributes are also copied (except if the corresponding keyword arguments have been given).
            Defaults to `()`.
        name : str, optional
            The identifier of the ballot.
            Defaults to `""`.
        meta : dict, optional
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
            Defaults to `dict()`.

    Attributes
    ----------
        name : str
            The identifier of the ballot.
        meta : dict
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
    """

    def __init__(
            self,
            init: dict[Project, Tuple[frozenset, List[float]]] = (),
            name: str | None = None,
            meta: dict | None = None,
    ):
        dict.__init__(self, init)
        if name is None:
            if isinstance(init, AbstractBallot):
                name = init.name
            else:
                name = ""
        if meta is None:
            if isinstance(init, AbstractBallot):
                meta = init.meta
            else:
                meta = dict()
        FrozenBallot.__init__(self, name=name, meta=meta)
        AbstractInteractionBallot.__init__(self)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))


class InteractionBallot(dict[Project, Tuple[frozenset, List[float]]], Ballot, AbstractInteractionBallot):
    """
    An interaction ballot, that is, a ballot in which the voter split projects to groups and assign
    scores depend on how many are chosen. This class inherits from the Python class `dict`
    and can be used as one.

    Parameters
    ----------
        init: dict[frozenset], optional
            Dictionary of set used to initialise the ballot. In case an
            :py:class:`~pabutools.election.ballot.ballot.AbstractBallot` object is passed, the
            additional attributes are also copied (except if the corresponding keyword arguments have been given).
            Defaults to `()`.
        name : str, optional
            The identifier of the ballot.
            Defaults to `""`.
        meta : dict, optional
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
            Defaults to `dict()`.

    Attributes
    ----------
        name : str
            The identifier of the ballot.
        meta : dict
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
    """
    def __init__(
            self,
            init: dict[frozenset, List[float]] | None = None,
            name: str | None = None,
            meta: dict | None = None,
    ):
        if init is None:
            init = dict()

        else:
            self.validate_ballot(init)
            init = self.process_input(init)

        dict.__init__(self, init)
        if name is None:
            if isinstance(init, AbstractBallot):
                name = init.name
            else:
                name = ""
        if meta is None:
            if isinstance(init, AbstractBallot):
                meta = init.meta
            else:
                meta = dict
        Ballot.__init__(self, name=name, meta=meta)
        AbstractInteractionBallot.__init__(self)

    @staticmethod
    def validate_ballot(interactions):
        all_projects = set()
        for project_group, group_utils in interactions.items():
            assert len(project_group) == len(group_utils), f"Received group of size {len(project_group)}" \
                                                           f" but received utilities for {len(group_utils)} projects"
            assert len(all_projects.intersection(project_group)) == 0, f"The following projects appear in more then " \
                                                                       f"one group: {all_projects.intersection(project_group)}"
            all_projects |= project_group

    def validate_addition(self, project_group):
        for project in project_group:
            assert project not in self, f'Project {project} already appear in one of the groups'

    @staticmethod
    def process_input(interactions):
        output = {}
        for project_group, group_utils in interactions.items():
            for project in project_group:
                output[project] = (project_group, group_utils)
        return output

    def __setitem__(self, project_group: FrozenSet[Project], group_utils: tuple[Numeric]):
        self.validate_addition(project_group)
        for project in project_group:
            super().__setitem__(project, (project_group, group_utils))

    def complete(self, projects: Collection[Project], default_score: Numeric) -> None:
        """
        Completes the ballot by assigning the `default_score` to all projects from `projects` that have not been
        assigned a score yet.

        Parameters
        ----------
            projects : Iterable[:py:class:`~pabutools.election.instance.Project`]
                The set of all the projects to consider. This is typically the instance.
            default_score : Numeric
                The default score that will be assigned.
        """
        for project in projects:
            if project not in self:
                super().__setitem__(project, ({project}, (default_score,)))


    def frozen(self) -> FrozenInteractionBallot:
        """
        Returns the frozen interaction ballot (that is hashable) corresponding to the ballot.

        Returns
        -------
            FrozenInteractionBallot
                The frozen interaction ballot.
        """
        return FrozenInteractionBallot(self)

    # This allows dict method returning copies of a dict to work
    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(result, name=self.name, meta=self.meta)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


InteractionBallot._wrap_methods(["copy", "__ior__", "__or__", "__ror__"])
